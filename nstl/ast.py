
import sys
from collections import OrderedDict



def isiterable(obj):
    try:
        (e for e in obj)
        return True
    except TypeError:
        return False

def unzip(iterable):
    return tuple(zip(*iterable))

class AttributeBucket(OrderedDict):
    def __getattribute__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return super().__getattribute__(attr)
    
    
    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            super().__setattr__(attr, value)
        else:
            self[attr] = value



def EzNode(children=None, attrs=None):
    def decorator(cls):
        class generated(Node):
            if children or attrs:
                def __init__(self, **kwargs):
                    super().__init__()
                    default = self.a if attrs is None else self.c
                    for attr, value in kwargs.items():
                        if children and attr in children:
                            setattr(self.c, attr, Nodelist(value)
                                            if isiterable(value) else value)
                        else:
                            setattr(self.a if attrs and attr in attrs
                                            else default, attr, value)
        
        for attr, value in cls.__dict__.items():
            if attr == '__init__':
                raise ValueError(
                    "can't overwrite __init__ when using the EzNode decorator")
            elif not attr in ('__dict__', '__doc__'):
                setattr(generated, attr, value)
        generated.__name__ = cls.__name__
        return generated
    return decorator



class Node(object):
    def __init__(self):
        super().__setattr__("a", AttributeBucket())
        super().__setattr__("c", AttributeBucket())
    
    
    def __getattribute__(self, attr):
        get = super().__getattribute__
        try:
            return get(attr)
        except AttributeError:
            a = get("a")
            if hasattr(a, attr):
                return getattr(a, attr)
            
            c = get("c")
            if hasattr(c, attr):
                return getattr(c, attr)
            
            raise
    
    
    def __setattr__(self, attr, value):
        if isinstance(value, (Node, Nodelist)):
            setattr(self.c, attr, value)
        else:
            setattr(self.a, attr, value)
    
    
    def children(self):
        nodes = [ ]
        for attr, value in self.c.items():
            if value is not None:
                nodes.append((attr, value))
        return tuple(nodes)
    
    
    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False,
                                                        _this_node_name=None):
        lead = ' ' * offset
        if nodenames and _this_node_name is not None:
            buf.write(lead + self.__class__.__name__ + ' <' + _this_node_name + '>: ')
        else:
            buf.write(lead + self.__class__.__name__+ ': ')
        
        
        if self.a:
            if attrnames:
                attrstr = ', '.join("=".join((n, str(v))) for n, v in self.a.items())
            else:
                attrstr = ', '.join(str(v) for v in self.a.values())
            buf.write(attrstr)
        
        buf.write('\n')
        
        for child_name, child in self.children():
            child.show(buf, offset + 4, attrnames, nodenames, child_name)



class Nodelist(list):
    def show(self, *args, **kwargs):
        for node in self:
            node.show(*args, **kwargs)
    
    def children(self):
        nodes = [ ]
        
        class assert_not_used(object):
            def __str__(self):
                assert False
        
        for node in self:
            nodes.append((assert_not_used(), node))
        return tuple(nodes)



class NodeVisitor(object):
    def visit(self, node, *args, **kwargs):
        if not isinstance(node, (Node, Nodelist)):
            import pdb
            pdb.set_trace()
            raise TypeError("can't visit a node that is not a subclass of Node")
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args, **kwargs)
    
    
    def generic_visit(self, node, *args, **kwargs):
        for child_name, child in node.children():
            self.visit(child, *args, **kwargs)



class NodeTransformer(NodeVisitor):
    def visit(self, node, *args, **kwargs):
        if isinstance(node, Nodelist):
            return Nodelist(self.visit(n, *args, **kwargs) for n in node)
        else:
            return super().visit(node, *args, **kwargs)
    
    
    def generic_visit(self, node, *args, **kwargs):
        for child_name, child in node.children():
            setattr(node, child_name, self.visit(child, *args, **kwargs))
        return node



class Program(Node):
    """
    decls   sequence of declarations
    """
    def __init__(self, decls):
        super().__init__()
        self.c.decls = Nodelist(decls)

class Namespace(Node):
    """
    name    identifier
    decls   sequence of declarations
    """
    def __init__(self, name, decls):
        super().__init__()
        self.c.name = name
        self.c.decls = Nodelist(decls)

class Template(Node):
    """
    name    identifier
    params  list of parameter declarations
    body    compound statement
    """
    def __init__(self, name, params, body):
        super().__init__()
        self.c.name = name
        self.c.params = Nodelist(params)
        self.c.body = body

class ParameterDeclaration(Node):
    """
    name        parameter identifier
    default     expression or None (default argument)
    """
    def __init__(self, name, default):
        super().__init__()
        self.c.name = name
        self.c.default = default

class ParameterIdentifier(Node):
    """
    name    string                  --> name of the C macro
    params  list of strings or None --> parameters to the C macro
    """
    def __init__(self, value, params):
        super().__init__()
        self.a.value = value
        self.a.params = params

class CompoundStatement(Node):
    """
    stmnts  sequence of statements
    """
    def __init__(self, stmnts):
        super().__init__()
        self.c.stmnts = Nodelist(stmnts)

class NestStatement(Node):
    """
    ref     a qualified or unqualified identifier
    args    list of argument expressions
    """
    def __init__(self, ref, args):
        super().__init__()
        self.c.ref = ref
        self.c.args =  Nodelist(args)

class ImportStatement(Node):
    """
    refs    list of qualified or unqualified identifiers
    args    list of argument expressions
    """
    def __init__(self, refs, args):
        super().__init__()
        self.c.refs = Nodelist(refs)
        self.c.args = Nodelist(args)

class ArgumentExpression(Node):
    """
    name    parameter identifier --> named keyword argument
    value   expression
    """
    def __init__(self, name, value):
        super().__init__()
        self.c.name = name
        self.c.value = value

class RawExpression(Node):
    """
    value   raw string input
    """
    def __init__(self, value):
        super().__init__()
        self.a.value = value

class QualifiedIdentifier(Node):
    """
    name    unqualified identifier
    quals   list of identifiers that are qualifiers (nested namespace names)
    """
    def __init__(self, quals, name):
        super().__init__()
        self.c.quals = Nodelist(quals)
        self.c.name = name

class Identifier(Node):
    """
    value   string value of the identifier
    """
    def __init__(self, value):
        super().__init__()
        self.a.value = value



if __name__ == "__main__":
    pass
