from .. import ast

import sys
from itertools import chain


class Scope(dict):
    def __init__(self, parent=None, name=None, *args, **kwargs):
        assert isinstance(parent, Scope) or parent is None
        
        super().__init__(*args, **kwargs)
        self.name = name
        self.parent = parent
        self.scopes = dict()
        if parent is not None and self.name is not None:
            self.parent.scopes.update({self.name:self})
    
    
    def get_outer_scope(self, name):
        """Return the nearest reachable scope with the corresponding name.
        """
        try:
            return self.scopes[name]
        except KeyError:
            if self.parent is None:
                raise NameError("scope {} is not reachable".format(name))
            return self.parent.get_outer_scope(name)
    
    
    def __contains__(self, name):
        """Return whether a name is reachable from the current scope.
        """
        return (super().__contains__(name) or
                                any(name in scope for scope in self.parents()))
    
    
    def __getitem__(self, name):
        """Return the object binding to a name, if the name is in scope.
        """
        try:
            return super().__getitem__(name)
        except KeyError:
            if self.parent is None:
                raise NameError("name {} is not in scope".format(name))
            return self.parent.__getitem__(name)
    
    
    def __setitem__(self, *args, **kwargs):
        """Bind a name to an object inside the current scope.
        """
        return super().__setitem__(*args, **kwargs)
    
    
    def parents(self):
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent
    
    
    def show(self, buf=sys.stdout):
        lead = ''
        for scope in reversed(list(chain([self], self.parents()))):
            for name, binding in scope.items():
                buf.write(lead + str(name) + " : " + str(binding) + "\n")
            lead = lead + ' ' * 4



class NameResolver(ast.NodeVisitor):
    def visit_Namespace(self, node, current_scope=Scope()):
        current_scope[node.name.value] = node
        node.scope = Scope(current_scope, node.name.value)
        self.generic_visit(node, node.scope)
    
    
    def visit_Template(self, node, current_scope=Scope()):
        current_scope[node.name.value] = node
        node.scope = Scope(current_scope)
        self.generic_visit(node, node.scope)
    
    
    def visit_Identifier(self, node, current_scope):
        if node.value not in current_scope:
            raise NameError("unresolved reference {}".format(node.value))
        node.resolved = current_scope[node.value]
    
    
    def visit_QualifiedIdentifier(self, node, current_scope):
        outer, *rest = node.quals
        scope = current_scope.get_outer_scope(outer.value)
        for qual in rest:
            scope = getattr(scope, qual.value)
        
        self.visit(node.name, scope)
        node.resolved = node.name.resolved

