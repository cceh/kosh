from inspect import stack
from re import search
from typing import Callable, get_type_hints


def concretemethod(method: Callable) -> Callable:
    """
    ``concretemethod`` annotation with typechecking. This inheritance helper
    throws an error when an annotated ``concretemethod`` does not correctly
    inherit its base methods signature.

    :param method: The decorated method.
    :returns: The decorated method.
    :raises TypeError: On incorrect inheritance.
    """
    name = search(r"class[^(]+\((\w+)\)\:", stack()[2][4][0]).group(1)
    base = getattr(stack()[2][0].f_locals[name], method.__name__)

    if get_type_hints(method) != get_type_hints(base):
        raise TypeError("Invalid concretisation")

    return method
