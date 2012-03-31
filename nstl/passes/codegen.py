from .. import ast

from string import Template
import sys
import os



def iscallable(obj):
    return hasattr(obj, "__call__")



class Environment(dict):
    """A class to facilitate instantiating string templates.
    """
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        return self
    
    def __getattribute__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return super().__getattribute__(attr)
    
    
    def __setattr__(self, attr, value):
        self[attr] = value



class StructuredEmitter(object):
    """A class to handle emitting output to a stream in a structured way.
    """
    def __init__(self, ostream=sys.stdout, indent=' '*4):
        self._ostream = ostream
        self._knownstreams = { }
        self._indent_level = 0
        self._indent_str = indent
    
    
    def setstream(self, ostream, reset=True):
        """Remembers the current stream and its associated state.
        If reset is True and the stream was not previously used with this
        emitter, the indentation level starts over at 0. In all cases, if
        the stream was previously used with this emitter, state in which the
        stream was left is restored. The resetindent() method can be called
        in order to manually reset the state.
        """
        self._knownstreams[self._ostream] = self._indent_level
        if ostream in self._knownstreams:
            self._indent_level = self._knownstreams[ostream]
        elif reset:
            self.resetindent()
        self._ostream = ostream
    
    
    def emit(self, text, newline=True):
        indentation = self.indentation()
        lines = text.splitlines()
        if newline:
            buf = "".join(indentation + line + "\n" for line in lines)
        else:
            buf = "".join(indentation + line for line in lines)
        self._ostream.write(buf)
    
    
    def emit_indented(self, text, newline=True):
        self.indent()
        self.emit(text, newline)
        self.dedent()
    
    
    def indentation(self):
        return self._indent_level * self.indent_str()
    
    
    def resetindent(self):
        self._indent_level = 0
    
    
    def indent_str(self):
        return self._indent_str
    
    
    def indent(self):
        """Add an indent level to the emitted code.
        """
        self._indent_level += 1
    
    
    def dedent(self):
        """Remove an indent level to the emitted code.
        """
        self._indent_level -= 1



class TemplatedEmitter(StructuredEmitter):
    """A class to emit templated output.
    """
    def __init__(self, env=Environment(), *args, **kwargs):
        assert isinstance(env, Environment)
        
        super().__init__(*args, **kwargs)
        self.env = env
        self.env.indent = self.indent_str()
    
    
    def emit(self, text, newline=True, **env):
        text = self.subs(text, **env)
        return self.emit_raw(text, newline)
    
    
    def emit_raw(self, text, newline=True):
        return super().emit(text, newline)
    
    
    def emit_indented(self, text, newline=True, **env):
        self.indent()
        self.emit(text, newline, **env)
        self.dedent()
    
    
    def setenv(self, env):
        self.env = env
    
    
    def subs(self, text, **env):
        return Template(text).substitute(self.env, **env)



class _AstPreparator(ast.NodeTransformer):
    def visit_Template(self, template):
        # Template :
        #  [name            -> string
        #   path            -> string
        #   content_file    -> string  (path to the non-top level include file)
        #   package_file    -> string  (path to the top level include file)
        #   body_file       -> string  (path to the body of the template)
        #   body**          -> Import|Nest|(RawExpression   -> string)
        #   params**        -> ParameterDeclaration]
        @ast.EzNode(children=('params', 'body'))
        class Template(object):
            pass
        
        name = template.name.value
        return Template(name=name,
                        path=str(template.path),
                        content_file=name + ".contents",
                        body_file=name + ".body",
                        package_file=name + ".h",
                        body=self.visit(template.body.stmnts),
                        params=self.visit(template.params))
    
    
    def visit_ParameterDeclaration(self, decl):
        # ParameterDeclaration :
        #   [name       -> string
        #    params     -> list<string> or None
        #    default    -> string]
        @ast.EzNode(attrs=('params', 'name', 'default'))
        class ParameterDeclaration(object):
            pass
        
        return ParameterDeclaration(name=decl.name.value,
                                    params=decl.name.params,
                                default=decl.default and decl.default.value)
    
    
    def visit_Namespace(self, namespace):
        # Namespace :
        #   [name       -> string
        #    path       -> string
        #    decls**    -> Template|Namespace]
        @ast.EzNode(attrs=('name', 'path'))
        class Namespace(object):
            pass
        
        return Namespace(name=namespace.name.value,
                            path=str(namespace.path),
                            decls=self.visit(namespace.decls))
    
    
    def visit_ArgumentExpression(self, expr):
        # ArgumentExpression :
        #   [name   -> string
        #    params -> list<string> or None
        #    value  -> string]
        @ast.EzNode(attrs=('name', 'params', 'values'))
        class ArgumentExpression(object):
            pass
        
        return ArgumentExpression(name=expr.name.value,
                                    params=expr.name.params,
                                    value=expr.value.value)
    
    
    def visit_ImportStatement(self, impt):
        # ImportStatement :
        #   [args**         -> ArgumentExpression
        #    templates**    -> Template]
        @ast.EzNode(children=('args', 'templates'))
        class ImportStatement(object):
            pass
        
        return ImportStatement(args=self.visit(impt.args),
        templates=ast.Nodelist(self.visit(ref.resolved) for ref in impt.refs))
    
    
    def visit_NestStatement(self, nest):
        # NestStatement :
        #   [args**     -> ArgumentExpression
        #    template*  -> Template]
        @ast.EzNode(children=('args', 'template'))
        class NestStatement(object):
            pass
        
        return NestStatement(args=self.visit(nest.args),
                             template=self.visit(nest.ref.resolved))



