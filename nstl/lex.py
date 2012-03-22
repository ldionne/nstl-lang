
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
        'tNAMESPACE', 'tTEMPLATE', 'tIMPORT', 'tNEST', 'tWITH',
    )
    keywordMap = {keyword.lstrip('t').lower():keyword for keyword in keywords}
    
    
    
    ##
    ## All the tokens recognized by the lexer
    ##
    tokens = keywords + (
        'tID',
        
        'tLPAREN', 'tRPAREN',
        'tLBRACE', 'tRBRACE',
        'tRAWBEGIN', 'tRAWEND', 'tRAWINPUT',
        
        'tCOMMA', 'tPERIOD', 'tEQUALS',
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
    
    t_tLBRACE       = r"\{"
    t_tRBRACE       = r"\}"
    t_tLPAREN       = r"\("
    t_tRPAREN       = r"\)"
    
    t_tCOMMA        = r","
    t_tPERIOD       = r"\."
    t_tEQUALS       = r"="
    
    
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



if __name__ == "__main__":
    pass
