import attr
import collections
import pandas as pd


class ItemList(collections.Iterable):
    """
    Represents a list of items produced by calling `generate()` on a tohu generator.
    """

    def __init__(self, items, tohu_items_cls=None):
        assert isinstance(items, list)
        self.items = items
        self.num_items = len(items)
        self.tohu_items_cls = tohu_items_cls

    def __repr__(self):
        return f"<ItemList containing {self.num_items} items>"

    def __eq__(self, other):
        return self.items == other

    def __len__(self):
        return self.num_items

    def __getitem__(self, idx):
        return self.items[idx]

    def __iter__(self):
        return iter(self.items)

    def to_df(self):
        if self.tohu_items_cls is None:  # pragma: no cover
            raise RuntimeError()

        colnames_to_export = self.tohu_items_cls.field_names
        df = pd.DataFrame([x.as_dict() for x in self.items], columns=colnames_to_export)
        return df