NstlDefaultEnv = Environment(
        get_depth = 'NSTL_DEPTH',
        get_package = 'NSTL_PACKAGE',
        depth_incr = '#include <params/depth/incr.h>',
        depth_decr = '#include <params/depth/decr.h>',
        package_incr = '#include <params/package/incr.h>',
        max_depth = 5,
        max_package = 5,
    )

#   List of placeholders used in the templates below.
# max_depth           The maximum depth.
# max_package         The maximum number of packages.
# depth_incr          A procedure to increment the depth.
# depth_decr          A procedure to decrement the depth.
# get_package         The name of a macro that must expand to the current
#                       package number when preprocessed.
# get_depth           The name of a macro that must expand to the current
#                       depth when preprocessed.

fmt_arg_list = lambda a: "(" + ", ".join(a) + ")" if a is not None else ""

class Generator(ast.NodeVisitor, TemplatedEmitter):
    def __init__(self, overwrite=False, env=NstlDefaultEnv, *args, **kwargs):
        super().__init__(*args, env=env, **kwargs)
        self.overwrite = overwrite
    
    
    def emit(self, output, newline=True, **env):
        """This method provides an optimization to reduce the total number
        of lines by removing empty lines.
        """
        lines = map(str.lstrip, output.splitlines())
        compressed = "\n".join(filter(None, lines))
        super().emit(compressed, newline, **env)
    
    
    def setstream(self, filename):
        if not self.overwrite and os.path.exists(filename):
            raise IOError("can't overwrite the contents of " + filename)
        super().setstream(open(filename, 'w'))
    
    
    def visit_Program(self, root):
        root = _AstPreparator().visit(root)
        self.generic_visit(root)
    
    
    def visit_Namespace(self, namespace):
        previous = os.getcwd()
        if not os.path.exists(namespace.name):
            os.mkdir(namespace.name)
        os.chdir(namespace.name)
        for decl in namespace.decls:
            self.visit(decl)
        os.chdir(previous)
    
    
    def visit_Template(self, template):
        self.setstream(template.package_file)
        self._emit_packagefile(template)
        
        self.setstream(template.content_file)
        self._emit_contentfile(template)
        
        self.setstream(template.body_file)
        for stmnt in template.body:
            if isinstance(stmnt, ast.RawExpression):
                self.emit_raw(stmnt.value)
            else:
                 self.visit(stmnt)
    
    
    def _emit_packagefile(self, template):
        """Generate a package file from the information contained in the given
        environment. The following information must be provided by the environment:
        
        get_package
        max_package
        max_depth
        """
        oldenv = self.env
        self.env = self.env.copy()
        
        self._emit_inner_params(template)
        
        for package in range(self.env['max_package']):
            self.env['package'] = package
            self.env['depth'] = 0

            self.emit("""
            #if ${get_package} == ${package}
            """)
            self.indent()
            
            # Argument reception from the clients
            #   ex : #define ValueType_0_0 ValueType
            for param in template.params:
                self.emit("""
                #define ${name}_${package}_${depth}${params} ${name}
                """, name=param.name, params=fmt_arg_list(param.params))
            
            
            self.emit("""
            #include "${file}"
            """, file=template.content_file)
            
            
            # Argument cleanup
            #   ex : #undef ValueType_0_0
            #        #undef ValueType_
            #        #undef ValueType
            for param in template.params:
                self.emit("""
                #undef ${name}_${package}_${depth}
                #undef ${name}_
                #undef ${name}
                """, name=param.name)
            
            
            self.dedent()
            self.emit("""
            #endif
            """)
        
        self.setenv(oldenv)
    
    
    def _emit_inner_params(self, template):
        """Generate the definition of inner parameters of a template.
        For example, a template with parameter ValueType will have an inner
        parameter called ValueType_.
        
        The following information must be provided by the environment:
        
        get_package
        get_depth
        """
        for param in template.params:
            self.emit("""
            #define ${name}_ CONCAT(${name}_, ${get_package}, _, ${get_depth})
            """, name=param.name)
    
    
    def _emit_contentfile(self, template):
        """Generate a content file from the information contained in the given
        environment. The following information must be provided by the environment:
        
        get_package
        get_depth
        max_depth
        max_package
        """
        oldenv = self.env
        self.env = self.env.copy()
        
        for package in range(self.env['max_package']):
            self.env['package'] = package
            
            self.emit("""
            #if ${get_package} == ${package}
            """)
            self.indent()
            
            
            for depth in range(self.env['max_depth']):
                self.env['depth'] = depth
                self.emit("""
                #if ${get_depth} == ${depth}
                """)
                self.indent()
                
                # Signalize that this template was instantiated
                self.emit("""
                #define ${name}_${package}_${depth}_H 1
                """, name=template.name)
                
                
                # Argument reception
                for param in template.params:
                    mangled_name = "_".join(map(str, [param.name, package, depth]))
                    
                    # Make sure all arguments without default were passed
                    if param.default is None:
                        self.emit("""
                        #if ! defined(${name})
                        ${indent}#error "missing argument to template parameter ${name}"
                        #endif
                        """, name=mangled_name)
                    
                    # Or use default argument
                    else:
                        self.emit("""
                        #if ! defined(${name})
                        ${indent}#define ${name}${params} ${default}
                        #endif
                        """, name=mangled_name, params=fmt_arg_list(param.params),
                                                            default=param.default)
                
                
                # This is only included as a separate file in order to save lines.
                self.emit("""
                #include "${file}"
                """, file=template.body_file)
                
                
                # Argument cleanup
                for param in template.params:
                    mangled_name = "_".join(map(str, [param.name, package, depth]))
                    
                    self.emit("""
                    #undef ${name}
                    """, name=mangled_name)
                
                
                self.dedent()
                self.emit("""
                #endif
                """)
            
            self.dedent()
            self.emit("""
            #endif
            """)

        self.env = oldenv
    
    
    def visit_ImportStatement(self, impt):
        """Generate the importation of a list of templates.
        The following information must be provided by the environment :
        
        get_depth
        get_package
        """
        oldenv = self.env
        self.env = self.env.copy()
        
        for template in impt.templates:
            self.emit("""
            #if CONCAT(${name}_, ${get_package}, _, ${get_depth}, _H) != 1
            ${indent}#include "${file}"
            #endif
            """, name=template.name, file=template.content_file)
        
        self.env = oldenv
    
    
    def visit_NestStatement(self, nest):
        """Generate the nesting of a template.
        The following information must be provided by the environment :
        
        get_depth
        get_package
        depth_incr
        depth_decr
        """
        oldenv = self.env
        self.env = self.env.copy()
        
        for package in range(self.env['max_package']):
            self.env['package'] = package
            
            self.emit("""
            #if ${get_package} == ${package}
            """)
            self.indent()
            
            
            for depth in range(self.env['max_depth']):
                self.env['depth'] = depth
                
                self.emit("""
                #if ${get_depth} == ${depth}
                """)
                self.indent()
                
                # Undefine the inner parameters
                for param in nest.template.params:
                    self.emit("""
                    #undef ${name}_
                    """, name=param.name)
                
                for arg in nest.args:
                    params = fmt_arg_list(arg.params)
                    self.emit("""
                    #define ${name}_${package}_${depth}${params} ${value}
                    """, name=arg.name, params=params, value=arg.value)
                
                # Redefine the inner parameters
                self._emit_inner_params(nest.template)


                self.dedent()
                self.emit("""
                #endif
                """)
            
            self.dedent()
            self.emit("""
            #endif
            """)
        
        
        self.emit("""
        ${depth_incr}
        #include "${file}"
        ${depth_decr}
        """, file=nest.template.content_file)

        self.env = oldenv



if __name__ == "__main__":
    pass
