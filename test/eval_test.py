from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator
from lang.ast import *
import unittest
from random import randint
from lang.paddle import parse
from lark import exceptions
from lang.transformer import TransformerVariableException
import os
from pathlib import Path


class TestEval(unittest.TestCase):
    def test_interface_present(self):
        eval_mname = "evaluate"
        eval_expr_mname = "evaluate_expr"
        evaluate_exists = hasattr(Evaluator, eval_mname) and callable(
            getattr(Evaluator, eval_mname))
        evaluate_expr_exists = hasattr(Evaluator, eval_expr_mname) and callable(
            getattr(Evaluator, eval_expr_mname))
        self.assertTrue(
            evaluate_exists, msg="Make sure the %s method in Evaluator is implemented." % eval_mname)
        self.assertTrue(
            evaluate_expr_exists, msg="Make sure the %s method in Evaluator is implemented." % eval_expr_mname)

    def test_example_max2(self):
        filename = '%s/examples/max2.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        # Evaluating this program with no hole definitions should raise an EvaluationUndefinedHoleError
        with self.assertRaises(EvaluationUndefinedHoleError):
            empty.evaluate(prog)
        # Now let's give definitions
        self.assertEqual(len(prog.inputs), 2,
                         msg="In %s, we expected exactly 2 inputs." % filename)
        x = VarExpr(prog.inputs[0])
        y = VarExpr(prog.inputs[1])
        e1 = BinaryExpr(BinaryOperator.GREATER, x, y)
        e2 = Ite(e1, x, y)
        defined = Evaluator({"hmax": e2})
        prog_res = defined.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only two variables in prog_res
        self.assertEqual(len(prog_res.uses()), 2)

    def test_example_mult_to_add_true(self):
        filename = '%s/examples/verification/mult_to_add_true.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only one variable in prog_res
        self.assertEqual(len(prog_res.uses()), 1)
        # Evaluate the expression
        lhs = empty.evaluate_expr({"x": IntConst(0)}, prog_res.left_operand)
        rhs = empty.evaluate_expr({"x": IntConst(0)}, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

    def test_example_mult_to_add_false(self):
        filename = '%s/examples/verification/mult_to_add_false.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only one variable in prog_res
        self.assertEqual(len(prog_res.uses()), 1)
        # Evaluate the expression
        lhs = empty.evaluate_expr({"x": IntConst(1)}, prog_res.left_operand)
        rhs = empty.evaluate_expr({"x": IntConst(1)}, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        # They should be different (3 != 4)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))

    def test_example_sum4c(self):
        filename = '%s/examples/verification/sum4c_false.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only 4 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 4)
        # Evaluate the expression
        model = {"x": IntConst(1), "y": IntConst(
            2), "z": IntConst(3), "w": IntConst(4)}
        lhs = empty.evaluate_expr(model, prog_res.left_operand)
        rhs = empty.evaluate_expr(model, prog_res.right_operand)
        # These expressions can be evaluated in Python directly
        # They should be different (3 != 4)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))

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
                    ev.evaluate(ast)
                except:
                    self.assertFalse(
                        True, "Exception was raised when parsing %s" % filename)
            else:
                continue

    def test_eval_examples(self):
        examples_directory = '%s/examples/evaluation' % Path(
            __file__).parent.parent.absolute()
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                filename = os.path.join(examples_directory, filename)
                # Parse
                try:
                    ast: Program = parse(filename)
                except:
                    self.assertFalse(
                        True, "Exception was raised when parsing %s" % filename)
                # Check variables x,y,z,w, b exist
                x = ast.get_var_of_name("x")
                y = ast.get_var_of_name("y")
                z = ast.get_var_of_name("z")
                w = ast.get_var_of_name("w")
                b = ast.get_var_of_name("b")
                self.assertTrue(
                    x is not None and y is not None and z is not None
                    and w is not None and b is not None,
                    msg="The examples in examples/evaluation should have exactly\n\
                        x,y,z and w as integers inputs,\n\
                        and b as boolean input.\n\
                        i.e. they should start with:\n\
                        input x : int;\n\
                        input y : int;\n\
                        input z : int;\n\
                        input b : bool;\n\
                    %s doesn't match that specification." % os.path.basename(filename)
                )

                self.assertIsInstance(
                    ast, Program, msg="ast must be an instance of Program")
                # Evaluate from empty
                try:
                    # Create an evaluator with no hole definitions.
                    # The files in examples/evaluation should not contain any holes.
                    ev = Evaluator({})
                    self.assertIsInstance(
                        ev, Evaluator, msg="ev must be an instance of Evaluator")

                    expr = ev.evaluate(ast)
                    # Expr must be an instance of Expression
                    self.assertIsInstance(
                        expr, Expression, msg="expr must be an instance of Expression")
                    # The expression must also be a pure expression.
                    self.assertTrue(ast.is_pure_expression(expr),
                                    msg="expr must be a pure expression")

                    for i in range(5):
                        model = {
                            "x": IntConst(randint(-5, 5)),
                            "y": IntConst(randint(-5, 5)),
                            "z": IntConst(randint(-5, 5)),
                            "w": IntConst(randint(-5, 5)),
                            "b": BoolConst(randint(-5, 5) >= 0),
                        }

                        # Evaluate expressions
                        e1 = ev.evaluate_expr(model, expr)
                        self.assertTrue(ast.is_pure_expression(
                            e1), msg="Evaluation should return pure expressions")
                        # Attempt Python eval, which may not work
                        b1 = True
                        try:
                            b1 = eval(pythonize(str(e1)))
                        except:
                            # If it doesn't work just set to True
                            b1 = True
                        self.assertTrue(b1, msg="%s should be true." % str(e1))

                except:
                    self.assertFalse(
                        True, "Exception was raised when evaluating %s" % filename)
            else:
                continue
