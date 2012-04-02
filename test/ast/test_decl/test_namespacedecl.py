"""Test module for the NamespaceDecl class of ast/namespacedecl.py."""

import unittest
from nstl.ast.decl import NamespaceDecl


class TestNamespaceDecl(unittest.TestCase):
    """Test class for the NamespaceDecl class."""
    
    def test_should_redeclare_itself_as_told_to(self):
        first = NamespaceDecl('foo', None, None)
        second = NamespaceDecl('bar', None, first)
        self.assertEqual(second.previous, first)


if __name__ == "__main__":
    pass
