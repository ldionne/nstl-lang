#!/usr/bin/env python3

from string import Template
from . import nstl_ast

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
#	if $depth == $maxdepth
#		error "Maximum template depth reached."
#	endif
#	define $nstl_depth $depth_plus_1
#endif
""")


depth_decr = Template("""
#if $nstl_depth == $depth
#	if $depth == 0
#		error "Template depth can't be negative."
#	endif
#	define $nstl_depth $depth_minus_1
#endif
""")


unique_incr = Template("""
#if $nstl_unique == $unique
#	if $unique == $maxunique
#		error "Maximum unique template instantiations reached."
#	endif
#	define $nstl_unique $unique_plus_1
#endif
""")



class Generator(nstl_ast.NodeAccumulator):
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
		
		return "\n".join([
		self._signalize(node.name),
		self._init_args(defaults, all_params),
		
		self.passon(node, *args, **kwargs),
		
		self._clean_args((param.keyword.name for param in node.params)),
		])
	
	
	
	def visit_Import(self, node, *args, **kwargs):
		return "visit_Import\n"
	
	
	
	def visit_CallOp(self, node, *args, **kwargs):
		return "visit_CallOp\n"
	
	
	
	#
	# Helpers
	#
	def _substitute_with(self, variant, text, **env):
		assert isinstance(variant, str)
		max_reps = getattr(self.env, 'max'+variant)
		stream = self._variable_subs(variant, text, range(max_reps), **env)
		acc = [ ]
		#implement binary search
		for i, atom in enumerate(stream):
			acc.append(atom)
		return "\n".join(acc)
	
	
	def _variable_subs(self, variant, text, generator, **env):
		before = "#if $nstl_{0} == ${0}".format(variant)
		after = "#endif"
		text = Template("\n".join([before, text, after]))
		for i in generator:
			env[variant] = i
			yield text.substitute(self.env, **env)
	
	
	def _signalize(self, template_name):
		action = "#define ${template_name}_${depth}_H 1"
		return self._substitute_with('depth', action, template_name=template_name)
	
	
	def _init_args(self, default_args, all_args):
		define_defaults = self._define_args(default_args)
		assert_all_defined = "\n".join(Template("\n".join([
		"#if !defined (${arg}_$unique)",
		"#error \"Missing template argument $arg.\"",
		"#endif"
		])).substitute(arg=arg[0], unique='$unique') for arg in all_args)
		
		action = "\n".join([define_defaults, assert_all_defined])
		return self._substitute_with('unique', action)
	
	
	def _clean_args(self, arg_names):
		action = self._undef_args(arg_names)
		return self._substitute_with('unique', action)
	
	
	def _define_args(self, args):
		"""args must be an iterable of tuples like this:
		(argument_name, argument_parameters, argument_definition)
		"""
		arg_template = lambda arg: "#define {}_$unique{} {}".format(*arg)
		return "\n".join(arg_template(arg) for arg in args)
	
	
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



#---------------------------------old----------------------------------------#
# write = Template("""
# #if $thisdepth
# #	if defined ($macro)
# #		warning	\"Template parameter $macro is being overwritten at coordinates ($x, $y).\"
# #	endif
# #	define $macro$args $definition
# #endif
# """)
# 
# instantiate = Template("""
# #if defined ($nstl_instantiate)
# 	$write
# #endif
# """)
# 
# default = Template("""
# # if defined ($nstl_default)
# 	$write
# #endif
# """)
# 
# 
# clean = Template("""
# #if defined ($nstl_clean) && $thisdepth && defined ($macro)
# #	undef $macro
# #endif
# """)
# 
# 
# require = Template("""
# #if defined ($nstl_require) && $thisdepth && !defined ($macro)
# #	error \"Missing required template parameter $macro at coordinates ($x, $y).\"
# #endif
# """)
# 
# 
# thisdepth = Template("$nstl_y == $y && $nstl_x == $x")
# 
# 
# 
# 
# env = dict(
# nstl_x = "NSTL_TEMPLATE_X_",
# nstl_y = "NSTL_TEMPLATE_Y_${x}_",
# x_max = 10,
# y_max = 10,
# nstl_require = "NSTL_TEMPLATE_REQUIRE_",
# nstl_clean = "NSTL_TEMPLATE_CLEAN_PARAMS_",
# nstl_instantiate = "NSTL_TEMPLATE_INSTANTIATE_",
# )
# 
# env.update(dict(
# thisdepth = thisdepth,
# 
# ))
# 
# 
# def parameter(p):
# 	if not hasattr(p, "args"):
# 		p.args = None
# 	elif not isinstance(p.args, tuple):
# 		p.args = (p.args, )
# 	
# 	if not hasattr(p, "default"):
# 		p.default = None
# 	else:
# 		# Backslash the end of the lines automatically for the preprocessor
# 		p.default = "\\\n".join(p.default.splitlines())
# 		p.default = Template(p.default)
# 	
# 	p.name = p.__name__
# 	
# 	return p
# 
# def paramclass(cls):
# 	for name, member in vars(cls).items():
# 		if not name.startswith("__"):
# 			setattr(cls, name, parameter(member))
# 
# @paramclass
# class Misc(object):
# 	class FuncName(object):
# 		args = "func"
# 		default = "$func"
# 	
# 	class Container(object):
# 		pass
# 	
# 	class Allocate(object):
# 		args = "size", "n"
# 		default = "nstl_default_alloc_($size, $n)"
# 	
# 	class Deallocate(object):
# 		args = "ptr", "n"
# 		default = "nstl_default_dealloc_($ptr, $n)"
# 	
# 	class Iterator(object):
# 		default = "CONCAT(Container, Iterator)"
# 	
# 	class Adaptor(object):
# 		default = "sequence/dlist"
# 
# @paramclass
# class Node(object):
# 	class NodeType(object):
# 		pass
# 	
# 	class NodeNext(object):
# 		pass
# 	
# 	class NodePrev(object):
# 		pass
# 	
# 	class NodeToValue(object):
# 		pass
# 	
# 	class NodeJumpForward(object):
# 		pass
# 	
# 	class NodeJumpForward(object):
# 		pass
# 
# @paramclass
# class Value(object):
# 	class ValueConstruct(object):
# 		args = "this", "value"
# 		default = "(*($this) = ($value))"
# 	
# 	class ValueDestruct(object):
# 		args = "this"
# 	
# 	class ValueEqual(object):
# 		args = "a", "b"
# 		default = "(($a) == ($b))"
# 	
# 	class ValueStrictWeakOrdering(object):
# 		args = "a", "b"
# 		default = "(($a) < ($b))"
# 	
# 	class ValueType(object):
# 		pass
# 	
# 	class ValueToNode(object):
# 		pass



if __name__ == "__main__":
	pass
