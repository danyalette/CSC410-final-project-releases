"""
# CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This is the main entry point for this project.


Open the documentation in your browser, e.g. open `docs/main.html`.

# Group Members

TODO: Remove me, and write the names and UTORids of the group members.

# Roles and Tasks

TODO: Remove me, and write a *very brief* description of what each team member
did in the project.

---

Good luck, you'll be writing your first program synthesizer!

# Reminders from the handout

This is the list of files you will have to modify:

- [[test/student_test.py]]

- [[lang/symb_eval.py]]

- [[verification/verifier.py]]

- [[synthesis/synth.py]]

To understand how a Paddle program is represented, you can have a look at
[[lang/ast.py]].

We encourage you to look at the examples in `examples/` and add your
own there!

## Linting

The following command should return `0`:

`
flake8 . --count --exit-zero --max-line-length=127 --ignore F,W503,W504,E722
`

## Testing
The following command should succeed:

`
python test.py
`

You should also uncomment the relevant tests as you make progress.

## Documenting
You should document your code, and generate the documentation using:

`
pycco *.py **/*.py
`

The documentation for `pycco` is available [here](https://pycco-docs.github.io/pycco/).


---
"""

import sys
from typing import Mapping
from lang.paddle import parse
from lang.ast import Expression
from lang.symb_eval import Evaluator
from synthesis.synth import Synthesizer
from verification.verifier import is_valid


# You can modifiy this variable. It limits how many times the synthesis loop
# will call the synthesis method, which is necessary in case there is no
# solution to the synthesis problem, or the program is very complex and waiting
# for the loop to find it would take too long.
ITERATIONS_LIMIT = 1000


def usage():
    """Print usage information for this file."""
    print("Usage: python3 main.py METHOD_NUM INPUT_FILE")


def print_solution(solution_map: Mapping[str, Expression]) -> None:
    """Print the solution, which is a map from hole IDs to expressions."""
    for hole in solution_map:
        print(f"The solution for {hole} is {solution_map[hole]}")


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print("Please provide a method number and an input file!")
        print("There are some example inputs in ./examples/")
        usage()
        sys.exit(-1)
    # ! Important !
    # YOU SHOULD NOT MODIFY THE NAME OF THE VARIABLES USED BELOW THIS LINE!
    # YOU CAN ONLY ADD NEW VARIABLES, OR PRINT STATEMENTS
    #
    #
    # Get the method that should be used
    method_num = int(sys.argv[1])
    # Get the name of the input file
    filename = sys.argv[2]
    # Parse the input file into an AST
    ast = parse(filename)
    # Initialize a Synthesizer with it
    synt = Synthesizer(ast)
    # Iterate until a solution is found or iteration limit is reached
    iterations = 0
    while iterations < ITERATIONS_LIMIT:
        iterations += 1
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
            print_solution(hole_completions)
            sys.exit(0)
        # Otherwise the loop continues.
