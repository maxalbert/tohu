__all__ = ['identity', 'print_generated_sequence']


def identity(x):
    """
    Helper function which returns its argument unchanged.
    That is, `identity(x)` returns `x` for any input `x`.
    """
    return x


def print_generated_sequence(gen, num, *, sep=", ", seed=None):
    """
    Helper function which prints a sequence of `num` items
    produced by the random generator `gen`.
    """
    if seed:
       gen.reset(seed)

    elems = [str(next(gen)) for _ in range(num)]
    sep_initial = "\n\n" if sep == "\n" else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))