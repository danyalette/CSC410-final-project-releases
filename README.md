# CSC410 final project

This repository contains the starter code for the final project of CSC410H1F 2021 at the University of Toronto.

In this project, your goal will be to write a small program synthesizer: a tool that generates automatically a program that satisfies some user intent. Program synthesis is a very difficult problem that has been the focus of decades of research. In this project, you will focus on a simple but interesting problem: synthesizing small program with arithmetic expressions that satisfy a logical specification.

Throughout the term, you will learn how to build the different components needed. This project will first require you to understand how to manipulate program representations. You will also learn how to express user intent in a logical and unambiguous manner. Finally, in order to synthesize a correct program, you will need to learn how to check that a program is correct.

## Files
During the project, we expect you to carefully read and then modify the following files:
```lang/symb_eval.py``` (where you will program the evaluation function)
```synthesis/synth.py``` (where you will program the program enumerator)
```verification/verifier.py``` (where you will program the verification function)
```test/student_test.py``` (where you will add your own custom tests)
```main.py``` You should only modify `main.py` to add the required comments (docstrings). You should *not modify* the code in `main.py`, except for adding the required comments, and adding printing functions. We expect your algorithm to work as written in `main.py`.
You should have a look at the examples in `examples` add possibly add your own.


## Installation

This project requires a recent version of Python, Pip, and Graphviz, and the following:

```pip install -r requirements.txt```

## Running the project

```python main.py <method num = 1, 2, or 3> <paddle filename>```

## Testing

We are using unittest. If you add new tests, ensure that you import them in `test.py`.

```python test.py -v```

You can also use pytest to run all tests in the `test` directory:
```pytest test```

## Documentation
We are using `pycco`, run:
`pycco *.py **/*.py`
And open `docs/main.html` with your browser.
