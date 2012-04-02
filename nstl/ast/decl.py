"""This file contains the Decl interface."""


class Decl(object):
    """This class represents one declaration or definition.
    
    It is the parent class for all declarations, each of which may augment
    the behavior defined here.
    
    _ctx            The semantic context in which the Decl was declared.
    _lexical_ctx    The lexical context in which the Decl was declared.
    _next           The next declaration within the same lexical context.
                        This is None when there is no next declaration.
    """
    
    def __init__(self, context, next=None):
        """Initialize the declaration. By default, both the semantic and
           lexical contexts are set to be the same."""
        self.context = context
        self.next = next
    
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


if __name__ == "__main__":
    pass
