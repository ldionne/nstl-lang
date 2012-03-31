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


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


class NameCollector(ast.NodeTransformer):
    def visit_Program(self, root, current_scope=Scope()):
        new_root = self.generic_visit(root, current_scope)
        new_root.decls = ast.Nodelist(unique(new_root.decls))
        return new_root
    
    def visit_Namespace(self, node, current_scope=Scope()):
        if node.name.value in current_scope:
            already_there = current_scope[node.name.value]
            current_scope = already_there.scope
            for decl in node.decls:
                already_there.decls.append(self.visit(decl, current_scope))
            
            already_there.decls = ast.Nodelist(unique(already_there.decls))
            return already_there
        else:
            current_scope[node.name.value] = node
            node.a.scope = Scope(current_scope, node.name.value)
            return self.generic_visit(node, node.scope)
    
    def visit_Template(self, node, current_scope=Scope()):
        if node.name.value in current_scope:
            raise NameError("redefinition of template "+ node.name.value)
        current_scope[node.name.value] = node
        node.a.scope = Scope(current_scope)
        return self.generic_visit(node, node.scope)


def merge_asts(*programs):
    decls = [ ]
    for prog in programs:
        for decl in prog.decls:
            decls.append(decl)
    
    return ast.Program(decls)


class NameResolver(ast.NodeTransformer):
    def visit_Program(self, root):
        scope = Scope()
        root = NameCollector().visit(root, scope)
        return self.generic_visit(root, scope)
    
    def visit_Namespace(self, node, scope):
        return self.generic_visit(node, node.scope)
    
    def visit_Template(self, node, scope):
        return self.generic_visit(node, node.scope)
    
    def visit_Identifier(self, node, current_scope):
        if node.value not in current_scope:
            raise NameError("unresolved reference {}".format(node.value))
        node.a.resolved = current_scope[node.value]
        return node
    
    def visit_QualifiedIdentifier(self, node, current_scope):
        outer, *rest = list(reversed(node.quals))
        scope = current_scope.get_outer_scope(outer.value)
        for qual in rest:
            scope = scope[qual.value].scope
        
        self.visit(node.name, scope)
        node.a.resolved = node.name.resolved
        return node

