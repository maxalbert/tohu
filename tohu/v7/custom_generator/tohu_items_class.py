import attr

__all__ = ["make_tohu_items_class"]


def make_tohu_items_class(clsname, field_names):
    """
    Parameters
    ----------
    clsname: string
        Name of the class to be created.

    field_names: list of strings
        Names of the field attributes of the class to be created.
    """
    item_cls = attr.make_class(clsname, {name: attr.ib() for name in field_names}, repr=True, cmp=True, frozen=True)
    func_eq_orig = item_cls.__eq__

    def func_eq_new(self, other):
        """
        Custom __eq__() method which also allows comparisons with
        tuples and dictionaries. This is mostly for convenience
        during testing.
        """

        if isinstance(other, self.__class__):
            return func_eq_orig(self, other)
        else:
            if isinstance(other, tuple):
                return attr.astuple(self) == other
            elif isinstance(other, dict):
                return attr.asdict(self) == other
            else:
                raise TypeError(
                    f"Tohu items have types that cannot be compared: "
                    "{self.__class__.__name__}, {other.__class__.__name__}"
                )

    item_cls.__eq__ = func_eq_new
    item_cls.field_names = field_names
    return item_cls
