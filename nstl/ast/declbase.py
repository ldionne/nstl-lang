"""This file contains the Decl and DeclContext interfaces."""

from collections import OrderedDict
from ..helpers.orderedset import OrderedSet


class Decl(object):
    """This class represents one declaration or definition.
    
    It is the parent class for all declarations, each of which may augment
    the behavior defined here.
    
    _ctx            The semantic context in which the Decl was declared.
    _lexical_ctx    The lexical context in which the Decl was declared.
    _next           The next declaration within the same lexical context.
                        This is None when there is no next declaration.
    
    """
    
    def __init__(self, context):
        """Initialize the declaration. By default, both the semantic and
           lexical contexts are set to be the same."""
        super().__init__()
        self.context = context
        self.next = None
    
    @property
    def context(self):
        """Return the semantic context of the declaration."""
        return self._ctx
    
    @context.setter
    def context(self, context):
        """Set both the semantic and lexical contexts of the declaration."""
        self._ctx = self.lexical_context = context
    
    @property
    def lexical_context(self):
        """Return the lexical context of the declaration."""
        return self._lexical_ctx
    
    @lexical_context.setter
    def lexical_context(self, context):
        """Set the lexical context of the declaration."""
        self._lexical_ctx = context
    
    def is_in_semantic_context(self):
        """Return whether the declaration was declared in its semantic context.
        """
        return self.context == self.lexical_context
    
    @property
    def next(self):
        """Return the next declaration within the same lexical context."""
        return self._next
    
    @next.setter
    def next(self, decl):
        """Set the next declaration within the same lexical context."""
        self._next = decl


class DeclContext(object):
    """This class represents a declaration context.
    
    It is the parent class of all declaration contexts. This class is not
    meant to be instantiated directly. It is meant to be multiply inherited
    in pair with Decl or a subclass of Decl.
    
    _decls      The structure responsible for containing the declarations
                    inside this context.
    
    """
    
    def __init__(self):
        super().__init__()
        assert isinstance(self, Decl), \
"DeclContext must be multiply inherited in pair with Decl or a subclass of it."
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
