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
        self._ostream.write(self.indentation() + text + '\n' if newline else'')
    
    
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
    
    
    def subs(self, text, **env):
        return Template(text).substitute(self.env, **env)



class CodeEmitter(TemplatedEmitter):
    defaultenv = Environment(
        nstl_depth = 'NSTL_DEPTH',
        nstl_unique = 'NSTL_UNIQUE',
        nstl_depth_incr = '#include <params/depth/incr.h>',
        nstl_depth_decr = '#include <params/depth/decr.h>',
        nstl_unique_incr = '#include <params/unique/incr.h>',
        maxdepth = 2,
        maxunique = 2,
    )
    
    
    def __init__(self, env=defaultenv, *args, **kwargs):
        super().__init__(*args, env=env, **kwargs)
    
    
    def emit(self, output, newline=True, **env):
        if isinstance(output, str):
            for line in filter(None, map(str.lstrip, output.splitlines())):
                super().emit(line, newline, **env)
        
        elif isiterable(output):
            for elt in output:
                self.emit(elt, newline, **env)
        
        elif iscallable(input):
            rv = output(**env)
            if rv: self.emit(rv, newline, **env)
        
        else:
            raise TypeError(
                "an object of {} type can not be emitted".format(type(output)))
    
    
    def emit_template_header(self, template_name, **env):
        self.emit("${nstl_unique_incr}", **env)
        self._emit_for_all_depths(
        "#define ${name}_${depth}_H 1",
        name=template_name, **env)
    
    
    def emit_params_initialization(self, param_decls, **env):
        if not param_decls:
            return
        
        def emit_them(**env):
            rest = [ ]
            defaults = lambda p: p.default is not None or rest.append(p)
            for decl in filter(defaults, param_decls):
                self._emit_param_default(decl, **env)
            
            for decl in rest:
                self.emit("""
                #if ! defined (${param}_${unique})
                ${indent}#error "missing argument to template parameter $param"
                #endif
                """, param=decl.name.value, **env)
        
        self._emit_for_all_uniques(emit_them, **env)
    
    
    def _emit_param_default(self, param_decl, **env):
        """Emit the definition of a parameter with a default argument.
        """
        param_id = param_decl.name
        macrodef = self._defmacro(param_id.value, param_id.params,
                                                    param_decl.default.value)
        self.emit("""
        #if ! defined (${name}_${unique})
        ${indent}""" + macrodef + """
        #endif
        """, name=param_id.value, **env)
    
    
    def emit_params_cleanup(self, param_decls, **env):
        """Emit the cleaning of parameters after a template.
        """
        if not param_decls:
            return
        
        undefs = [self._undefmacro(decl.name.value) for decl in param_decls]
        self._emit_for_all_uniques(undefs, **env)
    
    
    def emit_nest(self, nest_stmnt, **env):
        """Emit the nesting of one or many templates.
        """
        self._emit_arguments(nest_stmnt.args)
        
        for ref in nest_stmnt.refs:
            self.emit("""
            ${nstl_depth_incr}
            #include <${path}>
            ${nstl_depth_decr}
            """, path=ref.resolved.path, **env)
    
    
    def emit_import(self, import_stmnt, **env):
        """Emit the importation of one or many templates.
        """
        self._emit_arguments(import_stmnt.args)
        
        for ref in import_stmnt.refs:
            self.emit("""
            #if CONCAT(${name}, _, ${nstl_depth}, _H) != 1
            ${indent}#include <${path}>
            #endif
            """, path=ref.resolved.path, name=ref.resolved.name.value, **env)
    
    
    def emit_depth_modifier(self, incr=True, **env):
        pick = lambda incr_, decr_: incr_ if incr else decr_
        env.update(dict(
            modifier_op = pick("+", "-"),
            bound = pick("${maxdepth}", "${mindepth}"),
            err_msg = pick("maximum", "minimum") + " template depth reached.",
        ))
        
        self.emit("""
        #if ${depth} == ${bound}
            ${indent}#error "${err_msg}"
        #endif
        """, **env)
        
        self._emit_for_all_depths("""
        #if ${nstl_depth} == ${depth}
            ${indent}#define ${nstl_depth} ${depth} ${modifer_op} 1
        #endif
        """, **env)
    
    
    def _emit_arguments(self, args, **env):
        """Instantiate arguments before a nest or an import.
        """
        args = [self._defmacro(arg.name.value, arg.name.params,
                                            arg.value.value) for arg in args]
        if args:
            self._emit_for_all_uniques(args, **env)
    
    
    def _defmacro(self, name, params, body):
        """Generate and return the definition of a macro.
        """
        params = "(" + ", ".join(params) + ")" if params is not None else ''
        return "#define {}_$unique{} {}".format(name, params, body)
    
    
    def _undefmacro(self, macro_name):
        """Generate and return the undefinition of a macro.
        """
        return "#undef {}_$unique".format(macro_name)
    
    
    def _emit_for_all_uniques(self, output, **env):
        # TODO Implement binary search
        for unique in range(self.env.maxunique):
            self.emit("#if ${nstl_unique} == ${unique}", unique=unique, **env)
            self.emit_indented(output, unique=unique, **env)
            self.emit("#endif", **env)
    
    
    def _emit_for_all_depths(self, output, **env):
        # TODO Implement binary search
        for depth in range(self.env.maxdepth):
            self.emit("#if ${nstl_depth} == ${depth}", depth=depth, **env)
            self.emit_indented(output, depth=depth, **env)
            self.emit("#endif", **env)



class Generator(ast.NodeVisitor):
    def __init__(self):
        self._emitter = CodeEmitter()
    
    
    def __getattribute__(self, attr):
        # Simple call forwarding to simplify writing this class
        get = super().__getattribute__
        try:
            return get(attr)
        except AttributeError:
            if attr.startswith("__"):
                raise
            return getattr(get("_emitter"), attr)
    
    
    def visit_Namespace(self, node, overwrite=False):
        previous = os.getcwd()
        if not os.path.exists(node.name.value):
            os.mkdir(node.name.value)
        os.chdir(node.name.value)
        self.generic_visit(node, overwrite)
        os.chdir(previous)
    
    
    def visit_Template(self, node, overwrite=False):
        filename = node.name.value + ".h"
        if not overwrite and os.path.exists(filename):
            raise IOError("can't overwrite the contents of " + filename)
        outfile = open(filename, 'w')
        self.setstream(outfile)
        
        self.emit_template_header(node.name.value)
        self.emit_params_initialization(node.params)
        
        for stmnt in node.body.stmnts:
            if isinstance(stmnt, ast.RawExpression):
                self.emit_raw(stmnt.value)
            else:
                self.visit(stmnt, overwrite)
        
        self.emit_params_cleanup(node.params)
    
    
    def visit_ImportStatement(self, node, *args, **kwargs):
        self.emit_import(node)
    
    
    def visit_NestStatement(self, node, *args, **kwargs):
        self.emit_nest(node)



if __name__ == "__main__":
    pass

