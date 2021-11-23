from lang.ast import *
from lang.symb_eval import Evaluator
from synthesis.synth import Synthesizer
from verification.verifier import is_valid
import unittest
from lang.paddle import parse
import os
from pathlib import Path

# A smaller limit for the tests.
ITERATIONS_LIMIT = 1000


def main_loop_synth_check(method_num, filename):
    # Parse the input file into an AST
    ast = parse(filename)
    # Intiialize a Synthesizer with it
    synt = Synthesizer(ast)
    # Iterate until a solution is found or iteration limit is reached
    iteration = 0
    while iteration < ITERATIONS_LIMIT:
        iteration += 1
        # At each call of the methods of the synthesizer a new
        # hole completion should be returned.
        if method_num == 3:
            hole_completions = synt.synth_method_3()
        elif method_num == 2:
            hole_completions = synt.synth_method_2()
        else:
            hole_completions = synt.synth_method_1()
        # Evaluate the program with these completions
        evaluator = Evaluator(hole_completions)
        final_constraint_expr = evaluator.evaluate(ast)
        # Verify the program, if it is valid it is a solution!
        if is_valid(final_constraint_expr):
            return True
        # Otherwise the loop continues.
    return False


def testFile(testcase, filename):
    testcase.assertTrue(os.path.exists(filename))
    if not os.path.exists(filename):
        raise Exception(
            "TestSynth is looking for %s, which was in the starter code.\
                 Make sure file exists." % filename)
    r1 = main_loop_synth_check(1, filename)

    testcase.assertTrue(
        r1, msg="Method 1 failed to synthesize a solution for %s." % filename)
    r2 = main_loop_synth_check(2, filename)
    testcase.assertTrue(
        r2, msg="Method 2 failed to synthesize a solution for %s." % filename)
    r3 = main_loop_synth_check(3, filename)
    testcase.assertTrue(
        r3, msg="Method 3 failed to synthesize a solution for %s." % filename)


class TestSynth(unittest.TestCase):

    def test_on_sum_inputs(self,):
        for i in range(2, 4):
            filename = '%s/examples/sum%i.paddle' % (
                Path(__file__).parent.parent.absolute(), i)
            testFile(self, filename)

    def test_on_xor_input(self,):
        filename = '%s/examples/xor.paddle' % Path(
            __file__).parent.parent.absolute()
        testFile(self, filename)

    def test_on_abs_input(self,):
        filename = '%s/examples/abs.paddle' % Path(
            __file__).parent.parent.absolute()
        testFile(self, filename)

    def test_on_even_input(self,):
        filename = '%s/examples/even.paddle' % Path(
            __file__).parent.parent.absolute()
        testFile(self, filename)

    def test_on_odd_input(self,):
        filename = '%s/examples/odd.paddle' % Path(
            __file__).parent.parent.absolute()
        testFile(self, filename)

    def test_on_max_inputs(self,):
        for i in range(2, 3):
            filename = '%s/examples/max%i.paddle' % (
                Path(__file__).parent.parent.absolute(), i)
            testFile(self, filename)
