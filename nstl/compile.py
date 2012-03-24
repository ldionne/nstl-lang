from . import parse
from .passes import *

import os
import argparse


class Compiler(object):
    def __init__(self):
        self.args = argparse.ArgumentParser(description = 
        "Translate files written in the nstl domain specific language to C preprocessor directives."
        )
        
        self.args.add_argument('file', help="The input file to process.")
        self.args.add_argument('-o', default=os.curdir, help="Specify the directory for the output.")
        self.args.add_argument('-f', action='store_true', help="Do not prompt before overwriting files in the output directories.")
    
    
    def compile(self, argv):
        args = self.args.parse_args(argv)
        outputdir = args.o
        
        with open(args.file, 'r') as file:
            input_text = "".join(file)
        
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        os.chdir(outputdir)
        
        parser = parse.NstlParser()
        ast = parser.parse(input_text)
        
        nameres = nameresolve.NameResolver()
        nameres.visit(ast)
        
        pathbuild = pathresolve.PathBuilder()
        pathbuild.visit(ast)
        
        generator = codegen.Generator()
        generator.visit(ast, args.f)



if __name__ == "__main__":
    pass
