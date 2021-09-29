from lang.symb_eval import Evaluator
from lang.ast import *
from verification.verifier import is_valid
import unittest
from lang.paddle import parse
from lark import exceptions
import os
from pathlib import Path


class TestVerif(unittest.TestCase):
    def test_verif_examples(self):
        examples_directory = '%s/examples/verification' % Path(
            __file__).parent.parent.absolute()
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                filename = os.path.join(examples_directory, filename)
                # Parse
                try:
                    ast = parse(filename)
                except:
                    self.assertFalse(
                        True, "Exception was raised when parsing %s" % filename)
                # Evaluate from empty
                try:
                    ev = Evaluator({})
                    final_constraint_expr = ev.evaluate(ast)
                except:
                    self.assertFalse(
                        True, "Exception was raised when parsing %s" % filename)
                # Verify
                try:
                    # Paddle names ending with false.paddle are expected to be incorrect.
                    if filename.endswith("false.paddle"):
                        self.assertFalse(is_valid(final_constraint_expr))
                    else:
                        self.assertTrue(is_valid(final_constraint_expr))
                except:
                    self.assertFalse(
                        True, "Exception was raised when verifying %s" % filename)

            else:
                continue
