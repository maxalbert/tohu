import attr

__all__ = ["make_tohu_items_class"]


def is_tohu_items_class(cls):
    try:
        cls.__is_tohu_items_class__
        return True
    except AttributeError:
        return False


def tohu_item_classes_are_equivalent(cls1, cls2):
    return is_tohu_items_class(cls1) and is_tohu_items_class(cls2) and cls1.__name__ == cls2.__name__ and cls1.__attrs_attrs__ == cls2.__attrs_attrs__


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
    item_cls.__is_tohu_items_class__ = True
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
            elif tohu_item_classes_are_equivalent(self.__class__, other.__class__):
                return attr.asdict(self) == attr.asdict(other)
            else:
                raise TypeError(
                    f"Tohu items have types that cannot be compared: "
                    "{self.__class__.__name__}, {other.__class__.__name__}"
                )

    item_cls.__eq__ = func_eq_new
    item_cls.field_names = field_names
    return item_cls
