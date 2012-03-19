#!/usr/bin/env python3


def generate_ast_classes(in_file, out_file):
    from pycparser._ast_gen import ASTCodeGenerator
    gen = ASTCodeGenerator(in_file)
    gen.generate(open(out_file, 'w'))

generate_ast_classes(in_file='nstl_ast.cfg', out_file='_generated_nstl_ast.py')
