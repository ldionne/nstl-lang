"""This file contains the Decl subclasses."""

from .declbase import Decl
from .declbase import DeclContext
from .redeclarable import Redeclarable


class TranslationUnitDecl(Decl, DeclContext):
    """This class represents the top declaration context."""
    
    def __init__(self):
        super().__init__(None) # The declaration context is None.


class NamedDecl(Decl):
    """This class represents a declaration with a name.
    
    _name       The name of the declaration in a DeclarationName object.
    
    """
    
    def __init__(self, declaration_name, context):
        super().__init__(context)
        self.name = declaration_name
    
    @property
    def name(self):
        """Return the name of the declaration."""
        return self._name
    
    @name.setter
    def name(self, decl_name):
        """Set the name of the declaration to the given DeclarationName."""
        self._name = decl_name


class NamespaceDecl(NamedDecl, DeclContext, Redeclarable):
    """This class represents a namespace declaration or definition."""
    
    def __init__(self, name, declaration_context, previous_declaration):
        super().__init__(name, declaration_context)
        if previous_declaration is not None:
            previous_declaration.redeclare_with(self)


if __name__ == "__main__":
    pass
