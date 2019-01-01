from importlib import import_module
from inspect import isclass

from ..context import tohu
from tohu.v6.base import TohuBaseGenerator


def check_each_generator_class_has_at_least_one_exemplar_instance(
    module_name, exemplar_instances, exclude_classes=None
):
    """
    Helper function to check that for each generator class occurring
    in the module `module_name` there is at least one instance in the
    list `exemplar_instances` that is an instance of this generator
    class. Any entries in the list `exclude_classes` are excluded from
    the check. The base class TohuBaseGenerator is excluded by default.
    """
    m = import_module(module_name)

    generator_classes = [
        cls
        for cls in m.__dict__.values()
        if isclass(cls)
        and issubclass(cls, TohuBaseGenerator)
        and cls.__module__.startswith(module_name)
    ]

    exclude_classes = exclude_classes or []
    for cls in exclude_classes:
        generator_classes.remove(cls)

    for cls in generator_classes:
        if not any([isinstance(x, cls) for x in exemplar_instances]):
            raise RuntimeError(f"No exemplar generator defined for class '{cls}'")
