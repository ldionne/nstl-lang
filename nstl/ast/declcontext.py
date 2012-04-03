"""This file contains the DeclContext interface."""

from collections import OrderedDict
from ..helpers.orderedset import OrderedSet
from .decl import Decl


class DeclContext(Decl):
    """This class represents a declaration context.
    
    It is the parent class of all declaration contexts.
    
    _decls      The structure responsible for containing the declarations
                    inside this context.
    """
    
    def __init__(self, parent, next=None):
        super().__init__(parent, next)
        self._decls = OrderedDict()
    
    def __contains__(self, decl):
        """Return whether the declaration is within the declaration context."""
        return decl in iter(self)
    
    def __iter__(self):
        """Iterate over all the declarations stored within this context."""
        for decl_chain in self._decls.values():
            for decl in decl_chain:
                yield decl
    
    @property
    def lexical_parent(self):
        """Return the containing lexical declaration context."""
        return self.lexical_context
    
    @property
    def parent(self):
        """Return the containing declaration context."""
        return self.context
    
    def encloses(self, other):
        """Return whether this declaration context encloses an
           other declaration context 'other'."""
        return other == self or (other.parent and self.encloses(other.parent))
    
    def sema_connected(self):
        """Iterate over all of the declaration contexts that are semantically
           connected to this declaration context.
        
        For a generic declaration context, there are not other contexts.
        
        """
        yield self
    
    def add(self, decl):
        """Add a declaration to this context."""
        assert decl.lexical_context == self, \
                                "declaration added in wrong lexical context"
        self.make_visible(decl)
    
    def remove(self, decl):
        """Remove a declaration from this context."""
        assert decl.lexical_context == self, \
    "declaration being removed from something else than its lexical context"
        self._decls[decl.name].remove(decl)
        if not self._decls[decl.name]:
            del self._decls[decl.name]
    
    def lookup(self, decl_name):
        """Iterate over all the declarations with the given name
           in this context."""
        if decl_name not in self._decls.keys(): raise StopIteration
        for decl in self._decls[decl_name]:
            yield decl
    
    def make_visible(self, decl):
        """Make a declaration visible inside this context, without changing
           the ownership of the declaration."""
        if decl.name not in self._decls.keys():
            self._decls[decl.name] = OrderedSet()
        self._decls[decl.name].add(decl)


if __name__ == "__main__":
    pass
