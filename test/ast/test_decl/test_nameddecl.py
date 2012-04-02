"""Test module for the NamedDecl class of ast/decl.py."""

import unittest
from nstl.ast.decl import NamedDecl


class _DeclarationName(object):
    """Mock class representing the name of a declaration."""
    
    def __init__(self, name):
        self.name = name


class TestNamedDecl(unittest.TestCase):
    """Test class for the NamedDecl class."""
    
    def test_should_have_name_given_at_declaration(self):
        name = _DeclarationName("foo")
        self.assertEqual(NamedDecl(name, context=None).name, name)


if __name__ == "__main__":
    pass
