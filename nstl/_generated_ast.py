#-----------------------------------------------------------------
# ** ATTENTION **
# This code was automatically generated from the file:
# ast.cfg 
#
# Do not modify it directly. Modify the configuration file and
# run the generator again.
# ** ** *** ** **
#
# pycparser: c_ast.py
#
# AST Node classes.
#
# Copyright (C) 2008-2012, Eli Bendersky
# License: BSD
#-----------------------------------------------------------------


import sys


class Node(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        """ A sequence of all children that are Nodes
        """
        pass

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.
            
            buf:   
                Open IO buffer into which the Node is printed.
            
            offset: 
                Initial offset (amount of leading spaces) 
            
            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.
                
            nodenames:
                True if you want to see the actual node names 
                within their parents.
            
            showcoord:
                Do you want the coordinates of each Node to be
                displayed.
        """
        lead = ' ' * offset
        if nodenames and _my_node_name is not None:
            buf.write(lead + self.__class__.__name__+ ' <' + _my_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__+ ': ')

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            child.show(
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name)


class NodeVisitor(object):
    """ A base NodeVisitor class for visiting c_ast nodes. 
        Subclass it and define your own visit_XXX methods, where
        XXX is the class name you want to visit with these 
        methods.
        
        For example:
        
        class ConstantVisitor(NodeVisitor):
            def __init__(self):
                self.values = []
            
            def visit_Constant(self, node):
                self.values.append(node.value)

        Creates a list of values of all the constant nodes 
        encountered below the given node. To use it:
        
        cv = ConstantVisitor()
        cv.visit(node)
        
        Notes:
        
        *   generic_visit() will be called for AST nodes for which 
            no visit_XXX method was defined. 
        *   The children of nodes for which a visit_XXX was 
            defined will not be visited - if you need this, call
            generic_visit() on the node. 
            You can use:
                NodeVisitor.generic_visit(self, node)
        *   Modeled after Python's own AST visiting facilities
            (the ast module of Python 3.0)
    """
    def visit(self, node):
        """ Visit a node. 
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        """ Called if no explicit visitor function exists for a 
            node. Implements preorder visiting of the node.
        """
        for c_name, c in node.children():
            self.visit(c)


class Program(Node):
    def __init__(self, defs, coord=None):
        self.defs = defs
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.defs or []):
            nodelist.append(("defs[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Namespace(Node):
    def __init__(self, name, members, coord=None):
        self.name = name
        self.members = members
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.members or []):
            nodelist.append(("members[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Template(Node):
    def __init__(self, name, params, body, coord=None):
        self.name = name
        self.params = params
        self.body = body
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        for i, child in enumerate(self.body or []):
            nodelist.append(("body[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Import(Node):
    def __init__(self, templates, coord=None):
        self.templates = templates
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.templates or []):
            nodelist.append(("templates[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Parameter(Node):
    def __init__(self, keyword, default, coord=None):
        self.keyword = keyword
        self.default = default
        self.coord = coord

    def children(self):
        nodelist = []
        if self.keyword is not None: nodelist.append(("keyword", self.keyword))
        if self.default is not None: nodelist.append(("default", self.default))
        return tuple(nodelist)

    attr_names = ()

class ParameterId(Node):
    def __init__(self, name, params, coord=None):
        self.name = name
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name','params',)

class Raw(Node):
    def __init__(self, input, coord=None):
        self.input = input
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('input',)

class ScopeOp(Node):
    def __init__(self, outer, inner, coord=None):
        self.outer = outer
        self.inner = inner
        self.coord = coord

    def children(self):
        nodelist = []
        if self.outer is not None: nodelist.append(("outer", self.outer))
        if self.inner is not None: nodelist.append(("inner", self.inner))
        return tuple(nodelist)

    attr_names = ()

class CallOp(Node):
    def __init__(self, name, args, coord=None):
        self.name = name
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.args or []):
            nodelist.append(("args[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Argument(Node):
    def __init__(self, value, keyword, coord=None):
        self.value = value
        self.keyword = keyword
        self.coord = coord

    def children(self):
        nodelist = []
        if self.value is not None: nodelist.append(("value", self.value))
        if self.keyword is not None: nodelist.append(("keyword", self.keyword))
        return tuple(nodelist)

    attr_names = ()

class Identifier(Node):
    def __init__(self, name, coord=None):
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('name',)

