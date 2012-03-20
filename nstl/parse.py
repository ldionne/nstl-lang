
from . import ply
from .ply import yacc
from . import ast
from . import lex



class ParseError(Exception):
	pass



class NstlParser(object):
	def __init__(self, lexoptimize=True, lextab='_lextab',
					yaccoptimize=True, yacctab='_yacctab', yaccdebug=False):
		"""Create a new parser for the nstl micro-language.
		"""
		self.lexer = lex.NstlLexer()
		self.lexer.build(optimize=lexoptimize, lextab=lextab)
		self.tokens = self.lexer.tokens
		self.parser = ply.yacc.yacc(module=self, debug=yaccdebug,
									optimize=yaccoptimize, tabmodule=yacctab)
	
	def parse(self, text, **kwargs):
		return self.parser.parse(text, lexer=self.lexer, **kwargs)
	
	def accumulate(self, p, skip=0):
		"""This function accumulates tokens in a list. This is useful for all
			non terminals with the following pattern.
			non-terminal-list : non-terminal | non-terminal-list non-terminal
		skip : The number of tokens to skip after the first token in order to
				get the token to accumulate. In the example, skip=0 because the
				tokens follow each other.
		"""
		return [p[1]] if len(p) == 2 else p[1] + [p[2+skip]]
	
	
	
	def p_input(self, p):
		"""input : nothing
				 | def-list
		"""
		p[0] = ast.Program(p[1] or [ ])
	
	
	
	#
	# Statements
	#
	def p_statement(self, p):
		"""stmnt : import-stmnt
		"""
		p[0] = p[1]
	
	
	
	# Import
	def p_import_statement(self, p):
		"""import-stmnt : tIMPORT arg-expr-list
		"""
		p[0] = ast.Import(p[2])
	
	
	
	#
	# Definitions
	#
	def p_definition(self, p):
		"""def : namespace-def
			   | template-def
		"""
		p[0] = p[1]
	
	
	
	# Namespace
	def p_namespace_definition(self, p):
		"""namespace-def : tNAMESPACE identifier tLBRACE nothing tRBRACE
						 | tNAMESPACE identifier tLBRACE def-list tRBRACE
		"""
		p[0] = ast.Namespace(p[2], p[4] or [ ])
	
	
	
	# Template
	def p_template_definition(self, p):
		"""template-def : template-begin template-params template-body
		"""
		p[0] = ast.Template(p[1], p[2] or [ ], p[3] or [ ])
	
	def p_template_begin(self, p):
		"""template-begin : tTEMPLATE identifier
		"""
		p[0] = p[2]
	
	def p_template_params(self, p):
		"""template-params : tLPAREN nothing tRPAREN
						   | tLPAREN param-list tRPAREN
		"""
		p[0] = p[2]
	
	def p_template_body(self, p):
		"""template-body : tLBRACE nothing tRBRACE
						 | tLBRACE stmnt-or-expr-list tRBRACE
		"""
		p[0] = p[2]
	
	
	
	#
	# Expressions
	#
	def p_expression(self, p):
		"""expr : postfix-expr
		"""
		p[0] = p[1]
	
	
	
	def p_postfix_expression__primary_expr(self, p):
		"""postfix-expr : primary-expr
		"""
		p[0] = p[1]
	
	def p_postfix_expression__scope_op(self, p):
		"""postfix-expr : postfix-expr tPERIOD identifier
		"""
		p[0] = ast.ScopeOp(p[1], p[3])
	
	def p_postfix_expression__call_op(self, p):
		"""postfix-expr : postfix-expr tLPAREN nothing tRPAREN
						| postfix-expr tLPAREN arg-list tRPAREN
		"""
		p[0] = ast.CallOp(p[1], p[3] or [ ])
	
	
	def p_primary_expression__ident(self, p):
		"""primary-expr : identifier
		"""
		p[0] = p[1]
	
	def p_primary_expression__rawinput(self, p):
		"""primary-expr : rawinput
		"""
		p[0] = p[1]
	
	def p_primary_expression__expr(self, p):
		"""primary-expr : tLPAREN expr tRPAREN
		"""
		p[0] = p[2]
	
	
	
	#
	# Others
	#
	def p_argument_list(self, p):
		"""arg-list : arg
					| arg-list tCOMMA arg
		"""
		p[0] = self.accumulate(p, skip=1)
		if len(p[0]) > 1 and p[0][0].haskeyword() and not p[0][1].haskeyword():
			raise ParseError("non-keyword argument follows keyword argument")
	
	def p_argument(self, p):
		"""arg : expr
			   | param-id tEQUALS expr
		"""
		if len(p) > 2:
			p[0] = ast.Argument(p[3], p[1])
		else:
			p[0] = ast.Argument(p[1], None)
	
	
	
	def p_parameter_list(self, p):
		"""param-list : param
					  | param-list tCOMMA param
		"""
		p[0] = self.accumulate(p, skip=1)
		if len(p[0]) > 1 and p[0][0].hasdefault() and not p[0][1].hasdefault():
			raise ParseError("non-default argument follows default argument")
	
	def p_parameter(self, p):
		"""param : param-id
				 | param-id tEQUALS expr
		"""
		p[0] = ast.Parameter(p[1], p[3] if len(p) > 2 else None)
	
	def p_parameter_identifier(self, p):
		"""param-id : tID param-id-params
		"""
		p[0] = ast.ParameterId(p[1], p[2])
	
	def p_parameter_identifier_params(self, p):
		"""param-id-params : nothing
						   | tLPAREN nothing tRPAREN
						   | tLPAREN tID-list tRPAREN
		"""
		p[0] = p[1] if len(p) == 2 else (p[2] or [ ])
	
	def p_parameter_identifier_params_tID_list(self, p):
		"""tID-list : tID
					| tID-list tCOMMA tID
		"""
		p[0] = self.accumulate(p, skip=1)
	
	
	
	def p_identifier(self, p):
		"""identifier : tID
		"""
		p[0] = ast.Identifier(p[1])
	
	def p_identifier_list(self, p):
		"""identifier-list : identifier
						   | identifier-list tCOMMA identifier
		"""
		p[0] = self.accumulate(p, skip=1)
	
	
	
	def p_rawinput(self, p):
		"""rawinput : tRAWBEGIN nothing tRAWEND
					| tRAWBEGIN rawinput_aux tRAWEND
		"""
		p[0] = ast.Raw("" if p[2] is None else "".join(p[2]))
	
	def p_rawinput_aux(self, p):
		"""rawinput_aux : tRAWINPUT
						| rawinput_aux tRAWINPUT
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_nothing(self, p):
		"""nothing : 
		"""
		p[0] = None
	
	
	
	#
	# Helpers
	#
	def p_statement_list(self, p):
		"""stmnt-list : stmnt
					  | stmnt-list stmnt
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_definition_list(self, p):
		"""def-list : def
					| def-list def
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_expression_list(self, p):
		"""expr-list : expr
					 | expr-list expr
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_argument_expression_list(self, p):
		"""arg-expr-list : expr
						 | arg-expr-list tCOMMA expr
		"""
		p[0] = self.accumulate(p, skip=1)
	
	
	
	def p_definition_or_statement(self, p):
		"""def-or-stmnt : def
						| stmnt
		"""
		p[0] = p[1]
	
	def p_definition_or_statement_list(self, p):
		"""def-or-stmnt-list : def-or-stmnt
							 | def-or-stmnt-list def-or-stmnt
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_statement_or_expression(self, p):
		"""stmnt-or-expr : stmnt
						 | expr
		"""
		p[0] = p[1]
	
	def p_statement_or_expression_list(self, p):
		"""stmnt-or-expr-list : stmnt-or-expr
							  | stmnt-or-expr-list stmnt-or-expr
		"""
		p[0] = self.accumulate(p)
	
	
	
	def p_error(self, p):
		raise ParseError("{}: token [{}] with type [{}]"
									.format(p.lexer.lineno, p.value, p.type))
	
	
	

if __name__ == "__main__":
	pass
	