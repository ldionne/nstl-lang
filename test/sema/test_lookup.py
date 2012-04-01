#!/usr/bin/env python3
"""Test module for the lexical scoped lookup in sema/lookup.py."""

import unittest
from collections import deque
# temporary: until this module gets run via the test suite
import sys
sys.path.append("../../")
from nstl.sema import scope
from nstl.sema.lookup import *


class _DeclName(object):
    """Mock class to simulate a declaration name."""
    pass


class _Decl(object):
    """Mock class to simulate a declaration."""
    pass


class _Environment(object):
    """Mock class to simulate the environment of a resolver.
    
    The environment consists of nested scopes containing declarations.
    
    _scope      The current scope.
    """
    def __init__(self):
        self._scope = scope.Scope()
    
    def declare(self, decl_name, decl):
        """Declare a declaration in the current scope."""
        self._scope.add(decl)
    
    def enter_scope(self):
        """Enter a new scope, setting the current scope as the
           parent scope of the new one."""
        self._scope = scope.Scope(self._scope)
    
    def exit_scope(self):
        """Exit the current scope. The current scope is lost and forgotten."""
        self._scope = self._scope.parent


class _Pair(tuple):
    """A dummy class to make attribute access more legible."""
    @property
    def name(self): return self[0]
    @property
    def decl(self): return self[1]


class _Resolver(Resolver):
    def resolve(self, *args, **kwargs):
        """Abstract away the type of the result of a lookup. The tests
           below only need to know about declarations."""
        return super().resolve(*args, **kwargs)


class TestResolver(unittest.TestCase):
    """Test class for the Resolver class."""
    
    def setUp(self):
        """All tests get a modified resolver instance, a mock environment and
           a list of declaration names with their associated declaration."""
        self.env = _Environment()
        self.res = _Resolver()
        self.decls = [_Pair((_DeclName(), _Decl())) for i in range(5)]
    
    def assertResolve(self, name, decl):
        """Helper method to save some typing."""
        self.assertEqual(list(self.res.resolve(name))[0], decl)
    
    def test_should_fail_to_resolve_inexistant_name(self):
        self.assertRaises(NameNotFoundException, self.res.resolve,
                                                            self.decls[0].name)
    
    def test_should_resolve_declaration_made_in_this_scope(self):
        self.env.declare(*self.decls[0])
        self.assertResolve(*self.decls[0])
    
    def test_should_resolve_declaration_made_in_outer_scope(self):
        self.env.declare(*self.decls[0])
        self.env.enter_scope()
        self.assertResolve(*self.decls[0])
    
    def test_should_not_resolve_declaration_made_in_inner_scope(self):
        self.env.enter_scope()
        self.env.declare(*self.decls[0])
        self.env.exit_scope()
        self.assertRaises(NameNotFoundException, self.res.resolve,
                                                            self.decls[0].name)
    
    def test_should_resolve_shadowed_declarations_in_order(self):
        shadowed = deque()
        name = self.decls[0].name
        for _, decl in self.decls:
            shadowed.appendleft(decl)
            self.env.declare(name, decl)
            self.env.enter_scope()
        
        self.assertListEqual(list(shadowed), list(self.res.resolve(name)))


if __name__ == "__main__":
    unittest.main()
