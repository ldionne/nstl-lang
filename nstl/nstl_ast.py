
from ._generated_nstl_ast import *


def augment(cls):
    augmented = globals()[cls.__name__]
    must_be_augmented = lambda a: a.startswith("augment_")
    for attr in dir(cls):
        if must_be_augmented(attr):
            setattr(augmented, attr[len("augment_"):], getattr(cls, attr))
    return augmented



@augment
class NodeVisitor(object):
    def augment_visit(self, node, *args, **kwargs):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args, **kwargs)
    
    def augment_passon(self, node, *args, **kwargs):
        return self.generic_visit(node, *args, **kwargs)
    
    def augment_generic_visit(self, node, *args, **kwargs):
        for child_name, child in node.children():
            self.visit(child, *args, **kwargs)



class NodeAccumulator(NodeVisitor):
    def generic_visit(self, node, *args, **kwargs):
        if node is None:
            return ""
        return ("".join(self.visit(child, *args, **kwargs)
                                    for child_name, child in node.children()))



@augment
class Parameter(object):
    def augment_hasdefault(self):
        return self.default is not None



@augment
class Argument(object):
    def augment_haskeyword(self):
        return self.keyword is not None
    
    def augment___str__(self):
        if self.haskeyword():
            return str(self.keyword) + "=" + str(self.value)
        return "<positional argument> = " + str(self.value)



@augment
class ParameterId(object):
    def augment_hasparams(self):
        return self.params is not None
    
    def augment___str__(self):
        return self.name + ("(" + ", ".join(self.params) + ")"
                                                if self.hasparams() else "")



@augment
class Template(object):
    def augment___str__(self):
        strparams = map(str, self.params)
        return "template " + self.name + "(" + ", ".join(strparams) + ")"



@augment
class ScopeOp(object):
    def augment___str__(self):
        return ".".join(map(str, (self.outer, self.inner)))



@augment
class CallOp(object):
    def augment___str__(self):
        return str(self.name) + "(" + ", ".join(map(str, self.args)) + ")"



@augment
class Identifier(object):
    def augment___str__(self):
        return self.name



@augment
class Raw(object):
    def augment___str__(self):
        return self.input



if __name__ == "__main__":
    pass
