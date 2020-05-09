'''
    From pwwang/python-varname
    https://github.com/pwwang/python-varname
'''

import ast
import inspect
import executing


class IncorrectUseOfNameof(Exception):
    """When nameof is used in statement"""


def nameof(*args):
    """Get the names of the variables passed in"""
    frame = inspect.stack()[1].frame
    exe = executing.Source.executing(frame)

    if not exe.node:
        # we cannot do: assert nameof(a) == 'a'
        raise IncorrectUseOfNameof("Should not use nameof it in statements.")

    assert isinstance(exe.node, ast.Call)

    ret = []
    for node in exe.node.args:
        if not isinstance(node, ast.Name):
            raise IncorrectUseOfNameof("Only variables should "
                                       "be passed to nameof")
        ret.append(node.id)

    if not ret:
        raise IncorrectUseOfNameof("At least one variable should be "
                                   "passed to nameof")

    return ret[0] if len(args) == 1 else tuple(ret)
