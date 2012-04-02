"""This file contains the Redeclarable interface."""


class Redeclarable(object):
    """This class provides a common interface for the declarations
       that can be redeclared.
    
    _previous   The previous declaration of this declaration, or None.
    _next       The next declaration of this declaration, or None.
    
    """
    
    def __init__(self):
        self._previous = self._next = None
    
    @property
    def previous(self):
        """Return the previous declaration of this declaration."""
        return self._previous
    
    @property
    def next(self):
        """Return the next declaration of this declaration."""
        return self._next
    
    @property
    def first(self):
        """Return the first declaration of this declaration."""
        first = self
        while first.previous is not None:
            first = first.previous
        return first
    
    @property
    def last(self):
        """Return the last declaration of this declaration."""
        last = self
        while last.next is not None:
            last = last.next
        return last
    
    def is_last(self):
        """Return whether this declaration is the last declaration."""
        return self.next is None
    
    def is_first(self):
        """Return whether this declaration is the first declaration."""
        return self.previous is None
    
    def redeclare_with(self, declaration):
        """Redeclare this declaration with a given declaration."""
        assert isinstance(declaration, Redeclarable), \
        "can not redeclare a declaration with a non-redeclarable declaration"
        self.last._link_with(declaration)
    
    def _link_with(self, other):
        self._next = other
        other._previous = self


if __name__ == "__main__":
    pass
