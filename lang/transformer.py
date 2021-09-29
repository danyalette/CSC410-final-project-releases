"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file contains the code required to convert a Paddle parse
tree to a Paddle AST.
"""
import sys
from typing import Dict
from itertools import dropwhile, takewhile
from lark import ast_utils, Transformer, v_args
from lang.ast import *


class TransformerException(Exception):
    """
    Exception that is raised during the transformation
    of Paddle parse tree to Paddle AST.
    """


class TransformerVariableException(TransformerException):
    """
    Exception that is raised due to errors in variable creation
    during the transformation of Paddle parse tree to Paddle AST.
    """


def flatten(nested_list):
    """
    Convert a nested list to a flat list.
    """
    if isinstance(nested_list, list):
        if len(nested_list) == 0:
            return nested_list
        return flatten(nested_list[0]) + flatten(nested_list[1:])
    else:
        return [nested_list]


def takedrop(pred, lst):
    """
    Given a predicate pred and a list lst, return a pair of
    lists (fst, snd) such that:
        - lst = fst + snd
        - the first element of snd is the first element of lst
        that does not satify pred.
    """
    fst = list(takewhile(pred, lst))
    snd = list(dropwhile(pred, lst))
    return (fst, snd)


this_module = sys.modules[__name__]


class ToAst(Transformer):
    """
    This class contains methods which are applied in a bottom-up
    fashion to a Paddle parse tree in order to convert the
    parse tree to a Paddle AST.
    The lark parsing library applies the methods of this class
    according to the names of the corresponding nodes in the parse
    tree as specified in the paddle grammar file `paddle.lark`.
    """

    # `program_variables` is a map from ids to Variables.
    # These correspond to the variables that appear in an input
    # declaration, a hole declaration, or an assignment.
    program_variables: Dict[str, Variable]
    # `grammar_variables` is a map from a hole id to a map
    # corresponding to the varirables that appear in that hole's
    # grammar.
    grammar_variables: Dict[str, Dict[str, Variable]]

    def __init__(self):
        self.program_variables = {}
        self.grammar_variables = {}
        super().__init__()

    def _add_program_variable(self, var: Variable):
        """
        This method should be called upon encountering a variable
        while traversing the parse tree.
        This var is added to self.program_variables so that it may be
        found by name while traversing the remainder of the parse tree.
        """
        if var.name in self.program_variables.keys():
            raise TransformerVariableException(
                f"Variable with id \"{var.name}\" is declared more than once.")
        self.program_variables[var.name] = var

    def _add_grammar_variable(self, hole_id: str, var: Variable):
        if hole_id not in self.grammar_variables.keys():
            self.grammar_variables[hole_id] = {}
        if var.name in self.grammar_variables[hole_id].keys():
            raise TransformerVariableException(
                f"Grammar variable with id \"{var.name}\" is declared \
                    more than once for hole \"{hole_id}\".")
        self.grammar_variables[hole_id][var.name] = var

    def _assign_program_variables(self, node: Node):
        if node is None:
            return
        if isinstance(node, VarExpr):
            if node.name in self.program_variables.keys():
                node.var = self.program_variables[node.name]
            else:
                raise TransformerVariableException(
                    f"Expression contains unknown variable \"{node.name}\"")
        for child in node.children():
            self._assign_program_variables(child)

    def _assign_grammar_variables(self, hole_id: str, node: Node):
        if node is None:
            return
        if isinstance(node, VarExpr):
            if node.name in self.grammar_variables[hole_id].keys():
                node.var = self.grammar_variables[hole_id][node.name]
            elif node.name in self.program_variables.keys():
                node.var = self.program_variables[node.name]
            else:
                raise TransformerVariableException(
                    f"Grammar contains unknown variable \"{node.name}\"")
        for child in node.children():
            self._assign_grammar_variables(hole_id, child)

    def program(self, lst):
        inputs, lst = takedrop(lambda x: isinstance(x, Variable), lst)
        holes, lst = takedrop(lambda x: isinstance(x, HoleDeclaration), lst)
        assignments, lst = takedrop(lambda x: isinstance(x, Assignment), lst)
        constraint = list(
            dropwhile(lambda x: isinstance(x, Assignment), lst)).pop()
        return Program(inputs, holes, assignments, constraint)

    @v_args(inline=True)
    def inputdecl(self, identifier, paddletype):
        var = Variable(identifier, paddletype)
        self._add_program_variable(var)
        return var

    @v_args(inline=True)
    def paddletype(self, s):
        if s == "int":
            return PaddleType.INT
        elif s == "bool":
            return PaddleType.BOOL
        else:
            raise TransformerException("Could not parse type.")

    @v_args(inline=True)
    def holedecl(self, identifier, paddletype, grammar):
        var = Variable(identifier, paddletype)
        for rule in grammar.rules:
            rule_var = rule.symbol
            self._add_grammar_variable(identifier, rule_var)
        self._assign_grammar_variables(identifier, grammar)
        self._add_program_variable(var)
        return HoleDeclaration(var, grammar)

    @v_args(inline=True)
    def assignment(self, identifier, paddletype, expr):
        var = Variable(identifier, paddletype)
        self._assign_program_variables(expr)
        self._add_program_variable(var)
        return Assignment(var, expr)

    def assertion(self, e):
        for node in e:
            self._assign_program_variables(node)
        return self.expression(e)

    def expression(self, e):
        if len(e) >= 1:
            return e[0]
        return None

    @v_args(inline=True)
    def intexpr(self, i):
        return IntConst(self.INTEGER(i))

    @v_args(inline=True)
    def boolexpr(self, b):
        return BoolConst(b)

    @v_args(inline=True)
    def varexpr(self, s):
        return VarExpr(name=s)

    @v_args(inline=True)
    def unexpr(self, op, e):
        # UNOP won't be called autmatically it seems
        return UnaryExpr(self.UNOP(op), e)

    @v_args(inline=True)
    def binexpr(self, e1, op, e2) -> Expression:
        # BINOP won't be called autmatically it seems
        return BinaryExpr(self.BINOP(op), e1, e2)

    @v_args(inline=True)
    def ternexpr(self, e1, e2, e3) -> Expression:
        return Ite(e1, e2, e3)

    def grammar(self, lst):
        prod_rules = []
        for rule in lst:
            if isinstance(rule, Grammar):
                prod_rules += rule.rules
            elif isinstance(rule, ProductionRule):
                prod_rules += [rule]
        return Grammar(prod_rules)

    @v_args(inline=True)
    def productionrule(self, identifier, paddletype, production):
        var = Variable(identifier, paddletype)
        return ProductionRule(var, production)

    def production(self, lst):
        return flatten(lst)

    @v_args(inline=True)
    def grammarexpression(self, e):
        return e

    def INTEGER(self, n) -> int:
        return int(n)

    def BOOL(self, b) -> bool:
        if b == "True":
            return True
        elif b == "False":
            return False
        else:
            raise TransformerException("Could not parse boolean constant.")

    def ID(self, s) -> str:
        return str(s)

    def UNOP(self, s) -> UnaryOperator:
        s = str(s)
        if s == "abs":
            return UnaryOperator.ABS
        elif s == "-":
            return UnaryOperator.NEG
        elif s == "!":
            return UnaryOperator.NOT
        else:
            raise TransformerException(
                f"Could not parse unary operator '{s}'.")

    def BINOP(self, s) -> BinaryOperator:
        operator_map = {
            "+": BinaryOperator.PLUS,
            "-": BinaryOperator.MINUS,
            "*": BinaryOperator.TIMES,
            "/": BinaryOperator.DIV,
            "%": BinaryOperator.MODULO,
            "=": BinaryOperator.EQUALS,
            "!=": BinaryOperator.NOTEQUALS,
            "<": BinaryOperator.LESSTHAN,
            "<=": BinaryOperator.LESSTHAN_EQ,
            ">": BinaryOperator.GREATER,
            ">=": BinaryOperator.GREATER_EQ,
            "&&": BinaryOperator.AND,
            "||": BinaryOperator.OR
        }
        if s in operator_map.keys():
            return operator_map[s]
        raise TransformerException("Could not parse binary operator.")

    def GRAMMARCONST(self, s) -> Expression:
        if s == "Var":
            return GrammarVar()
        elif s == "Integer":
            return GrammarInteger()
        else:
            raise TransformerException("Could not parse grammar constant.")


def paddle_transform(parse_tree):
    """
    Transform Paddle parse tree to Paddle AST.
    """
    transformer = ast_utils.create_transformer("paddle", ToAst())
    return transformer.transform(parse_tree)
