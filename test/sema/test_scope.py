"""Test module for sema/scope.py."""

import unittest
from nstl.sema.scope import Scope


class _Decl(object):
    """Mock class representing a declaration."""
    
    pass


class ScopeTest(unittest.TestCase):
    """Test class for Scopes."""
    
    def setUp(self):
        self.maxDiff = None
        self.scope = Scope()
        self.decls = [_Decl() for i in range(3)]
    
    def test_should_contain_a_declaration_made_in_it(self):
        self.scope.add(self.decls[0])
        self.assertTrue(self.decls[0] in self.scope)
    
    def test_should_not_contain_a_declaration_made_nowhere(self):
        self.scope.add(self.decls[0])
        self.assertFalse(self.decls[1] in self.scope)
    
    def test_should_not_contain_a_declaration_made_in_a_parent_scope(self):
        child = Scope(self.scope)
        self.scope.add(self.decls[0])
        self.assertFalse(self.decls[0] in child)
    
    def test_should_not_contain_a_declaration_made_in_a_child_scope(self):
        child = Scope(self.scope)
        child.add(self.decls[0])
        self.assertFalse(self.decls[0] in self.scope)
    
    def test_should_not_contain_declarations_when_empty(self):
        for decl in self.scope:
            self.fail()
    
    def test_should_provide_iterator_over_all_decls_it_contains_in_order(self):
        for decl in self.decls:
            self.scope.add(decl)
        self.assertListEqual(self.decls, list(decl for decl in self.scope))
    
    def test_should_appear_as_outermost_when_parentless(self):
        self.assertTrue(self.scope.is_outermost())
    
    def test_should_not_appear_as_outermost_when_having_parents(self):
        child = Scope(self.scope)
        self.assertFalse(child.is_outermost())
    
    def test_should_provide_parent_scope_or_None_when_outermost(self):
        self.assertIsNone(self.scope.parent)
        self.assertEqual(Scope(self.scope).parent, self.scope)
    
    def test_should_provide_iterator_over_all_parents_in_order(self):
        parent = self.scope
        parents = [parent]
        for i in range(3):
            parent = Scope(parent)
            parents.append(parent)
        child = Scope(parent)
        self.assertListEqual(list(reversed(parents)), list(child.parents()))
    
    def test_should_provide_empty_sequence_of_parents_when_outermost(self):
        self.assertListEqual(list(), list(self.scope.parents()))        


if __name__ == "__main__":
    pass
