"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file contains classes that are used to construct the Paddle AST.
"""
import sys
from typing import Set, List, Optional, Tuple
from enum import Enum, unique
from lark import ast_utils


class ASTException(TypeError):
    """
    Exception that is raised during the creation of an
    AST Node when the parameters are not the correct type.
    """


# Language definitions : Operators and Types


@unique
class BinaryOperator(Enum):
    """Binary operators."""
    # The arithmetic + operator.
    PLUS = 1
    # The arithmetic - operator.
    MINUS = 2
    # The arithmetic * operator.
    TIMES = 3
    # The arithmetic / operator.
    DIV = 4
    # The arithmetic % operator.
    MODULO = 5
    # The arithmetic = operator.
    EQUALS = 6
    # The arithmetic > operator.
    GREATER = 7
    # The arithmetic >= operator.
    GREATER_EQ = 8
    # The arithmetic < operator.
    LESSTHAN = 9
    # The arithmetic <= operator.
    LESSTHAN_EQ = 10
    # The boolean && operator.
    AND = 11
    # The boolean || operator.
    OR = 12
    # The arithmetic != operator.
    NOTEQUALS = 13

    def __str__(self):
        strings = ["+", "-", "*", "/", "%", "=",
                   ">", ">=", "<", "<=", "&&", "||", "!="]
        return strings[self.value - 1]


@unique
class UnaryOperator(Enum):
    """Unary operators."""
    # The boolean ! (not) operator
    NOT = 1
    # The arithmetic abs (absolute value) operator
    ABS = 2
    # The unary minus operator
    NEG = 3

    def __str__(self):
        strings = ["!", "abs", "-"]
        return strings[self.value - 1]


@unique
class PaddleType(Enum):
    """Paddle types."""
    # The type of integers (int)
    INT = 1
    # The type of booleans (bool)
    BOOL = 2

    def __str__(self):
        if self.value == 1:
            return "int"
        if self.value == 2:
            return "bool"
        return "unknown"


# =============================================================================
# AST Nodes abstract classes.
# =============================================================================


class Node(ast_utils.Ast):

    """ Abstract base class for AST nodes.
    """

    attr_names: Tuple[str]

    def children(self) -> list:
        """ A sequence of all children that are Nodes
        """
        return []

    def iter(self, func) -> None:
        """Apply function fun recursively to all children."""
        for child in self.children():
            if child is not None:
                func(child)
                child.iter(func)

    def show(self, buf=sys.stdout, offset=0, attrnames=False):
        """ Pretty print the Node and all its attributes and
            children (recursively) to a buffer.

            buf:
                Open IO buffer into which the Node is printed.

            offset:
                Initial offset (amount of leading spaces)

            attrnames:
                True if you want to see the attribute names in
                name=value pairs. False to only see the values.
        """
        lead = ' ' * offset
        buf.write(f"{lead}{self.__class__.__name__}: ")

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self, n)) for n in self.attr_names]
                attrstr = ', '.join(f"{nv[0]}={nv[1]}" for nv in nvlist)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join(str(v) for v in vlist)
            buf.write(attrstr)

        buf.write('\n')

        for child in self.children():
            if child is not None:
                child.show(
                    buf,
                    offset=offset + 2,
                    attrnames=attrnames)

    attr_names = tuple()

# Variables, Expressions and Assignments


class Variable(Node):
    """ A Variable is a name and a type (and instance of PaddleType).

        Slots:
        - name: a string representing the name of the variable,
        - type: a PaddleType representing the type (int or boolean)
        of the variable
    """

    def __init__(self, name: str, paddletype: PaddleType) -> None:
        self.name = name
        self.type = paddletype

    def __str__(self) -> str:
        return f"{self.name} : {str(self.type)}"

    attr_names = ('name', 'type')


# === Paddle Expressions and Declarations Abstract Nodes ===

class Expression(Node):
    """An abstract class for expressions."""

    def uses(self,) -> Set[Variable]:
        '''An expression uses some variables.'''


class Declaration(Node):
    """ An abstract class for Nodes that declare variables.
    Calling declares() on a Declaration returns the set of
    variables declared in that Node.
    """

    def declares(self,) -> Set[Variable]:
        """Get all Variable nodes declared within this node."""
        return set()


class Assignment(Declaration):
    """ An Assignment represents the assignment of an expression
        to a variable.
    """

    def __init__(self, var: Variable, expr: Expression) -> None:
        if not isinstance(expr, Expression):
            raise ASTException("expr must be an Expression")
        if not isinstance(var, Variable):
            raise ASTException("var must be a Variable")
        self.var = var
        self.expr = expr

    def children(self) -> list:
        return [self.var, self.expr]

    def declares(self) -> Set[Variable]:
        return {self.var}

    attr_names = set()

    def __str__(self) -> str:
        return f"{self.var} = {self.expr}"


# === The Paddle Expressions ===

class Ite(Expression):
    """An if-then-else expression."""

    cond: Expression
    true_br: Expression
    false_br: Expression

    def __init__(self, cond: Expression, true_br: Expression,
                 false_br: Expression) -> None:
        if not ((isinstance(cond, Expression)
                 and isinstance(true_br, Expression)
                 and isinstance(false_br, Expression))):
            raise ASTException(
                "cond, true_br and false_br should all be an Expression.")
        self.cond = cond
        self.true_br = true_br
        self.false_br = false_br

    def children(self) -> list:
        return [self.cond, self.true_br, self.false_br]

    def uses(self) -> Set[Variable]:
        branches_uses = self.true_br.uses().union(self.false_br.uses())
        return self.cond.uses().union(branches_uses)

    def __str__(self) -> str:
        return f"{self.cond} ? {self.true_br} : {self.false_br}"


class BinaryExpr(Expression):
    """ A Binary operation with an operator (BinaryOperator),
    an left and a right operand. """

    def __init__(self, operator: BinaryOperator, left_operand: Expression,
                 right_operand: Expression) -> None:
        if not isinstance(operator, BinaryOperator):
            print(f"Operator was {operator}, not a proper operator")
            raise ASTException(
                "operator should be an instance of BinaryOperator")

        if not isinstance(left_operand, Expression):
            raise ASTException(
                "left_operand should be an instance of Expression")

        if not isinstance(right_operand, Expression):
            raise ASTException(
                "right_operand should be an instance of Expression")

        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def children(self) -> list:
        return [self.left_operand, self.right_operand]

    def uses(self,) -> Set[Variable]:
        return self.left_operand.uses().union(self.right_operand.uses())

    def __str__(self):
        return (f"({str(self.left_operand)} {str(self.operator)} "
                f"{str(self.right_operand)})")

    attr_names = ('operator', )


class UnaryExpr(Expression):
    """ A unary expression with an operator (UnaryOperator) and an operand. """

    def __init__(self, operator: UnaryOperator, operand: Expression):

        if not isinstance(operator, UnaryOperator):
            raise ASTException(
                "operator should be an instance of UnaryOperator")
        self.operator = operator

        if not isinstance(operand, Expression):
            raise ASTException("operand should be an instance of Expression")

        self.operand = operand

    def children(self) -> list:
        return [self.operand]

    def uses(self) -> Set[Variable]:
        return self.operand.uses()

    def __str__(self):
        return f"({str(self.operator)} {str(self.operand)})"

    attr_names = ('operator', )


class VarExpr(Expression):
    """ A variable as an expression. """

    def __init__(self, var: Optional[Variable] = None,
                 name: Optional[str] = None) -> None:
        if var is None and name is None:
            name = ""
        elif name is None:
            name = var.name
        self.name = name
        self.var = var

    def uses(self) -> Set[Variable]:
        if self.var is None:
            return set()
        return {self.var}

    def __str__(self) -> str:
        return self.name

    def children(self) -> list:
        if self.var is None:
            return []
        return [self.var]

    attr_names = ('name', )


class IntConst(Expression):
    """ An integer constant is an expression with an integer value."""

    def __init__(self, value: int) -> None:
        if not isinstance(value, int):
            raise ASTException("value must be an int")
        self.value = value

    def uses(self) -> Set[Variable]:
        return set()

    def __str__(self) -> str:
        return str(self.value)

    attr_names = ('value', )


class BoolConst(Expression):
    """ A boolean constant is an expression with a boolean value."""

    def __init__(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ASTException("value must be a bool")
        self.value = value

    def uses(self) -> Set[Variable]:
        return set()

    def __str__(self) -> str:
        return str(self.value)

    attr_names = ('value', )

# =============================================================================
# Grammars and Holes
# =============================================================================


class GrammarInteger(Expression):
    """A grammar integer is a special constant that can be completed
    with and integer constant expression with any value.
    """

    def uses(self) -> Set[Variable]:
        return set()

    def __str__(self) -> str:
        return "Integer"


class GrammarVar(Expression):
    """ A grammar variable (Var in a program) is a special expression
    that can be completed with any variable that the hole can use.
    A hole can use any variable that has been declared before its
    first use.
    """

    def uses(self) -> Set[Variable]:
        return set()

    def __str__(self) -> str:
        return "Var"


class ProductionRule(Node):
    """ A ProductionRule is a symbol (a variable) together with a
    list of productions. """

    def __init__(self, symbol: Variable,
                 productions: List[Expression]) -> None:
        if not isinstance(symbol, Variable):
            raise ASTException("A production rule must start with a Variable.")
        self.symbol = symbol
        for production in productions:
            if not isinstance(production, Expression):
                raise ASTException(
                    "Productions of a rule must be Expressions.")
        self.productions = productions

    def __str__(self) -> str:
        productions = " | ".join([str(x) for x in self.productions])
        return f"{str(self.symbol)} -> {productions}"

    def children(self) -> list:
        return [self.symbol] + self.productions


class Grammar(Node):
    """ A grammar is a list of production rule, each with its unique
    non-terminal."""

    def __init__(self, rules: List[ProductionRule]) -> None:
        for rule in rules:
            if not isinstance(rule, ProductionRule):
                raise ASTException(
                    "Grammars can only be constructed from list of rules.")
        self.rules = rules

    def well_formed(self) -> bool:
        """Basic sanity check for whether a grammar is well-formed."""
        nonterminals = {p.symbol for p in self.rules}
        # There are as many rules as there are nonterminals
        if not len(nonterminals) == len(self.rules):
            return False
        # The variables used in the rules can only be the nonterminals
        # of the rules.
        for rule in self.rules:
            uses = set().union(*[x.uses() for x in rule.productions])
            if not uses.issubset(nonterminals):
                return False

        return True

    def __str__(self):
        rules = "; ".join([str(x) for x in self.rules])
        return f"[ {rules} ]"

    def children(self) -> list:
        if self.rules is None:
            return []
        return self.rules


class HoleDeclaration(Declaration):
    """ A hole declaration is similar to an assignment, except that the
    hole variable is not assigned a specific expression but a grammar.
    """

    def __init__(self, var: Variable, grammar: Grammar) -> None:
        if not (isinstance(var, Variable) and isinstance(grammar, Grammar)):
            raise ASTException(
                "Initialize HoleDeclaration only with Variable and Grammar.")
        self.var = var
        self.grammar = grammar

    def declares(self, ) -> Set[Variable]:
        """ A HoleDeclaration declares the hole variable. """
        return {self.var}

    def __str__(self):
        return f"hole {str(self.var)} {str(self.grammar)}"

    def children(self) -> list:
        return [self.var, self.grammar]

# =============================================================================
# Programs
# =============================================================================


class Program(Declaration):
    """ A Program contains a list of input variables, holes, assignments
    and one constraint.

    - inputs: a list of Variable (with a name and a type)
    that represent the input variables of the program,
    - holes: a list of HoleDeclaration (hole name, type
    and grammar) that represent the hole declarations of
    the program.
    - assignments: a list of Assignment, each assignment
    assigns an expression to a new variable.
    - constraint: the constraint the program must satisfy,
    represented as an Expression.

    """

    def __init__(self, inputs: List[Variable],
                 holes: List[HoleDeclaration],
                 assignments: List[Assignment],
                 constraint: Expression) -> None:
        self.inputs = inputs
        self.holes = holes
        self.assignments = assignments
        self.constraint = constraint

    def __str__(self) -> str:
        return (f"inputs: {[str(x) for x in self.inputs]}\n"
                f"holes: {[str(x) for x in self.holes]}\n"
                f"assignments: {[str(x) for x in self.assignments]}\n"
                f"constraint: {str(self.constraint)}")

    def declares(self) -> Set[Variable]:
        """Get all declared Variables nodes in the program."""
        return (set(self.inputs)
                .union(*[x.declares() for x in self.holes])
                .union(*[x.declares() for x in self.assignments]))

    def assigns(self) -> Set[Variable]:
        """Get the set of Variable nodes that appear in assignments."""
        return set().union(*[x.declares() for x in self.assignments])

    def get_var_of_name(self, name: str) -> Variable:
        """Get Variable node that corresponds to an identifier."""
        for variable in self.declares():
            if variable.name == name:
                return variable
        return None

    def hole_vars(self) -> Set[Variable]:
        """Get the set of Variables nodes that are declared as holes."""
        return {x.var for x in self.holes}

    def check_well_formed(self) -> bool:
        ''' Check that the program is well-formed. '''
        # Check that variables are used only after being declared.
        declared = set(self.inputs).union(
            *[x.declares() for x in self.holes])
        for asgn in self.assignments:
            uses = asgn.expr.uses()
            if not uses.issubset(declared):
                for var in uses.difference(declared):
                    print(f"{var.name} is not declared.")

                return False
            declared.add(asgn.var)
        for hole in self.holes:
            if not hole.grammar.well_formed():
                return False

        return True

    def hole_can_use(self, hole_name: str) -> Set[Variable]:
        """
        Returns the set of variables that can be used in
        completing the hole.
        A variable can be used in the grammar of a hole if it is
        declared before the first use of the hole.
        If the name passed as argument is not a valid hole in the
        program, the function returns None.
        """
        hole_var = None
        for variable in self.hole_vars():
            if variable.name == hole_name:
                hole_var = variable
        if hole_var is None:
            return None
        # A hole can always use at least the inputs of the program
        can_use = set(self.inputs)
        for asgn in self.assignments:
            if hole_var in asgn.expr.uses():
                return can_use
            can_use.add(asgn.var)
        # Exists the loop the hole is used only in the constraint
        return can_use

    def is_pure_expression(self, expr: Expression) -> bool:
        """
        Check if the expression is a pure expression, that is it does
        not contain any GrammarVar or GrammarInteger or non-terminal from
        the grammars.
        """
        if not isinstance(expr, Expression):
            return False
        if isinstance(expr, (GrammarInteger, GrammarVar)):
            return False
        used_non_decls = expr.uses().difference(
            self.assigns(), self.inputs)
        # Expression should contain only input or assigned variables.
        if len(used_non_decls) > 0:
            return False
        # Check that the children are well formed.
        for child in expr.children():
            if isinstance(child, Expression):
                if not self.is_pure_expression(child):
                    return False
        return True

    def children(self) -> list:
        return self.inputs + self.holes + self.assignments + [self.constraint]


def pythonize(string: str) -> str:
    """
    Very limited function to replace some operator syntax
    with python operators.
    Will not work in many cases, use with care!
    This is meant to be used to evaluate some Paddle expression directly:
        x is an expression : eval(pythonize(str(x)))
    """
    return (string.replace(' = ', ' == ').replace('&&', 'and')
            .replace('||', 'or').replace('!', 'not'))
