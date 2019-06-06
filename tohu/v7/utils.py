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


def print_generated_sequence(gen, num, *, sep=", ", fmt="", seed=None):  # pragma: no cover
    """
    Helper function which prints a sequence of `num` items
    produced by the random generator `gen`.
    """
    if seed:
        gen.reset(seed)

    elems = [format(next(gen), fmt) for _ in range(num)]
    sep_initial = "\n\n" if "\n" in sep else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))
