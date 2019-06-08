from collections.abc import Mapping, Sequence
from operator import attrgetter
import typing

from .logging import logger


class FieldSelector:
    def __init__(
        self, tohu_items_cls: type, fields: typing.Union[typing.Sequence[str], typing.Mapping[str, str], None] = None
    ):
        self.tohu_items_cls = tohu_items_cls
        if fields is None:
            self.fields = {name: name for name in self.tohu_items_cls.field_names}
        elif isinstance(fields, Mapping):
            self.fields = fields
        elif isinstance(fields, Sequence):
            self.fields = {name: name for name in fields}
        else:  # pragma: no cover
            raise TypeError(f"Invalid 'fields' argument: {fields}")

        if not set(self.fields.values()).issubset(self.tohu_items_cls.field_names):
            # raise ValueError("Field names must be a subset of the fields defined on `tohu_items_cls`.")
            logger.warning("Field names are not a subset of the fields defined on `tohu_items_cls`.")
            logger.warning("TODO: Ensure we can deal with nested fields!")

        self.field_selectors = {new_name: attrgetter(orig_name) for new_name, orig_name in self.fields.items()}

    def __call__(self, items: typing.Iterable) -> typing.Iterable:
        for item in items:
            yield {name: f(item) for name, f in self.field_selectors.items()}
