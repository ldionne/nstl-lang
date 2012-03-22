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
    def __init__(self, decls, coord=None):
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Namespace(Node):
    def __init__(self, name, decls, coord=None):
        self.name = name
        self.decls = decls
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.decls or []):
            nodelist.append(("decls[%d]" % i, child))
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
        if self.body is not None: nodelist.append(("body", self.body))
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class ParameterDeclaration(Node):
    def __init__(self, name, default, coord=None):
        self.name = name
        self.default = default
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.default is not None: nodelist.append(("default", self.default))
        return tuple(nodelist)

    attr_names = ()

class ParameterIdentifier(Node):
    def __init__(self, name, params, coord=None):
        self.name = name
        self.params = params
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.params or []):
            nodelist.append(("params[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class CompoundStatement(Node):
    def __init__(self, stmnts, coord=None):
        self.stmnts = stmnts
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.stmnts or []):
            nodelist.append(("stmnts[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class NestStatement(Node):
    def __init__(self, refs, args, coord=None):
        self.refs = refs
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.refs or []):
            nodelist.append(("refs[%d]" % i, child))
        for i, child in enumerate(self.args or []):
            nodelist.append(("args[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class ImportStatement(Node):
    def __init__(self, refs, args, coord=None):
        self.refs = refs
        self.args = args
        self.coord = coord

    def children(self):
        nodelist = []
        for i, child in enumerate(self.refs or []):
            nodelist.append(("refs[%d]" % i, child))
        for i, child in enumerate(self.args or []):
            nodelist.append(("args[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class ArgumentExpression(Node):
    def __init__(self, name, value, coord=None):
        self.name = name
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        if self.value is not None: nodelist.append(("value", self.value))
        return tuple(nodelist)

    attr_names = ()

class RawExpression(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('value',)

class QualifiedIdentifier(Node):
    def __init__(self, quals, name, coord=None):
        self.quals = quals
        self.name = name
        self.coord = coord

    def children(self):
        nodelist = []
        if self.name is not None: nodelist.append(("name", self.name))
        for i, child in enumerate(self.quals or []):
            nodelist.append(("quals[%d]" % i, child))
        return tuple(nodelist)

    attr_names = ()

class Identifier(Node):
    def __init__(self, value, coord=None):
        self.value = value
        self.coord = coord

    def children(self):
        nodelist = []
        return tuple(nodelist)

    attr_names = ('value',)

