
from ._generated_ast import *


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



if __name__ == "__main__":
    pass
