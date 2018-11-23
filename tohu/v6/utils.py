from collections import namedtuple

__all__ = ['identity', 'print_generated_sequence']


def identity(x):
    """
    Helper function which returns its argument unchanged.
    That is, `identity(x)` returns `x` for any input `x`.
    """
    return x


def print_generated_sequence(gen, num, *, sep=", ", fmt='', seed=None):
    """
    Helper function which prints a sequence of `num` items
    produced by the random generator `gen`.
    """
    if seed:
       gen.reset(seed)

    elems = [format(next(gen), fmt) for _ in range(num)]
    sep_initial = "\n\n" if '\n' in sep else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))
