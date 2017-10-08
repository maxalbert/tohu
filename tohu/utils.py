from collections import deque
from functools import partial
from .generators import BaseGenerator, GeolocationPair, TupleGenerator

__all__ = ['First', 'Second', 'Nth', 'Split', 'Zip', 'Geolocation']


class Nth(BaseGenerator):
    """
    Generator which allows to extract the n-th element from a tuple-producing generator.
    """

    def __init__(self, g, idx):
        self.g = g
        self.idx = idx

    def __next__(self):
        return next(self.g)[self.idx]

    def _spawn(self):
        return Nth(self.g._spawn(), self.idx)

    def reset(self, seed):
        self.g.reset(seed)


First = partial(Nth, idx=0)
Second = partial(Nth, idx=1)


class BufferedTuple(BaseGenerator):
    """
    Helper class which allows buffered extraction
    of items from a tuple generator.
    """

    def __init__(self, g, *, tuple_len, maxbuffer=10):
        """
        Parameters
        ----------

        g: tohu generator
            The generator to be buffered. The items produced by `g` must be tuples.
        tuple_len: integer
            Length of tuples produced by g.
        maxbuffer: integer
            Maximum number of items to be buffered.
        """
        self.g = g
        self.tuple_len = tuple_len
        self.maxbuffer = maxbuffer
        self._reset_queues()

    def _spawn(self):
        return BufferedTuple(self.g._spawn(), tuple_len=self.tuple_len, maxbuffer=self.maxbuffer)

    def _reset_queues(self):
        self._queues = [deque(maxlen=self.maxbuffer) for _ in range(self.tuple_len)]

    def _refill(self):
        item = next(self.g)
        for x, queue in zip(item, self._queues):
            queue.append(x)

    def reset(self, seed):
        self.g.reset(seed)
        self._reset_queues()

    def next_nth(self, n):
        if len(self._queues[n]) == 0:
            self._refill()
        return self._queues[n].popleft()


def Split(g, *, maxbuffer=10, tuple_len=None):
    """
    Split a tuple generator into individual generators.

    Parameters
    ----------
    g: tohu generator
        The generator to be split. The items produced by `g` must be tuples.
    maxbuffer: integer
        Maximum number of items produced by `g` that will be buffered.
    """
    if tuple_len is None:
        try:
            tuple_len = g.tuple_len
        except AttributeError:
            raise ValueError("Argument 'tuple_len' must be given since generator is not of type TupleGenerator.")

    g_buffered = BufferedTuple(g, maxbuffer=maxbuffer, tuple_len=tuple_len)

    class NthBuffered(BaseGenerator):
        def __init__(self, g, idx):
            self.g = g
            self.idx = idx

        def __next__(self):
            return self.g.next_nth(self.idx)

        def _spawn(self):
            return NthBuffered(self.g._spawn(), self.idx)

        def reset(self, seed):
            self.g.reset(seed)

    return tuple(NthBuffered(g_buffered, i) for i in range(tuple_len))


class Zip(TupleGenerator):
    """
    Create a generator which produces tuples that are
    combined from the elements produced by multiple
    individual generators.
    """

    def __init__(self, *generators, seed=None):
        self._generators = [g._spawn() for g in generators]
        self.reset(seed)

    def __next__(self):
        return tuple(next(g) for g in self._generators)

    def reset(self, seed):
        for g in self._generators:
            g.reset(seed)


def Geolocation():
    """
    Return a pair (Lon, Lat) of iterators producing.
    """
    return Split(GeolocationPair())