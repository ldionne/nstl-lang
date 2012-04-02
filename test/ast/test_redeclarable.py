"""Test module for ast/redeclarable.py."""

import unittest
from nstl.ast.redeclarable import Redeclarable


class TestRedeclarable(unittest.TestCase):
    """Test class for the Redeclarable class."""
    
    def setUp(self):
        """All tests get a single and a list of redeclarables."""
        self.decl = Redeclarable()
        self.decls = [Redeclarable() for i in range(5)]
    
    def test_should_have_no_next_when_alone(self):
        self.assertEqual(None, self.decl.next)
    
    def test_should_have_no_previous_when_alone(self):
        self.assertEqual(None, self.decl.previous)
    
    def test_should_be_equal_to_last_when_alone(self):
        self.assertEqual(self.decl, self.decl.last)
    
    def test_should_be_equal_to_first_when_alone(self):
        self.assertEqual(self.decl, self.decl.first)
    
    def test_should_be_last_when_alone(self):
        self.assertTrue(self.decl.is_last())
    
    def test_should_be_first_when_alone(self):
        self.assertTrue(self.decl.is_first())
    
    def test_should_be_previous_of_next(self):
        self.decls[0].redeclare_with(self.decls[1])
        self.assertEqual(self.decls[0], self.decls[1].previous)
    
    def test_should_be_next_of_previous(self):
        self.decls[0].redeclare_with(self.decls[1])
        self.assertEqual(self.decls[0].next, self.decls[1])
    
    def test_should_be_last_when_declared_last(self):
        for i, decl in enumerate(self.decls[:-1]):
            decl.redeclare_with(self.decls[i+1])
        self.assertTrue(self.decls[-1].is_last())
    
    def test_should_be_first_when_declared_first(self):
        for i, decl in enumerate(self.decls[:-1]):
            decl.redeclare_with(self.decls[i+1])
        self.assertTrue(self.decls[0].is_first())


if __name__ == "__main__":
    pass
