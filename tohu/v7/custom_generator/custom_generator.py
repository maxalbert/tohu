from ..base import TohuBaseGenerator

__all__ = ["make_new_custom_generator"]


class CustomGenerator:
    def __init__(self):
        self.field_generators = {}

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

    @property
    def fields(self):
        """
        Return
        """
        return list(self.field_generators.keys())


def make_new_custom_generator():
    return CustomGenerator()
