"""Interface to store lexical scope related information
   used during semantic analysis."""

import sys
from itertools import chain
from ..helpers import orderedset


class Scope(object):
    """Parent class for all scopes.
    
    Implements generic lexical scoping operations.
    
    _parent     The parent scope of this scope, or None for outermost scope.
    _entity     The entity associated with this scope, or None. For example,
                    the entity of a namespace scope is the namespace itself.
    _decls      An ordered set keeping track of all declarations in this scope.
    
    """
    def __init__(self, parent=None, entity=None):
        if not (isinstance(parent, Scope) or parent is None): raise TypeError(
            "invalid type {} for parent scope. must be Scope instance or None."
                                                        .format(type(parent)))
        self._parent = parent
        self._entity = entity
        self._decls = orderedset.OrderedSet()
    
    def __contains__(self, decl):
        """Return whether a declaration was declared in this scope."""
        return decl in self._decls
    
    def __iter__(self):
        """Iterate over all the declarations made in this scope.
        
        Iteration is done over the declarations in the order they were added.
        
        """
        for decl in self._decls:
            yield decl
    
    def add(self, decl):
        """Add a declaration in this scope."""
        self._decls.add(decl)
    
    def is_outermost(self):
        """Return whether this scope is an outermost scope."""
        return self._parent is None
    
    @property
    def parent(self):
        """Return the direct parent of this scope, or None when outermost."""
        return self._parent
    
    def parents(self):
        """Iterate over the parents of this scope.
        
        Iteration is done in lexical order, so innermost parents
        are visited first.
        
        """
        if self.is_outermost():
            raise StopIteration
        yield self._parent
        for parent in self._parent.parents():
            yield parent
    
    
    def show(self, buf=sys.stdout, decls=False):
        """Write a formatted description of a scope and its parents to a buffer.
        
        If decls is True, the declarations contained in each scope are shown.
        
        """
        lead = ''
        for scope in reversed(list(chain([self], self.parents()))):
            buf.write(lead + "scope owned by {} :\n".format(self._entity))
            if decls:
                buf.write(lead + str(self._decls) + "\n")
            lead = lead + ' ' * 2


if __name__ == "__main__":
    pass
