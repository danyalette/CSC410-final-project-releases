"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file contains some tests of enumeration.
"""

import unittest
from typing import Mapping
from lang.ast import *
from lang import paddle
from pathlib import Path
from synthesis.synth import Synthesizer
import os


def check_well_formed(prog: Program, hole_map: Mapping[str, Expression]) -> bool:
    """
        Checks that a hole completion is well-formed:
        - the hole completion should be a dictionary with keys: hole ids and data: Expressions.
        - each key of the dictionary should be a string,
        - each value should be an Expression
        - each Expression should be pure, that is, there is no grammar symbol left in it, and there
            is no grammar expression left in it.
    """
    if not isinstance(prog, Program):
        return False
    if not isinstance(hole_map, dict):
        return False
    for hole_id, hole_completion in hole_map.items():
        # the keys should be strings
        if not isinstance(hole_id, str):
            return False
        # the data should be an expression
        if not isinstance(hole_completion, Expression):
            return False
        # the expression should be "pure", i.e not contain
        # any GrammarVar or GrammarInteger
        if not prog.is_pure_expression(hole_completion):
            return False

    return True


class TestEnumerator(unittest.TestCase):
    def test_interface_present(self):
        synth_method_names = ["synth_method_1",
                              "synth_method_2", "synth_method_3"]
        for mname in synth_method_names:
            m1_exists = hasattr(Synthesizer, mname) and callable(
                getattr(Synthesizer, mname))

        self.assertTrue(
            m1_exists, msg=f"Make sure the {mname} method in Evaluator is implemented.")

    def test_enumerate(self):
        base_path = Path(
            __file__).parent.parent.absolute()
        examples_directory = f"{base_path}/examples"
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                path = os.path.join(examples_directory, filename)
                ast = None
                try:
                    ast = paddle.parse(path)
                except:
                    # In order to see the name of the malformed file in this test output:
                    self.assertFalse(True, f"Failed parsing file {filename}")
                # Initialize a Synthesizer
                s = Synthesizer(ast)
                # Check the well-formedness of all the expressions
                prev_h1 = None
                prev_h2 = None
                prev_h3 = None
                for _ in range(0, 10):
                    # Call all the methods : 1, 2 and 3
                    try:
                        synth_h1 = s.synth_method_1()
                        synth_h2 = s.synth_method_2()
                        synth_h3 = s.synth_method_3()
                    except:
                        # There might be no next program. In that case, just continue.
                        continue

                    # The map returned should be different from the previous one.
                    self.assertFalse(synth_h1 == prev_h1 or synth_h2 == prev_h2 or synth_h3 == prev_h3,
                                     msg="The synth_method_i should return a new program at every call.")
                    # Check that all the maps are well-formed, according to the checkwf function.
                    self.assertTrue(check_well_formed(ast, synth_h1),
                                    msg="The synth_method should return well-formed maps from hole ids to expressions.")
                    self.assertTrue(check_well_formed(ast, synth_h2),
                                    msg="The synth_method should return well-formed maps from hole ids to expressions.")
                    self.assertTrue(check_well_formed(ast, synth_h3),
                                    msg="The synth_method should return well-formed maps from hole ids to expressions.")
                    # Update the prev variables.
                    prev_h1 = synth_h1
                    prev_h2 = synth_h2
                    prev_h3 = synth_h3

            else:
                continue
