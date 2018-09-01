__all__ = ['CloneableMeta']


class CloneableMeta(type):

    def __new__(metacls, cg_name, bases, clsdict):
        new_cls = super(CloneableMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        return new_cls