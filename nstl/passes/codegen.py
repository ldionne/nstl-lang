from .. import ast

from string import Template
import sys
import os



def isiterable(obj):
    return hasattr(obj, "__iter__")



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



fmt_arg_list = lambda a: "(" + ", ".join(a) + ")" if a is not None else ""

def emit_packagefile(emitter, env):
    """Generate a package file from the information contained in the given
    environment. The following information is required in the environment :
    
    param_macro_names   A list of the names of the template's parameters.
    param_macro_params  A list of the parameters of the template's parameters,
                            or None for a macro without parentheses.
    get_package         The name of a macro that must expand to the current
                            package number when preprocessed.
    content_file        The path to the file containing the contents of the
                            template.
    max_package         The maximum number of packages.
    max_depth           The maximum depth.
    """
    oldenv = env
    env = env.copy()
    emitter.setenv(env)
    
    macro_names = env['param_macro_names']
    macro_params = [fmt_arg_list(macro_params)
                                for macro_params in env['param_macro_params']]
    
    for package in range(env['max_package']):
        env['package'] = package
        env['depth'] = 0
        
        emitter.emit("""
        #if ${get_package} == ${package}
        """)
        emitter.indent()
        
        # Argument reception from the clients
        #   ex : #define ValueType_0_0 ValueType
        for name, params in zip(macro_names, macro_params):
            emitter.emit("""
            #define ${name}_${package}_${depth}${params} ${name}
            """, name=name, params=params)
        
        
        emitter.emit("""
        #include "${content_file}"
        """)
        
        
        # Argument cleanup
        #   ex : #undef ValueType_0_0
        #        #undef ValueType
        for name in macro_names:
            emitter.emit("""
            #undef ${name}_${package}_${depth}
            #undef ${name}
            """, name=name)
        
        
        emitter.dedent()
        emitter.emit("""
        #endif
        """)
    
    emitter.setenv(oldenv)



def emit_contentfile(emitter, env):
    """Generate a content file from the information contained in the given
    environment. The following information is required in the environment :
    
    param_macro_names   A list of the names of the template's parameters.
    param_macro_params  A list of the parameters of the template's parameters,
                            or None for a macro without parentheses.
    param_defaults      A list of the default definition of the template's
                            parameters. In case there is no default, use None.
    get_package         The name of a macro that must expand to the current
                            package number when preprocessed.
    get_depth           The name of a macro that must expand to the current
                            depth when preprocessed.
    template_name       The name of the template.
    body_file           The path to the file containing the body of the
                            template.
    max_depth           The maximum depth.
    max_package         The maxmum number of packages.
    """
    oldenv = env
    env = env.copy()
    emitter.setenv(env)
    
    macro_names = env['param_macro_names']
    macro_params = [fmt_arg_list(macro_params)
                                for macro_params in env['param_macro_params']]
    defaults = env['param_defaults']
    
    for package in range(env['max_package']):
        env['package'] = package
    
        emitter.emit("""
        #if ${get_package} == ${package}
        """)
        emitter.indent()
    
    
        for depth in range(env['max_depth']):
            env['depth'] = depth
            emitter.emit("""
            #if ${get_depth} == ${depth}
            """)
            emitter.indent()
        
            # Signalize that this template was instantiated
            emitter.emit("""
            #define ${template_name}_${package}_${depth}_H 1
            """)
        
        
            # Argument reception
            for name, params, default in zip(macro_names, macro_params, defaults):
                mangled_name = "_".join(map(str, [name, package, depth]))
            
                # Make sure all arguments without default were passed
                if default is None:
                    emitter.emit("""
                    #if ! defined(${name})
                    ${indent}#error "missing argument to template parameter ${name}"
                    #endif
                    """, name=mangled_name)
            
                # Or use default argument
                else:
                    emitter.emit("""
                    #if ! defined(${name})
                    ${indent}#define ${name}${params} ${default}
                    #endif
                    """, name=mangled_name, params=params, default=default)
            
            
            # This is only included as a separate file in order to save lines.
            emitter.emit("""
            #include "${body_file}"
            """)
            
            
            
            # Argument cleanup
            for name in macro_names:
                mangled_name = "_".join(map(str, [name, package, depth]))
            
                emitter.emit("""
                #undef ${name}
                """, name=mangled_name)
        
        
        
            emitter.dedent()
            emitter.emit("""
            #endif
            """)
    
    
        emitter.dedent()
        emitter.emit("""
        #endif
        """)
    
    emitter.setenv(oldenv)



def emit_import(emitter, env):
    """Generate the importation of a list of templates.
    The following information is required inside the environment :
    
    get_depth           The maximum depth.
    get_package         The maximum number of packages.
    content_files       A list of the path to each template's content file.
    template_names      A list of the names of the templates.
    ~arg_macro_names     A list of the names of the arguments.
    ~arg_macro_params    A list of the parameters of the arguments, or None for
                            a macro without parentheses.
    ~arg_values          A list of the value of each argument.
    """
    oldenv = env
    env = env.copy()
    emitter.setenv(env)
    
    for name, file in zip(env['template_names'], env['content_files']):
        emitter.emit("""
        #if CONCAT(${template_name}_, ${get_package}, _, ${get_depth}, _H) != 1
        ${indent}#include "${content_file}"
        #endif
        """, template_name=name, content_file=file)
    
    emitter.setenv(oldenv)


