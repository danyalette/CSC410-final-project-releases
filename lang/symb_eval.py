"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file defines the Evaluator class, which is used to do symbolic
evaluation of an expression.
"""
from typing import Mapping
from lang.ast import *


class EvaluationTypeError(TypeError):
    """
    TypeError that is raised during symbolic evaluation.
    """


class EvaluationUndefinedHoleError(KeyError):
    """
    TypeError that is raised during symbolic evaluation
    that is due to an undefined hole.
    """


class Evaluator():
    """
    An Evaluator can be used to symbolically evaluate an expression.
    An Evaluator should be initialized with a map from hole name to
    the expression of the hole.
    """

    def __init__(self, hole_defs: Mapping[str, Expression]) -> None:
        """
        @param hole_defs A Mapping from string to expression, meant to be used
        to replace a hole variable by its definition.
        """
        self.hole_defs = hole_defs

    def evaluate_expr(self, var_defs: Mapping[str, Expression],
                      ex: Expression) -> Expression:
        """
        The evaluate_expr symbolically evaluates the expression ex
        in the environment var_defs.
        @param var_defs A Mapping from string to expression, meant to
        be used as the definition of the environment.
        @param ex The expression to evaluate.
        """
        result = None

        # Case 1 : ex is a binary expression.
        if isinstance(ex, BinaryExpr):
            operator = ex.operator
            lhs = ex.left_operand
            rhs = ex.right_operand
            # TODO: Do something with op, lhs and rhs...
            # op = ...
            # lhs = ...
            # rhs = ...
            result = BinaryExpr(operator, lhs, rhs)

        # Case 2 : ex is a unary expression.
        elif isinstance(ex, UnaryExpr):
            operator = ex.operator
            operand = ex.operand
            # TODO: Do something with op and ope...
            # op = ...
            # operand = ...
            result = UnaryExpr(operator, operand)

        # Case 3 : ex is a if-then-else expression (a ternary expression).
        elif isinstance(ex, Ite):
            cond = ex.cond
            true_branch = ex.true_br
            false_branch = ex.false_br
            # TODO: Do something with cond, true_branch and false_branch
            # cond = ...
            # true_branch = ...
            # false_branch = ...
            result = Ite(cond, true_branch, false_branch)

        # Case 4: ex is a variable
        elif isinstance(ex, VarExpr):
            if ex.var.name in var_defs:
                # TODO: what do we return if var has a definition?
                result = None
            elif ex.var.name in self.hole_defs:
                # TODO: what do we return if var is a hole?
                result = None
            else:
                # If a variable has no definition and is not a hole
                # (.e.g it's an input), then it is unchanged.
                result = ex

        # Case 5 : ex i a boolean constant
        elif isinstance(ex, (BoolConst, IntConst)):
            result = ex

        # Case 6 : ex is GrammarInteger or GramamrVar: this should
        # never happen during evaluation!
        elif isinstance(ex, (GrammarInteger, GrammarVar)):
            raise EvaluationTypeError(
                "GrammarInteger and GrammarVar should not appear in\
                  expressions that are evaluated.")

        # Case 7 should never be reached.
        elif isinstance(ex, Expression):
            raise EvaluationTypeError(
                "Argument is an Expression of unknown type!\n\
                 Maybe you forgot to implement a case in \
                     symb_eval.Evaluator.evaluate_expr")

        return result

    def check_holes_have_defs(self, prog: Program) -> None:
        """
        Check that all of the program's holes have been defined.
        """
        hole_names = [hole_def.var.name for hole_def in prog.holes]
        for hole_name in hole_names:
            if hole_name not in self.hole_defs:
                raise EvaluationUndefinedHoleError(
                    f"Evaluator should define the hole {hole_name}")

    def evaluate(self, prog: Program) -> Expression:
        """
        Evaluate performs a few checks and then evaluates
        the assignments.
        """
        #
        try:
            self.check_holes_have_defs(prog)
        except EvaluationUndefinedHoleError as exception:
            # Optionally, do something with this info...
            raise exception
        # Initially, the environment is empty since no variables are
        # defined.
        environment = {}
        for assignment in prog.assignments:
            # For each assignment, first evaluate the expression with
            # the current environment,
            expr = self.evaluate_expr(environment, assignment.expr)
            # and then update the environment with that expression for
            # the assigned variable.
            environment[assignment.var.name] = expr
        # Finally, return the evaluated constraint once all assignments
        # have been evaluated.
        # At the end of evaluation, the expression returned should only
        # contain variables that are defined as input.
        return self.evaluate_expr(environment, prog.constraint)
