#!/usr/bin/env python3


from . import ply
from .ply.lex import TOKEN



class LexError(Exception):
	pass



class NstlLexer(object):
	"""A lexer for the nstl domain specific language. After building the lexer,
		set the input text with input(), and call token() to get new tokens.
	"""
	def build(self, **kwargs):
		"""Builds the lexer from the specification.
		"""
		self.lexer = ply.lex.lex(object=self, **kwargs)
	
	def __getattribute__(self, attr):
		get = super().__getattribute__
		try:
			return get(attr)
		except AttributeError:
			return getattr(get('lexer'), attr)
	
	def __setattr__(self, attr, value):
		if (not attr in self.__dict__ and hasattr(self, 'lexer')
												and hasattr(self.lexer, attr)):
			return setattr(self.lexer, attr, value)
		return super().__setattr__(attr, value)
	
	def adjust_lineno(self, t):
		t.lexer.lineno += t.value.count("\n")
		return t
	
	
	##
	## Reserved keywords
	##
	keywords = (
		'tNAMESPACE', 'tTEMPLATE', 'tIMPORT',
	)
	keywordMap = {keyword.lstrip('t').lower():keyword for keyword in keywords}
	
	
	
	##
	## All the tokens recognized by the lexer
	##
	tokens = keywords + (
		# Identifiers
		'tID',
		
		# Delimiters
		'tLPAREN', 'tRPAREN',
		'tLBRACE', 'tRBRACE',
		'tMOD', 'tCOMMA',
		'tRAWBEGIN', 'tRAWEND', 'tRAWINPUT',
		
		# Operators
		'tPERIOD', 'tEQUALS',
	)
	
	
	
	##
	## Regexes for use in tokens
	##
	
	# valid C identifiers (K&R2: A.2.3)
	identifier = r"[a-zA-Z_][0-9a-zA-Z_]*"
	
	
	
	##
	## Lexer states
	##
	states = (
		('Ccomment', 'exclusive'),
		('Cppcomment', 'exclusive'),
		('rawinput', 'exclusive'),
	)
	
	
	
	##
	## Rules
	##
	t_ignore = " \t"
	
	# Delimiters
	t_tLBRACE		= r"\{"
	t_tRBRACE		= r"\}"
	t_tLPAREN		= r"\("
	t_tRPAREN		= r"\)"
	t_tCOMMA		= r","
	t_tPERIOD		= r"\."
	t_tMOD			= r"%"
	
	# Operators
	t_tPERIOD		= r"\."
	t_tEQUALS		= r"="
	
	
	# C style comments
	def t_beginCcomment(self, t):
		r"/\*"
		t.lexer.push_state('Ccomment')
	
	def t_Ccomment_endCcomment(self, t):
		r"\*/"
		t.lexer.pop_state()
	
	
	# C++ style comments
	def t_beginCppcomment(self, t):
		r"//"
		t.lexer.push_state('Cppcomment')
	
	def t_Cppcomment_endCppcomment(self, t):
		r"\n"
		self.adjust_lineno(t)
		t.lexer.pop_state()
	
	def t_Ccomment_Cppcomment_anything(self, t):
		r"."
		pass
	
	
	@TOKEN(identifier)
	def t_tID(self, t):
		t.type = self.keywordMap.get(t.value, t.type)
		return t
	
	
	# Raw input
	def t_tRAWBEGIN(self, t):
		r"\{%"
		t.lexer.push_state('rawinput')
		return t
	
	def t_rawinput_tRAWEND(self, t):
		r"%\}"
		t.lexer.pop_state()
		return t
	
	def t_rawinput_tRAWINPUT(self, t):
		r".|\n"
		if "\n" in t.value: self.adjust_lineno(t)
		return t
	
	
	# Always count newlines
	def t_ANY_newline(self, t):
		r"\n+"
		self.adjust_lineno(t)
	
	
	
	def t_ANY_error(self, t):
		raise LexError("{}: token [{}] with type [{}]"
									.format(t.lexer.lineno, t.value, t.type))








