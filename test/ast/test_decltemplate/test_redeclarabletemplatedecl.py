"""Test module for the RedeclarableTemplateDecl class of ast/decltemplate.py."""

import unittest
from nstl.ast.decltemplate import RedeclarableTemplateDecl


class TestRedeclarableTemplateDecl(unittest.TestCase):
    """Test class for the RedeclarableTemplateDecl class."""
    
    def setUp(self):
        """All tests get two RedeclarableTemplateDecl instances."""
        self.other = RedeclarableTemplateDecl(None, None, None, None)
        self.decl = RedeclarableTemplateDecl(None, None, None, None)
    
    def test_should_not_be_instantiated_from_member_template_by_default(self):
        self.assertFalse(self.decl.is_instantiated_from_member_template())
        self.assertIsNone(self.decl.instantiated_from_member_template)
    
    def test_should_be_instantiated_from_member_template_when_set(self):
        self.decl.instantiated_from_member_template = self.other
        self.assertTrue(self.decl.is_instantiated_from_member_template())
        self.assertEqual(self.decl.instantiated_from_member_template,self.other)
    
    def test_should_not_be_member_specialization_by_default(self):
        self.assertFalse(self.decl.is_member_specialization())
    
    def test_cant_be_member_spec_if_not_instantiated_from_member_template(self):
        self.assertRaises(AssertionError,self.decl.set_is_member_specialization)
    
    def test_should_be_member_spec_when_set_and_instantiated_from_member(self):
        self.decl.instantiated_from_member_template = self.other
        self.decl.set_is_member_specialization()
        self.assertTrue(self.decl.is_member_specialization())


if __name__ == "__main__":
    pass
