from .. import ast

import os
import itertools



class Path(object):
    def __init__(self, value, parent=None):
        if not (isinstance(parent, Path) or parent is None):
            raise TypeError(
                    "the parent of a path must either be a Path object or None")
        self.value = value
        self._parent = parent
    
    
    def xgetpath(self):
        yield self
        parent = self._parent
        while parent is not None:
            yield parent
            parent = parent._parent
    
    
    def getpath(self):
        return list(self.xgetpath())
    
    
    def __str__(self):
        reversed_path = list(str(p.value) for p in self.xgetpath())
        return os.sep.join(reversed(reversed_path))



class Current(Path):
    """Encodes the concept of the current position in a path.
    For example, this would be represented as "." in Unix systems.
    """
    def __init__(self, parent=None):
        super().__init__(os.curdir, parent)



class Backtrack(Path):
    """Encodes the concept of going back in a path.
    For example, this would be represented as ".." in Unix systems.
    """
    def __init__(self, i=1, parent=None):
        super().__init__(os.pardir, parent)
        self.i = i
    
    
    def xgetpath(self):
        for pseudo_parent in itertools.repeat(self, self.i):
            yield pseudo_parent
        
        parents = super().xgetpath()
        next(parents) # Skip ourselves, already included above
        for parent in parents:
            yield parent



class PathBuilder(ast.NodeTransformer):
    def visit_Namespace(self, node, parent=None):
        node.a.path = Path(node.name.value, parent)
        return self.generic_visit(node, node.path)
    
    
    def visit_Template(self, node, parent=None):
        node.a.path = Path(node.name.value, parent)
        return self.generic_visit(node, parent)


