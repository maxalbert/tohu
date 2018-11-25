from .base import TohuBaseGenerator
from .utils import make_tohu_item_class

__all__ = ['CustomGenerator']


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.orig_args = args
        self.orig_kwargs = kwargs

        self._set_tohu_item_class()

    def _set_tohu_item_class(self):
        #self.tohu_item_cls = make_tohu_item_class(self.__tohu_items_name__, self.field_names)
        pass

    def __next__(self):
        # field_values = [next(g) for g in self.field_generators.values()]
        # return self.tohu_item_cls(*field_values)
        return None

    def reset(self, seed):
        super().reset(seed)
        # for gen in self.field_generators.values():
        #     gen.reset(next(self.seed_generator))

    def spawn(self):
        new_obj = self.__class__(*self.orig_args, **self.orig_kwargs)
        new_obj._set_random_state_from(self)

        # # Explicitly set item_cls. This is necessary because due to
        # # the way in which `attr` works, explicit comparisons between
        # # generated items will return False even though they contain
        # # the same elements (because the underlying attr classes are
        # # different, so attr plays it safe).
        # new_obj.tohu_item_cls = self.tohu_item_cls

        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)

        # # TODO: should also set random state for unnamed field generators
        # #        (these can occur in chains of derived generators)
        # for name in self.field_generators.keys():
        #     self.field_generators[name]._set_random_state_from(other.field_generators[name])
