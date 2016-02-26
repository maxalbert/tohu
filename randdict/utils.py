"""
Helper functions and classes used in unit tests.
"""


class MockRandomGenerator:
    """
    Mock random generator which sequentially returns values in a given
    sequence whenever its next() method is called.

    """
    def __init__(self, values):
        """
        Initialise random generator with given values.

        """
        self.values = (x for x in values)

    def next(self):
        """
        Return next value in sequence.

        """
        return next(self.values)
