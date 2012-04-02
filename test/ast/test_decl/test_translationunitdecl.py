"""Test module for the TranslationUnitDecl class of ast/decl.py."""

import unittest
from nstl.ast.decl import TranslationUnitDecl


class TestTranslationUnitDecl(unittest.TestCase):
    """Test class for the TranslationUnitDecl class."""
    
    def test_should_have_no_parent_declaration_context(self):
        self.assertIsNone(TranslationUnitDecl().parent)


if __name__ == "__main__":
    pass
