"""Test module for the TemplateDecl class of ast/decltemplate.py."""

import unittest
from nstl.ast.decltemplate import TemplateDecl


class _TemplateParams(list):
    """Mock class representing a list of template parameters."""
    
    pass


class _NamedDecl(object):
    """Mock class representing a named declaration to be
       used as a templated declaration."""
    
    pass


class TestTemplateDecl(unittest.TestCase):
    """Test class for the TemplateDecl class."""
    
    def setUp(self):
        """All tests get a list of template parameters, a TemplateDecl instance
           using these parameters and the underlying templated declaration."""
        self.params = _TemplateParams()
        self.templated = _NamedDecl()
        self.decl = TemplateDecl(self.templated, self.params, 'foo', None)
    
    def test_should_provide_its_template_parameters(self):
        self.assertEqual(self.params, self.decl.params)
    
    def test_should_provide_right_underlying_templated_decl(self):
        self.assertEqual(self.templated, self.decl.templated_decl)


if __name__ == "__main__":
    pass
