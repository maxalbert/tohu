from .base import TohuBaseGenerator
from .primitive_generators import Constant

__all__ = ['as_tohu_generator']


def as_tohu_generator(g):
    """
    If g is a tohu generator return it unchanged,
    otherwise wrap it in a Constant generator.
    """

    if isinstance(g, TohuBaseGenerator):
        return g
    else:
        return Constant(g)
