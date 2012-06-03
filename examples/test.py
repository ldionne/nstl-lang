#!/usr/bin/env python3

import sys
import os
sys.path.extend(["/Users/louisdionne/Documents/Ordi/nstl-lang"])

from nstl import compile


compiler = compile.Compiler()
all_files_to_process = (file for file in os.listdir('inputs') if file.endswith('nstl'))
inputs = " ".join([os.path.join('inputs', file) for file in all_files_to_process])
argv = "-f -o test-env {}".format(inputs).split()
compiler.compile(argv)
