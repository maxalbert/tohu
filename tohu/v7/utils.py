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