def emit_nest(emitter, env):
    """Generate the nesting of a template.
    
    get_depth           The maximum depth.
    get_package         The maximum number of packages.
    content_file        The path to the template's content file.
    template_name       The name of the template.
    arg_macro_names     A list of the names of the arguments.
    arg_macro_params    A list of the parameters of the arguments, or None for
                            a macro without parentheses.
    arg_values          A list of the value of each argument.
    depth_incr          A procedure to increment the depth.
    depth_decr          A procedure to decrement the depth.
    """
    oldenv = env
    env = env.copy()
    emitter.setenv(env)
    
    for package in range(env['max_package']):
        env['package'] = package
        
        emitter.emit("""
        #if ${get_package} == ${package}
        """)
        emitter.indent()
        
        
        for depth in range(env['max_depth']):
            env['depth'] = depth
            
            emitter.emit("""
            #if ${get_depth} == ${depth}
            """)
            emitter.indent()
            
            
            for name, params, value in zip(env['arg_macro_names'],
                                    env['arg_macro_params'], env['arg_values']):
                params = fmt_arg_list(params)
                emitter.emit("""
                #define ${name}_${package}_${depth}${params} ${value}
                """, name=name, params=params, value=value)
            
            
            emitter.dedent()
            emitter.emit("""
            #endif
            """)
        
        
        emitter.dedent()
        emitter.emit("""
        #endif
        """)
    
    
    emitter.emit("""
    ${depth_incr}
    #include "${content_file}"
    ${depth_decr}
    """)
    
    
    emitter.setenv(oldenv)



class _AstPreparator(ast.NodeVisitor):
    def visit_Template(self, t):
        # Template :
        #   .name   -> string
        #   .path   -> string
        #   .content_file   -> string
        #   .package_file   -> string
        #   .body_file      -> string
        #   .body   -> list<statement>
        #   .params**:
        #       .name   -> string
        #       .params -> list<string>
        #       .default-> string
        t.name = t.name.value
        t.path = str(t.path)
        t.content_file = t.name + ".contents"
        t.body_file = t.name + ".body"
        t.package_file = t.name + ".h"
        t.body = t.body.stmnts
        
        for param in t.params:
            param.params = param.name.params
            param.name = param.name.value
            param.default = param.default and param.default.value
        
        for stmnt in t.body:
            self.visit(stmnt)
    
    
    def visit_Namespace(self, n):
        # Namespace :
        #   .name   -> string
        #   .decls  -- list<declaration>
        #   .path   -> string
        n.name = n.name.value
        n.path = str(n.path)
        for decl in n.decls:
            self.visit(decl)
    
    
    def _transform_args(args):
        #   .args**:
        #       .name   -> string
        #       .params -> list<string>
        #       .value  -> string
        for arg in args:
            arg.params = arg.name.params
            arg.name = arg.name.value
            arg.value = arg.value.value
    
    
    def visit_ImportStatement(self, i):
        # ImportStatement :
        #   .templates  -> list<Template>
        _AstPreparator._transform_args(i.args)
        i.templates = [ref.resolved for ref in i.refs]
    
    
    def visit_NestStatement(self, n):
        # NestStatement :
        #   .template   -> Template
        _AstPreparator._transform_args(n.args)
        n.template = n.ref.resolved



NstlDefaultEnv = Environment(
        get_depth = 'NSTL_DEPTH',
        get_package = 'NSTL_PACKAGE',
        depth_incr = '#include <params/depth/incr.h>',
        depth_decr = '#include <params/depth/decr.h>',
        package_incr = '#include <params/package/incr.h>',
        max_depth = 2,
        max_package = 5,
    )



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
        _AstPreparator().visit(root)
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
        env = self.env.copy()
        env.update(dict(
            content_file = template.content_file,
            body_file = template.body_file,
            template_name = template.name,
            param_macro_names = [param.name for param in template.params],
            param_macro_params = [param.params for param in template.params],
            param_defaults = [param.default for param in template.params],
        ))
        
        self.setstream(template.package_file)
        emit_packagefile(self, env)
        
        self.setstream(template.content_file)
        emit_contentfile(self, env)
        
        self.setstream(template.body_file)
        for stmnt in template.body:
            if isinstance(stmnt, ast.RawExpression):
                self.emit_raw(stmnt.value)
            else:
                self.visit(stmnt)
    
    
    def visit_ImportStatement(self, impt):
        env = self.env.copy()
        env.update(dict(
            content_files = [t.content_file for t in impt.templates],
            template_names = [t.name for t in impt.templates],
        ))
        emit_import(self, env)
    
    
    def visit_NestStatement(self, nest):
        env = self.env.copy()
        env.update(dict(
            content_file = nest.template.content_file,
            template_name = nest.template.name,
            arg_macro_names = [arg.name for arg in nest.args],
            arg_macro_params = [arg.params for arg in nest.args],
            arg_values = [arg.value for arg in nest.args],
        ))
        emit_nest(self, env)



if __name__ == "__main__":
    pass

