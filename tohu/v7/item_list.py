import collections


class ItemList(collections.Iterable):
    """
    Represents a list of items produced by calling `generate()` on a tohu generator.
    """

    def __init__(self, items):
        assert isinstance(items, list)
        self.items = items
        self.num_items = len(items)

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
