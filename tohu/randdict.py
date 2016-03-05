class RandDict:
    """
    Random dictionary generator.
    """

    def __init__(self, **itemgens):
        """
        TODO: Write me!!
        """
        self._itemgens = itemgens

    def __next__(self):
        """
        Return next instance of a random dictionary.
        """
        d = {key: next(value) for key, value in self._itemgens.items()}
        return d
