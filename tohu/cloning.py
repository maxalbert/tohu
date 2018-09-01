__all__ = ['CloneableMeta']


def attach_new_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one which
    also initialises the _clones attribute to an empty list.
    """

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        self._clones = []

    cls.__init__ = new_init


class CloneableMeta(type):

    def __new__(metacls, cg_name, bases, clsdict):
        new_cls = super(CloneableMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        attach_new_init_method(new_cls)

        return new_cls
