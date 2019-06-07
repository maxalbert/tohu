from ..base import TohuBaseGenerator
from .tohu_items_class import make_tohu_items_class

__all__ = ["make_new_custom_generator"]


class MissingTohuItemsCls:
    def __init__(self):
        self.is_unset = True

    def __call__(self, *args, **kwargs):
        raise RuntimeError("You must call `make_tohu_items_class` on the custom generator before generating items.")


class CustomGenerator(TohuBaseGenerator):
    def __init__(self):
        super().__init__()
        self.field_generators = {}
        self.tohu_items_cls = MissingTohuItemsCls()

    def __next__(self):
        field_values = {field_name: next(field_gen) for field_name, field_gen in self.field_generators.items()}
        return self.tohu_items_cls(**field_values)

    def reset(self, seed):
        super().reset(seed)
        for field_name, field_gen in self.field_generators.items():
            field_gen.reset(next(self.seed_generator))

    def spawn(self):
        new_obj = CustomGenerator()
        for field_name, field_gen in self.field_generators.items():
            new_obj.add_field_generator(field_name, field_gen.parent)
        new_obj._set_state_from(self)
        return new_obj

    def _set_state_from(self, other):
        super()._set_state_from(other)

    def add_field_generator(self, name: str, generator: TohuBaseGenerator):
        """
        Parameters
        ----------
        name : str
            Field name associated with the generator.
        generator : TohuBaseGenerator
            The generator to be added.
        """
        self.field_generators[name] = generator.clone()

    def make_tohu_items_class(self, cls_name):
        self.tohu_items_cls = make_tohu_items_class(cls_name, self.fields)

    @property
    def fields(self):
        """
        Return
        """
        return list(self.field_generators.keys())


def make_new_custom_generator():
    return CustomGenerator()