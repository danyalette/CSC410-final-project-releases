"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file is the entry point of the paddle parser.
"""
from pathlib import Path
from typing import Optional
from lark import Lark
from lang.transformer import paddle_transform

parser = Lark.open("paddle.lark", rel_to=Path(
    __file__).absolute(), start='program', propagate_positions=True)


def parse(filename: Optional[str] = None, string: Optional[str] = None):
    """
    This function takes a filename of a paddle file or a string of
    paddle code and returns the AST of the program.
    """
    if (filename is None and string is None):
        raise Exception(
            "Please provide a filename or a string to paddle.parse.")
    if string is not None:
        tree = paddle_transform(parser.parse(string))

    else:
        with open(filename) as file:
            content = "\n".join(file.readlines())
            tree = paddle_transform(parser.parse(content))
    return tree
