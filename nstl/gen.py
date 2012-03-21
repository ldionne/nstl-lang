
from string import Template

from . import ast
from string import Template
import sys


"""
Note : Binary search inside directives should be implemented soon to improve
        performance.
"""

class Environment(dict):
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        return self
    
    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            try:
                return self[attr]
            except KeyError:
                raise AttributeError
    
    def __setattr__(self, attr, value):
        if not hasattr(self, attr) and attr in self:
            self[attr] = value
        else:
            super().__setattr__(attr, value)
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



NstlDefaultEnvironment = Environment(
    nstl_depth = 'NSTL_DEPTH',
    nstl_unique = 'NSTL_UNIQUE',
    nstl_depth_incr = '#include <params/depth/incr.h>',
    nstl_depth_decr = '#include <params/depth/decr.h>',
    maxdepth = 10,
    maxunique = 10,
)

depth_incr = Template("""
#if $nstl_depth == $depth
#   if $depth == $maxdepth
#       error "Maximum template depth reached."
#   endif
#   define $nstl_depth $depth_plus_1
#endif
""")


depth_decr = Template("""
#if $nstl_depth == $depth
#   if $depth == 0
#       error "Template depth can't be negative."
#   endif
#   define $nstl_depth $depth_minus_1
#endif
""")


unique_incr = Template("""
#if $nstl_unique == $unique
#   if $unique == $maxunique
#       error "Maximum unique template instantiations reached."
#   endif
#   define $nstl_unique $unique_plus_1
#endif
""")


class ScopeStack(object):
    """A class representing nested scopes.
    """
    def __init__(self):
        self.scopes = [{ }]
    
    def enterscope(self):
        self.scopes.append({ })
    
    def exitscope(self):
        self.scopes.pop()
    
    def bind(self, name, object):
        """Bind a name to an object inside the current scope.
        """
        self.scopes[-1][name] = object
    
    def resolve(self, name):
        """Return the object binding to a name, if the name is in scope.
        """
        for scope in reversed(self.scopes):
            try:
                return scope[name]
            except KeyError:
                continue
        raise NameError("name {} is not in scope".format(name))
    
    def inscope(self, name):
        """Return whether a name is reachable from the current scope.
        """
        return any(name in scope for scope in reversed(self.scopes))
    
    def show(self):
        lead = ''
        for scope in self.scopes:
            for name, object in scope.items():
                print("{}{} : {}".format(lead, name, object))
            lead = lead + ' ' * 4



class Generator(ast.NodeAccumulator):
    def __init__(self, env=NstlDefaultEnvironment):
        self.env = env
    
    def visit_Template(self, node, *args, **kwargs):
        def prepare(p):
            if p.keyword.hasparams():
                params = "(" + ", ".join(p.keyword.params) + ")"
            else:
                params = ""
            return p.keyword.name, params, p.default
        defaults = filter(lambda param: param.hasdefault(), node.params)
        defaults = (prepare(param) for param in defaults)
        all_params = (prepare(param) for param in node.params)
class CodeEmitter(TemplatedEmitter):
    def __init__(self, env=NstlDefaultEnvironment, *args, **kwargs):
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
    
    
    def emit_template_heading(self, template, **env):
        self.emit("${nstl_unique_incr}", **env)
        self._emit_for_all_depths(
        "#define ${name}_${depth}_H 1",
        name=template.name, **env)
    
    
    def emit_params_initialization(self, params, **env):
        if not params:
            return
        
        def emit_them(**env):
            rest = [ ]
            for param in filter(lambda p: p.hasdefault() or rest.append(p),
                                                                       params):
                self._emit_param_default(param, **env)
            
            for param in rest:
                self.emit("""
                #if ! defined (${param}_${unique})
                ${indent}#error "missing argument to template parameter $param"
                #endif
                """, param=param.keyword.name, **env)
        
        self._emit_for_all_uniques(emit_them, **env)
    
    def _emit_param_default(self, param, **env):
        """Emit the definition of a parameter with a default argument.
        """
        kw = param.keyword
        self.emit("""
        #if ! defined (${name}_${unique})
        ${indent}""" + self._defmacro(kw.name, kw.params, param.default) + """
        #endif
        """, name=kw.name, **env)
    
    
    def emit_params_cleanup(self, params, **env):
        """Emit the cleaning of parameters after a template.
        """
        if not params:
            return
        
        undefs = [self._undefmacro(param.keyword.name) for param in params]
        self._emit_for_all_uniques(undefs, **env)
    
    
    def emit_call(self, call, **env):
        """Emit a call to a template.
        
        call.path   the home path of the template
        call.args   the arguments to the call
        """
        args = [self._defmacro(arg.keyword.name, arg.keyword.params, arg.value)
                                                        for arg in call.args]
        if args:
            self._emit_for_all_uniques(args, **env)
        
        self.emit("""
        ${nstl_depth_incr}
        #include <${path}>
        ${nstl_depth_decr}
        """, path=call.path, **env)
    
    
    def emit_import(self, templates, **env):
        """Emit the importation of one or many templates.
        """
        for template in templates:
            self.emit("""
            #if CONCAT(${name}, _, ${nstl_depth}, _H) != 1
            ${indent}#include <${path}>
            #endif
            """, path=template.path, name=template.name, **env)
    
    
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


    
    
    def _undef_args(self, args):
        """args must be an iterable of argument names
        """
        undef_template = lambda name: "#undef {}_$unique".format(name)
        return "\n".join(undef_template(name) for name in args)
    
    
    def _create_args(self, args):
        action = self._define_args(args)
        return self._substitute_with('unique', action)
    
    
    def _call_op(self, template_path, args):
        return Template("\n".join([
        self._create_args(args),
        "$nstl_incr_depth",
        "#include <$template_path>",
        "$nstl_decr_depth"
        ])).substitute(self.env, template_path=template_path)
    
    
    def _import_stmnt(self, template_name, template_path):
        return Template("\n".join([
        "#if ! CONCAT($name, _, $nstl_depth, _H)",
            "#include <$path>",
        "#endif"
        ])).substitute(self.env, name=template_name, path=template_path)



if __name__ == "__main__":
    pass
