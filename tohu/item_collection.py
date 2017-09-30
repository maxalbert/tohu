class ItemCollection:
    """
    Class representing a collection of items.
    """

    def __init__(self, items):
        self.items = list(items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "<ItemCollection of length {}>".format(len(self))

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]