from lang.ast import *
import unittest
from lang.paddle import parse
from lark import exceptions
from lang.transformer import TransformerVariableException
import os
from pathlib import Path


class TestAst(unittest.TestCase):
    def test_ast_well_formed_manual1(self):
        a = Variable("a", PaddleType.INT)
        b = Variable("b", PaddleType.INT)
        # Hole declaration
        h1_var = Variable("h1", PaddleType.INT)
        g = Variable("G", PaddleType.INT)
        h1_rules = [
            ProductionRule(
                g, [
                    BinaryExpr(BinaryOperator.PLUS, VarExpr(g), VarExpr(g)),
                    BinaryExpr(BinaryOperator.MINUS, VarExpr(g), VarExpr(g)),
                    IntConst(0),
                    IntConst(1),
                    GrammarVar()
                ])
        ]
        h1_grammar = Grammar(h1_rules)
        h1 = HoleDeclaration(h1_var, h1_grammar)
        # Assignments
        # c = a > 0 ? a : h1
        c = Variable("c", PaddleType.INT)
        ceq = Assignment(c, Ite(
            cond=BinaryExpr(BinaryOperator.GREATER, VarExpr(a), IntConst(0)),
            true_br=VarExpr(a),
            false_br=VarExpr(h1_var)))
        d = Variable("d", PaddleType.INT)
        # d = abs(b) + c
        deq = Assignment(d, BinaryExpr(BinaryOperator.PLUS,
                                       left_operand=UnaryExpr(
                                           UnaryOperator.ABS, VarExpr(b)),
                                       right_operand=VarExpr(c)))
        # Final assert: a > 0
        assertion = BinaryExpr(BinaryOperator.GREATER, VarExpr(a), IntConst(0))

        # The whole program:
        program = Program([a, b], [h1], [ceq, deq], assertion)
        self.assertTrue(program.check_well_formed())
        string = """
        input a : int;
        input b : int;
        hole h1 : int [
                  G : int -> G + G | G - G | 0 | 1 | Var
                ];
        define c : int = (a > 0) ? a : h1;
        define d : int = (abs b) + c;
        assert (a > 0);
        """
        self.assertEqual(str(parse(string=string)), str(program))

    def test_bad_inputs(self):
        # Inputs should not be declared after holes or assignments
        bad_program_string_1 = """
        input a : int;
        input b : int;
        hole h1 : int [
                  G : int -> G + G | G - G | 0 | 1 | Var
                ];
        define c : int = (a > 0) ? a : h1;
        define d : int = (abs b) + c;
        input x : int;
        assert (a > 0);
        """

        bad_program_string_2 = """
        input a : int;
        input b : int;
        hole h1 : int [
                  G : int -> G + G | G - G | 0 | 1 | Var
                ];
        input a : int;
        define c : int = (a > 0) ? a : h1;
        define d : int = (abs b) + c;
        assert (a > 0);
        """
        self.assertRaises(exceptions.UnexpectedCharacters,
                          parse, string=bad_program_string_1)
        self.assertRaises(exceptions.UnexpectedCharacters,
                          parse, string=bad_program_string_2)

    def test_bad_grammar(self):
        # In the following program, there is more than one rule per nonterminal
        # in the grammar
        bad_program_string = """
        input a : int;
        input b : int;
        hole h1 : int [
                  G : int -> B ? G : G | G + G | G - G | abs G | 0 | 1 | Var;
                  G : int -> G + G;
                  B : bool -> G > G | G < G | G = G | B && B | B || B | ! B
                ];
        define c : int = (a > 0) ? a : h1;
        define d : int = (abs b) + c;
        assert (a > 0);
        """
        self.assertRaises((TransformerVariableException, exceptions.VisitError),
                          lambda: parse(string=bad_program_string))

    def test_proper_association_1(self):
        # The expressions a && c + b and a && (c + b) should result in the same AST
        program_string = """
        input a : int;
        input b : int;
        input c : int;
        define d : int = a && c + b;
        define e : int = a && (c + b);
        assert (e > 0);
        """
        prog: Program = parse(string=program_string)
        self.assertEqual(len(prog.assignments), 2,
                         msg="Program should have exaclty 2 assignments.")
        d = prog.assignments[0].expr
        e = prog.assignments[1].expr
        self.assertEqual(str(e), str(
            d), msg="%s and %s should be equal." % (d, e))

    def test_proper_association_2(self):
        program_string = """
        input a : int;
        input b : int;
        input c : int;
        input y : int;
        define d : bool = (a > y) && (c >= b);
        define e : bool = a > y && c >= b;
        assert (e);
        """
        prog: Program = parse(string=program_string)
        self.assertEqual(len(prog.assignments), 2,
                         msg="Program should have exaclty 2 assignments.")
        d = prog.assignments[0].expr
        e = prog.assignments[1].expr
        self.assertEqual(str(e), str(
            d), msg="%s and %s should be equal." % (d, e))

    def test_hole_can_use(self):
        program_string = """
        input a : int;
        input b : int;
        input c : int;
        input y : int;
        hole h1 : int [ G : int -> Var | Integer | 0 | 1];
        define d : bool = (a > y) && (c >= b);
        define e : bool = a > y && h1 >= b;
        assert e;
        """
        prog: Program = parse(string=program_string)
        self.assertTrue(prog.check_well_formed(),
                        msg="program should be well-formed")
        self.assertEqual(len(prog.assignments), 2,
                         msg="Program should have exaclty 2 assignments.")
        self.assertEqual(len(prog.holes), 1,
                         msg="Program should have exactly 1 hole.")

        h1_can_use = prog.hole_can_use("h1")
        self.assertEqual(
            len(h1_can_use), 5, msg="h1 should be able to use 5 variables.")
        d = prog.get_var_of_name("d")
        self.assertTrue(
            d is not None, msg="d should be a variable in the program.")
        self.assertTrue(d in h1_can_use,
                        msg="d should be in the variables h1 can use.")
        e = prog.get_var_of_name("e")
        self.assertTrue(
            e is not None, msg="e should be a variable in the program.")
        self.assertFalse(e in h1_can_use,
                         msg="e should not be in the variables h1 can use.")

    def test_all_varexpr_has_var(self):
        examples_directory = '%s/examples/for_parsing' % Path(
            __file__).parent.parent.absolute()
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                filename = os.path.join(examples_directory, filename)
                try:
                    ast = parse(filename)
                except:
                    self.assertTrue(
                        True, "Exception was raised when parsing %s" % filename)
                self.all_varexpr_has_var(ast)
            else:
                continue

    def all_varexpr_has_var(self, node: Node):
        if node is not None:
            if isinstance(node, VarExpr):
                self.assertTrue(isinstance(node.var, Variable))
            for child in node.children():
                self.all_varexpr_has_var(child)

    def test_all_program_children_are_nodes(self):
        examples_directory = '%s/examples/for_parsing' % Path(
            __file__).parent.parent.absolute()
        for filename in os.listdir(examples_directory):
            if filename.endswith(".paddle"):
                filename = os.path.join(examples_directory, filename)
                try:
                    ast = parse(filename)
                except:
                    self.assertTrue(
                        True, "Exception was raised when parsing %s" % filename)
                self.all_varexpr_has_var(ast)
            else:
                continue

    def all_program_children_are_nodes(self, node: Node):
        self.assertTrue(isinstance(node, Node))
        for child in node.children():
            self.all_program_children_are_nodes(child)
