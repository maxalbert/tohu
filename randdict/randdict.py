class RandDict:
    """
    Random dictionary generator.
    """
    def __init__(self, **itemgens):
        """
        TODO: Write me!!
        """
        self._itemgens = itemgens

    def next(self):
        """
        Return next instance of a random dictionary.
        """
        d = {key: value.next() for key, value in self._itemgens.items()}
        return d
