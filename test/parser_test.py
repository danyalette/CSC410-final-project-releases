"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file contains tests for the Paddle parser.
"""

from lark.exceptions import VisitError, UnexpectedEOF, UnexpectedCharacters
from lang.transformer import TransformerVariableException
import unittest
import os
import re
from pathlib import Path
from lang import paddle

RE_STRIP = re.compile(r"\s+")


class TestParser(unittest.TestCase):
    """
    TestParser class contains the all the parsing tests.
    """

    def test_parse_all_examples(self):
        """ Collect all files in the examples directory
        and try parsing them.
        """
        base_path = Path(__file__).parent.parent.absolute()
        examples_directory = f"{base_path}/examples"
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                path = os.path.join(examples_directory, filename)
                try:
                    paddle.parse(path)
                except:
                    # In order to see the name of the malformed file in this test output:
                    self.assertFalse(True, f"Failed parsing file {filename}")
            else:
                continue

    def test_precedence1(self):
        """ Test precedence of > and &&. """
        constraint = paddle.parse(
            string="assert 1 > 2 && 3;").constraint
        self.assertEqual(str(constraint), "((1 > 2) && 3)")

    def test_precedence2(self):
        """ Test precedence of * and =. """
        constraint = paddle.parse(
            string="assert 1 * 2 = 3 * 4;").constraint
        self.assertEqual(str(constraint), "((1 * 2) = (3 * 4))")

    def test_precedence3(self):
        """ Test precedence of + and *. """
        constraint = paddle.parse(
            string="assert 1 + 2 * 3;").constraint
        self.assertEqual(str(constraint), "(1 + (2 * 3))")

    def test_precedence4(self):
        """ Test precedence in a complex expression. """
        constraint = paddle.parse(
            string="assert 1 + 2 * 3 + 4 >= 5 * 6 + 7 * 8;").constraint
        self.assertEqual(
            str(constraint), "((1 + ((2 * 3) + 4)) >= ((5 * 6) + (7 * 8)))")

    def test_precedence5(self):
        """ Test precedence in a complex expression. """
        constraint = paddle.parse(
            string="assert 0 * 1 * 2 > 3 + 4 && 5 + 6\
             <= 7 * 8 + 9 + 10 + 11;").constraint
        self.assertEqual(str(
            constraint), "((((0 * 1) * 2) > (3 + 4)) && "
            "((5 + 6) <= ((7 * 8) + (9 + (10 + 11)))))")

    def test_precedence_mul_assoc_left(self):
        """ Test that * is associates from left to right. """
        constraint = paddle.parse(
            string="assert 0 * 1 * 2;").constraint
        self.assertEqual(str(
            constraint), "((0 * 1) * 2)")

    def test_precedence_add_assoc_right(self):
        """ Test that + associates from right to left. """
        constraint = paddle.parse(
            string="assert 0 + 1 + 2;").constraint
        self.assertEqual(str(
            constraint), "(0 + (1 + 2))")

    def test_now_input_names(self):
        """Test that parser can parse input names that of various formatting."""
        names = ["a_longish_snake_case_name", "this_is_really_a_very_long_name_yes_this_is_really"
                 "_a_very_long_name_indeed",
                 "this_name_Shares_123NUMBERS_andCASEetc", "etc534", "_33", "_", "OK", "ASDFGHJKLZX78789"]
        for name in names:
            program = paddle.parse(
                string=f"input {name} : int; assert {name} = True;"
            )
            self.assertEqual({var.name for var in program.declares()}, {name})

    def test_now_input_bad_names(self):
        """Test that parser fails on bad input names."""
        names = ["123", "#ghjk_4", "&", "_&", "hello_1@", "a_longish_snake_case_name)", "\"", "s%", ":", "name'"]
        for name in names:
            self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
                string=f"input {name} : int; assert {name} = True;"
            ))

    def test_now_needs_assert1(self):
        """Test that not including assert raises error."""
        self.assertRaises(UnexpectedEOF, lambda: paddle.parse(
            string="hole a_hole: int [ \
                G: int -> Var ] "
        ))

    def test_now_needs_assert2(self):
        """Test that not including assert raises error."""
        self.assertRaises(UnexpectedEOF, lambda: paddle.parse(
            string="define hello : int = 0;"
        ))

    def test_now_needs_assert3(self):
        """Test that not including assert raises error."""
        self.assertRaises(UnexpectedEOF, lambda: paddle.parse(
            string="input hello : int;"
        ))

    def test_now_parse_undefined_raises(self):
        """Test that using undefined var raises error."""
        self.assertRaises((TransformerVariableException, VisitError), lambda: paddle.parse(
            string="input x : int;\
                assert (y = True);"
        ))
        self.assertRaises((TransformerVariableException, VisitError), lambda: paddle.parse(
            string="input x : int;\
                assert (x && y);"
        ))
        self.assertRaises((TransformerVariableException, VisitError), lambda: paddle.parse(
            string="input x : int;\
                assert (x && y);"
        ))
        self.assertRaises((TransformerVariableException, VisitError), lambda: paddle.parse(
            string="input x : int;\
                define y : int = q;\
                assert True;"
        ))

    def test_now_input_does_not_define(self):
        """Test that an input is not assigned a value."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="input x : bool = True; input y : int; assert True; "
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="input an_input : int = 48; assert an_input; "
        ))

    def test_now_hole_does_not_define(self):
        """Test that a hole is not assigned a value."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole aHole23 : int = 48; assert aHole23; "
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole another_hole : bool [G : int -> G] = 22; assert another_hole = 10; "
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole h1 : int [X : int -> Integer]; hole another_hole : \
                bool [G : int -> G] = 22; assert another_hole = 10;"
        ))

    def test_now_order_of_program_statements(self):
        """Test that program has parse error when program statements appear in the wrong order."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="assert True; input x : int;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="input x : bool; assert True; input x : int;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="assert True; define x : bool = True;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define x : bool = True; input y : int; assert True; "
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole z : int [K : bool -> Var]; input y : int; assert True; "
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define xVar : int = aHoleName; hole aHoleName : bool [B : bool -> B | Var]; assert True; "
        ))

    def test_now_semi_colon_pos(self):
        """Test that a semi-colon may only appear in the designated places. """
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="assert ;;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="assert True ;;"
        ))
        self.assertRaises((UnexpectedCharacters, VisitError), lambda: paddle.parse(
            string="define x : bool = ; assert True;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="; assert True;"
        ))
        self.assertRaises((UnexpectedCharacters, VisitError), lambda: paddle.parse(
            string="assert True &&;"
        ))

    def test_now_types_int_or_bool(self):
        """Test that types other than int or bool raise a parse error."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="input l : list; assert (1 = 2);"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole l : bool [G : unknown -> G | G && G]; assert (True && False);"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="input ok : int; define q : not_a_type = 12; assert ok;"
        ))

    def test_now_grammar_not_empty(self):
        """Test that grammar is not empty and does not contain empty rules."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole h1 : int; assert True;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole hole10 : int []; assert hole10;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole aHole : int [ G : int]; assert 0 < 0;"
        ))
        self.assertRaises((UnexpectedCharacters, VisitError), lambda: paddle.parse(
            string="hole aHole : int [ G : int -> ]; assert 0 < 0;"
        ))
        self.assertRaises((UnexpectedCharacters, VisitError), lambda: paddle.parse(
            string="hole aHole : int [ G : int -> ;]; assert 0 < 0;"
        ))
        self.assertRaises((UnexpectedCharacters, VisitError), lambda: paddle.parse(
            string="hole aHole : int [ G : int -> G; B : bool -> B | ]; assert 0 < 0;"
        ))

    def test_now_bad_binary_operators(self):
        """Test that bad binary operators cause a parse error."""
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define y : int = 10 $ 1; assert False;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define y : int = 10 ^ 10; assert False;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define y : int = 10 and 1; assert False;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="define y : bool = 10 or 1; assert False;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="hole aHole : int [ G : int -> G @ 1]; assert 0 < 0;"
        ))
        self.assertRaises(UnexpectedCharacters, lambda: paddle.parse(
            string="assert 10 10;"
        ))
