
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
		"""This function accumulates tokens in a sequence or list. This is
		    useful for all non terminals with the following pattern.
			non-terminal-seq : non-terminal | non-terminal-seq non-terminal
			
		skip : The number of tokens to skip after the first token in order to
				get the token to accumulate. In the example, skip=0 because the
				tokens follow each other.
		"""
		return [p[1]] if len(p) == 2 else p[1] + [p[2+skip]]
	
	
	
	def p_program(self, p):
	    """program : declaration-seq-opt
	    """
	    p[0] = ast.Program(p[1])
	
	def p_declaration_seq_opt(self, p):
	    """declaration-seq-opt : nothing
	                           | declaration-seq
	    """
	    p[0] = p[1] or [ ]
	
	def p_declaration_seq(self, p):
	    """declaration-seq : declaration
	                       | declaration-seq declaration
	    """
	    p[0] = self.accumulate(p)
	
	def p_declaration(self, p):
	    """declaration : namespace-definition
	                   | template-declaration
	    """
	    p[0] = p[1]
	
	def p_namespace_definition(self, p):
	    """namespace-definition : tNAMESPACE identifier tLBRACE namespace-body tRBRACE
	    """
	    p[0] = ast.Namespace(p[2], p[4])
	
	def p_namespace_body(self, p):
	    """namespace-body : nothing
	                      | declaration-seq
	    """
	    p[0] = p[1] or [ ]
	
	def p_template_declaration(self, p):
	    """template-declaration : tTEMPLATE identifier tLPAREN parameter-declaration-clause tRPAREN template-body
	    """
	    p[0] = ast.Template(p[2], p[4], p[6])
	
	def p_template_body(self, p):
	    """template-body : compound-statement
	    """
	    p[0] = p[1]
	
	def p_parameter_declaration_clause(self, p):
	    """parameter-declaration-clause : nothing
	                                    | parameter-declaration-list
	    """
	    p[0] = p[1] or [ ]
	
	def p_parameter_declaration_list(self, p):
	    """parameter-declaration-list : parameter-declaration
	                                  | parameter-declaration-list tCOMMA parameter-declaration
	    """
	    p[0] = self.accumulate(p, skip=1)
	
	def p_parameter_declaration(self, p):
	    """parameter-declaration : parameter-id
	                             | parameter-id tEQUALS expression
	    """
	    p[0] = ast.ParameterDeclaration(p[1], None if len(p) == 2 else p[3])
	
	def p_parameter_id(self, p):
	    """parameter-id : identifier
	                    | identifier tLPAREN identifier-list-opt tRPAREN
	    """
	    p[0] = ast.ParameterIdentifier(p[1], None if len(p) == 2 else p[3])
	
	def p_compound_statement(self, p):
	    """compound-statement : tLBRACE statement-seq-opt tRBRACE
	    """
	    p[0] = ast.CompoundStatement(p[2])
	
	def p_statement_seq_opt(self, p):
	    """statement-seq-opt : nothing
	                         | statement-seq
	    """
	    p[0] = p[1] or [ ]
	
	def p_statement_seq(self, p):
	    """statement-seq : statement
	                     | statement-seq statement
	    """
	    p[0] = self.accumulate(p)
	
	def p_statement(self, p):
	    """statement : import-statement
	                 | nest-statement
	                 | expression-statement
	    """
	    p[0] = p[1]
	
	def p_nest_statement(self, p):
	    """nest-statement : tNEST id-expression-list with-clause-opt
	    """
	    p[0] = ast.NestStatement(p[2], p[3])
	
	def p_import_statement(self, p):
	    """import-statement : tIMPORT id-expression-list with-clause-opt
	    """
	    p[0] = ast.ImportStatement(p[2], p[3])
	
	def p_expression_statement(self, p):
	    """expression-statement : expression
	    """
	    p[0] = p[1]
	
	def p_with_clause_opt(self, p):
	    """with-clause-opt : nothing
	                       | with-clause
	    """
	    p[0] = p[1] or [ ]
	
	def p_with_clause(self, p):
	    """with-clause : tWITH argument-expression-list
	    """
	    p[0] = p[2]
	
	def p_argument_expression_list(self, p):
	    """argument-expression-list : argument-expression
	                                | argument-expression-list tCOMMA argument-expression
	    """
	    p[0] = self.accumulate(p, skip=1)
	
	def p_argument_expression(self, p):
	    """argument-expression : parameter-id tEQUALS expression
	    """
	    p[0] = ast.ArgumentExpression(p[1], p[3])
	
	def p_id_expression_list(self, p):
	    """id-expression-list : id-expression
	                          | id-expression-list tCOMMA id-expression
	    """
	    p[0] = self.accumulate(p, skip=1)
	
	def p_expression(self, p):
	    """expression : tLPAREN expression tRPAREN
	                  | id-expression
	                  | raw-expression
	    """
	    p[0] = p[1] if len(p) == 2 else p[2]
	
	def p_raw_expression(self, p):
	    """raw-expression : tRAWBEGIN raw-input-opt tRAWEND
	    """
	    p[0] = ast.RawExpression(p[2])
	
	def p_raw_input_opt(self, p):
	    """raw-input-opt : nothing
	                     | raw-input
	    """
	    p[0] = p[1] or ""
	
	def p_raw_input(self, p):
	    """raw-input : tRAWINPUT
	                 | raw-input tRAWINPUT
	    """
	    p[0] = p[1] + (p[2] if len(p) > 2 else '')
	
	def p_id_expression(self, p):
	    """id-expression : unqualified-id
	                     | qualified-id
	    """
	    p[0] = p[1]
	
	def p_unqualified_id(self, p):
	    """unqualified-id : identifier
	    """
	    p[0] = p[1]
	
	def p_qualified_id(self, p):
	    """qualified-id : nested-name-specifier tPERIOD unqualified-id
	    """
	    p[0] = ast.QualifiedIdentifier(reversed(p[1]), p[3])
	
	def p_nested_name_specifier(self, p):
	    """nested-name-specifier : namespace-name
	                             | nested-name-specifier tPERIOD namespace-name
	    """
	    p[0] = self.accumulate(p, skip=1)
	
	def p_namespace_name(self, p):
	    """namespace-name : identifier
	    """
	    p[0] = p[1]
	
	def p_identifier(self, p):
	    """identifier : tID
	    """
	    p[0] = ast.Identifier(p[1])
	
	def p_identifier_list_opt(self, p):
	    """identifier-list-opt : nothing
	                           | identifier-list
	    """
	    p[0] = p[1] or [ ]
	
	def p_identifier_list(self, p):
	    """identifier-list : identifier
	                       | identifier-list tCOMMA identifier
	    """
	    p[0] = self.accumulate(p, skip=1)
	
	def p_nothing(self, p):
	    """nothing : 
	    """
	    p[0] = None
	
	def p_error(self, p):
		raise ParseError("{}: token [{}] with type [{}]"
									.format(p.lexer.lineno, p.value, p.type))
	
	
	

if __name__ == "__main__":
	pass
	