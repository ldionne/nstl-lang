#!/usr/bin/env python3
"""Script to run all the tests for nstl."""

import unittest
import os


suite = unittest.TestLoader().discover(os.path.join(os.pardir, "test"),
                                                    top_level_dir=os.pardir)
unittest.TextTestRunner(verbosity=1).run(suite)
