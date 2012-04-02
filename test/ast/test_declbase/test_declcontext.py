"""Test module for ast/declcontext.py."""

import unittest
from nstl.ast.declbase import DeclContext
from nstl.ast.declbase import Decl


class _NamedDecl(object):
    """Mock class representing a named declaration."""
    
    def __init__(self, name):
        self.name = name
        
        class Any(object):
            def __eq__(self, other):
                return True
        
        # This is needed to trick assertions inside DeclContext
        #   that don't matter during testing
        self.lexical_context = Any()


class _DeclContext(Decl, DeclContext):
    """Mock class to bypass the inheritance constraint on DeclContext."""
    
    pass


class TestDeclContext(unittest.TestCase):
    """Test class for the DeclContext class."""
    
    def setUp(self):
        """All tests get a child declaration context, its parent, 
           another unrelated context and a list of named declarations.
        """
        self.parent = _DeclContext(None)
        self.child = _DeclContext(self.parent)
        self.other = _DeclContext(None)
        self.decls = [_NamedDecl(str(i)) for i in range(5)]
    
    def test_should_have_parent_specified_at_creation(self):
        self.assertEqual(self.child.parent, self.parent)
    
    def test_should_have_same_parent_and_lexical_parent_by_default(self):
        self.assertEqual(self.child.parent, self.child.lexical_parent)
    
    def test_should_enclose_child_context(self):
        self.assertTrue(self.parent.encloses(self.child))
    
    def test_should_not_enclose_parent_context(self):
        self.assertFalse(self.child.encloses(self.parent))
    
    def test_should_provide_iteration_over_all_declarations_in_order(self):
        for decl in self.decls:
            self.other.add(decl)
        self.assertListEqual(self.decls, list(self.other))
    
    def test_should_not_provide_iteration_over_declarations_when_empty(self):
        for decl in self.other:
            self.fail()
    
    def test_should_not_provide_iteration_over_removed_declarations(self):
        for decl in self.decls:
            self.other.add(decl)
        self.other.remove(self.decls[0])
        self.assertListEqual(self.decls[1:], list(self.other))
    
    def test_should_not_contain_declarations_when_empty(self):
        self.assertFalse(self.decls[0] in self.other)
    
    def test_should_contain_declaration_added_to_it(self):
        self.other.add(self.decls[0])
        self.assertTrue(self.decls[0] in self.other)
    
    def test_should_not_contain_declaration_removed_from_it(self):
        self.other.add(self.decls[0])
        self.other.add(self.decls[1])
        self.other.remove(self.decls[0])
        self.assertFalse(self.decls[0] in self.other)
    
    def test_should_not_find_declaration_for_declaration_not_inside_it(self):
        decl = self.decls[0]
        assert decl not in self.other
        self.assertListEqual(list(), list(self.other.lookup(decl.name)))
    
    def test_should_find_all_declarations_associated_with_a_name(self):
        decls = [_NamedDecl('foo') for i in range(5)]
        for decl in decls:
            self.other.add(decl)
        self.assertListEqual(decls, list(self.other.lookup(decls[0].name)))
    
    def test_should_find_only_declarations_associated_with_a_name(self):
        self.other.add(self.decls[0])
        self.other.add(self.decls[1])
        self.assertListEqual([self.decls[0]],
                                    list(self.other.lookup(self.decls[0].name)))
    
    def test_should_not_find_declarations_in_parent_contexts(self):
        self.parent.add(_NamedDecl('foo'))
        decls = [_NamedDecl('foo') for i in range(5)]
        for decl in decls:
            self.child.add(decl)
        self.assertListEqual(decls, list(self.child.lookup(decls[0].name)))
    
    def test_should_not_find_declarations_in_child_contexts(self):
        self.child.add(_NamedDecl('foo'))
        decls = [_NamedDecl('foo') for i in range(5)]
        for decl in decls:
            self.parent.add(decl)
        self.assertListEqual(decls, list(self.parent.lookup(decls[0].name)))
    
    def test_should_contain_declaration_made_visible_in_it(self):
        self.other.make_visible(self.decls[0])
        self.assertTrue(self.decls[0] in self.other)
    
    def test_should_provide_iteration_over_declaration_made_visible_in_it(self):
        self.other.make_visible(self.decls[0])
        self.assertListEqual([self.decls[0]], list(self.other))
    
    def test_should_find_declaration_made_visible_in_it(self):
        decl = self.decls[0]
        self.other.make_visible(decl)
        self.assertListEqual([decl], list(self.other.lookup(decl.name)))
    
    def test_should_collect_all_semantically_connected_contexts(self):
        self.assertListEqual([self.other], list(self.other.sema_connected()))


if __name__ == "__main__":
    pass
