"""Test module for ast/declbase.py."""

import unittest
from nstl.ast.decl import Decl


class _DeclContext(object):
    """Mock class representing a declaration context."""
    pass


class TestDecl(unittest.TestCase):
    """Test class for the Decl class."""
    
    def setUp(self):
        """All tests get a list of declarations and a list of
           their mock declaration contexts."""
        self.ctxs = [_DeclContext() for i in range(2)]
        self.decls = [Decl(ctx) for ctx in self.ctxs]
    
    def test_should_be_in_semantic_context_by_default(self):
        self.assertTrue(self.decls[0].is_in_semantic_context())
    
    def test_should_not_be_in_semantic_context_when_changed(self):
        self.decls[0].lexical_context = self.ctxs[1]
        self.assertFalse(self.decls[0].is_in_semantic_context())
    
    def test_should_have_lex_and_sema_context_specified_at_declaration(self):
        self.assertEqual(self.ctxs[0], self.decls[0].lexical_context)
        self.assertEqual(self.ctxs[0], self.decls[0].context)
    
    def test_should_have_lex_and_sema_context_specified_after_declaration(self):
        self.decls[0].context = self.ctxs[1]
        self.assertEqual(self.ctxs[1], self.decls[0].lexical_context)
        self.assertEqual(self.ctxs[1], self.decls[0].context)
    
    def test_should_provide_next_declaration_in_lexical_context(self):
        nexts = self.decls[1:]
        for i, next in enumerate(nexts):
            self.decls[i].next = next
        self.assertListEqual(nexts + [None], [decl.next for decl in self.decls])


if __name__ == "__main__":
    pass