#---------------------------------old----------------------------------------#
# # These rules are defined here so they have more priority than anything else
# #	They serve the purpose of lexing only the input marked up with @nstl
# def adjust_lineno(t):
# 	t.lexer.lineno += t.value.count("\n")
# 	return t
# 
# def NEWLINE(self, t):
# 	r"\n+"
# 	adjust_lineno(t)
# 
# def START(self, t):
# 	r"@nstl"
# 	t.lexer.push_state('enabled')
# 	return t
# 
# def ANYTHING(self, t):
# 	r"."
# 	pass
# 
# 
# class WithSubcontexts(type):
# 	"""A metaclass to automatically create lexing subcontexts.
# 	A context is characterized by start and stop triggers, and an optional
# 	interrupt trigger. The context is entered when the start trigger is
# 	encountered, and the whole input gathered inside the context is returned
# 	with the specified token type when the stop trigger is met.
# 
# 	For a lexing class to be able to have sub contexts, it must have its
# 	metaclass set to WithSubcontexts and the desired subcontext rules must
# 	be decorated with the @subcontext decorator.
# 	"""
# 	def __new__(cls, name, bases, namespace):
# 		subctxStates = tuple()
# 		unique = 0
# 		subcontexts = { }
# 		lexer = super().__new__(cls, name, bases, namespace)
# 		for name, interrupt in lexer.__dict__.copy().items():
# 			if hasattr(interrupt, "issubcontext"):
# 				ctx = "autosubctx{}".format(unique)
# 			
# 				class enterCtx(object):
# 					def __init__(self, ctx, interrupt):
# 						self.tokenType = interrupt.tokenType
# 						self.ctx = ctx
# 						self.interrupt = interrupt
# 						self.do = interrupt.startAction
# 						self.discard = interrupt.discard
# 					def __call__(self, t):
# 						start = True
# 						if self.do:
# 							start = self.do(t)
# 						if start is not False:
# 							t.lexer.push_state(self.ctx)
# 							if not self.discard:
# 							 	accumulate(t.lexer, t)
# 					__call__.__doc__ = interrupt.start
# 				states = "_".join(interrupt.states)
# 				setattr(lexer, "t_{}_enterctx{}".format(states, unique),
# 											enterCtx(ctx, interrupt).__call__)
# 			
# 				if interrupt.__doc__ is not None:
# 					class intCtx(object):
# 						def __init__(self, interrupt):
# 							self.interrupt = interrupt
# 						def __call__(self, t, *args, **kwargs):
# 							return self.interrupt(t, *args, **kwargs)
# 						__call__.__doc__ = interrupt.__doc__
# 					setattr(lexer, "t_{}_interrupt".format(ctx),
# 													intCtx(interrupt).__call__)
# 			
# 				class exitCtx(object):
# 					def __init__(self, interrupt):
# 						self.tokenType = interrupt.tokenType
# 						self.do = interrupt.stopAction
# 						self.discard = interrupt.discard
# 					def __call__(self, t):
# 						stop = True
# 						if self.do:
# 							stop = self.do(t)
# 						if stop is not False:
# 							t.lexer.pop_state()
# 							if not self.discard:
# 								t.value = unload(t.lexer)
# 								t.type = self.tokenType
# 								return t
# 					__call__.__doc__ = interrupt.stop
# 				setattr(lexer, "t_{}_exit".format(ctx),
# 												exitCtx(interrupt).__call__)
# 			
# 				def ignoreCtx(self, t):
# 					r".|\n"
# 					pass
# 				setattr(lexer, "t_{}_ignoretherest".format(ctx), ignoreCtx)
# 			
# 				subctxStates = subctxStates + ((ctx, 'exclusive'), )
# 				unique += 1
# 	
# 		lexer.states = subctxStates + (lexer.states if hasattr(lexer, "states")
# 													else tuple())
# 		return lexer
# 
# def subcontext(start, stop, tokenType='', discard=False, states=('INITIAL', )):
# 	"""Create a new subcontext.
# 	tokenType		The token type returned when stop is met.
# 	start			The start regex triggering the sub context.
# 	stop			The stop regex triggering the end of the sub context.
# 	states			Optional states of the subcontext.
# 	"""
# 	def decorator(intr):
# 		intr.issubcontext = True
# 	
# 		intr.start, intr.startAction = (start if isinstance(start, tuple)
# 											else (start, None))
# 		intr.stop, intr.stopAction = (stop if isinstance(stop, tuple)
# 											else (stop, None))
# 		intr.tokenType = tokenType
# 		intr.discard = discard
# 		intr.states = states if isinstance(states, tuple) else (states, )
# 		return intr
# 	return decorator
# 
# def accumulate(lexer, token):
# 	pos = lexer.lexpos-len(token.value)
# 	if not hasattr(lexer, "_accumulateStack"):
# 		lexer._accumulateStack = [ ]
# 	lexer._accumulateStack.append(pos)
# 
# def unload(lexer):
# 	buf = lexer.lexdata[lexer._accumulateStack.pop():lexer.lexpos]
# 	return buf
# 
# 
# class NstlLexer(object, metaclass=WithSubcontexts):
# 	##
# 	## Reserved keywords
# 	##
# 	keywords = (
# 		'tSTART', 'tTEMPLATE', 'tINSTANTIATE', 'tIMPLEMENT', 'tDEFAULTS',
# 		'tNAMESPACE',
# 	)
# 	keywordMap = { }
# 	for keyword in keywords:
# 		if keyword != 'tSTART':
# 			keywordMap[keyword.lstrip('t').lower()] = keyword
# 
# 	##
# 	## All the tokens recognized by the lexer
# 	##
# 	tokens = keywords + (
# 		# Identifiers
# 		'tID',
# 	
# 		# Delimiters
# 		'tCOMMA', 'tPERIOD',
# 		'tLPAREN', 'tRPAREN',
# 		'tLBRACE', 'tRBRACE',
# 		'tLBRACKET', 'tRBRACKET',
# 		'tLT', 'tGT', 'tMOD', 'tSEMI',
# 	
# 		# Raw input
# 		'tRAW',
# 	)
# 
# 	##
# 	## Regexes for use in tokens
# 	##
# 
# 	# valid C identifiers (K&R2: A.2.3)
# 	identifier = r"[a-zA-Z_][0-9a-zA-Z_]*"
# 
# 
# 	##
# 	## Lexer states
# 	##
# 	states = (
# 		# When in between @nstl{...}
# 		('enabled', 'inclusive'),
# 	)
# 
# 	##
# 	## Rules for the INITIAL state
# 	##
# 	t_tNEWLINE = NEWLINE
# 	t_tSTART = START
# 	t_tANYTHING = ANYTHING
# 
# 	##
# 	## Rules for the enabled state
# 	##
# 	t_enabled_ignore = " \t"
# 
# 	# Newlines
# 	def t_enabled_tNEWLINE(self, t):
# 		r"\n+"
# 		adjust_lineno(t)
# 
# 	# Delimiters
# 	t_enabled_tLPAREN		= r"\("
# 	t_enabled_tRPAREN		= r"\)"
# 	t_enabled_tLBRACKET		= r"\["
# 	t_enabled_tRBRACKET		= r"\]"
# 	t_enabled_tCOMMA		= r","
# 	t_enabled_tPERIOD		= r"\."
# 	t_enabled_tLT			= r"<"
# 	t_enabled_tGT			= r">"
# 	t_enabled_tMOD			= r"%"
# 	t_enabled_tSEMI			= r";"
# 
# 	@TOKEN(identifier)
# 	def t_enabled_tID(self, t):
# 		t.type = self.keywordMap.get(t.value, 'tID')
# 		return t
# 
# 	# Match braces to disable lexing when out of @nstl{ ... }
# 	def t_enabled_tLBRACE(self, t):
# 		r"\{"
# 		t.lexer.braces += 1
# 		return t
# 
# 	def t_enabled_tRBRACE(self, t):
# 		r"\}"
# 		t.lexer.braces -= 1
# 		if not t.lexer.braces:
# 			t.lexer.pop_state()
# 		elif t.lexer.braces < 0:
# 			raise SyntaxError("Unexpected closing brace.")
# 		return t
# 
# 
# 	# Raw C input
# 	def set_braces(t):
# 		t.lexer.rawc_braces = 1
# 	def match_braces(t):
# 		t.lexer.rawc_braces -= 1
# 		if t.lexer.rawc_braces:
# 			return False
# 	@subcontext((r"%\{", set_braces), (r"\}", match_braces), tokenType='tRAW',
# 															states='enabled')
# 	def interrupt_tRAW(t):
# 		r"\n|\{"
# 		if t.value == "\n":
# 			adjust_lineno(t)
# 		else:
# 			t.lexer.rawc_braces += 1
# 
# 
# 	# Comments
# 	@subcontext(r"/\*", r"\*/", discard=True, states='enabled')
# 	def interrupt_CCOMMENT(t):
# 		r"\n+"
# 		adjust_lineno(t)
# 
# 	@subcontext(r"//", (r"\n", adjust_lineno), discard=True, states='enabled')
# 	def interrupt_CPPCOMMENT(t):
# 		pass
# 	
# 
# 	# C string constants
# 	@subcontext(r"\"", r"\"", tokenType='cstring', states='enabled')
# 	def interrupt_CSTRING(t):
# 		r"\n"
# 		print(t.lexer.lexdata[t.lexer.lexpos:])
# 		raise SyntaxError("Found line break inside string constant.")
# 
# 	# C character constants
# 	@subcontext(r"'", "'", tokenType='ccharconst', states='enabled')
# 	def interrupt_CCHARCONST(t):
# 		r"\n"
# 		raise SyntaxError("Found line break inside character constant.")
# 
# 	def t_ANY_error(self, t):
# 		print(t.lexer.lexdata[:t.lexer.lexpos])
# 		raise SyntaxError(
# 		"Tokenizer error:token [{}] with type [{}]".format(t.value, t.type))
	
	

if __name__ == "__main__":
	pass
