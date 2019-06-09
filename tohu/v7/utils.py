from .._version import get_versions

__all__ = ["print_tohu_version", "identity"]


def print_tohu_version():  # pragma: no cover
    """
    Convenience helper function to print the current tohu version.
    """
    print(f"Tohu version: {get_versions()['version']}")


def identity(x):
    """
    Helper function which returns its argument unchanged.
    That is, `identity(x)` returns `x` for any input `x`.
    """
    return x


def print_generated_sequence(gen, num, *, fmt="", sep=", ", seed=None):  # pragma: no cover
    """
    Helper function which prints a sequence of `num` item produced by the random generator `gen`.

    Example:
    >>> g = Integer(1, 20)
    >>> print_generated_sequence(g, num=10, seed=99999, fmt='02d', sep=", ")
    Generated sequence: 06, 07, 18, 12, 19, 05, 17, 15, 09, 18
    """
    if seed:
        gen.reset(seed)

    elems = [format(next(gen), fmt) for _ in range(num)]
    sep_initial = "\n\n" if "\n" in sep else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))
