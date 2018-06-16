import pandas as pd
import re
import sys
from collections import namedtuple
from random import Random

from .generators import BaseGenerator, SeedGenerator
from .csv_formatter import CSVFormatter
from .csv_formatter_v1 import CSVFormatterV1

__all__ = ["CustomGenerator"]


def make_item_class(cg):
    """
    Parameters
    ----------
    cg: CustomGenerator
    """

    clsname = cg.get_item_class_name()
    attr_names = cg.field_gens.keys()
    item_cls = namedtuple(clsname, attr_names)

    cg.fmt_dict = {name: "${" + name + "}" for name in cg.field_gens.keys()}
    cg.csvformatter = CSVFormatterV1(cg.fmt_dict)
    item_cls.__format__ = lambda item, fmt: cg.csvformatter.format_item(item)

    return item_cls


class CustomGeneratorMeta(type):
    def __new__(metacls, cg_name, bases, clsdict):
        gen_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        orig_init = gen_cls.__init__

        def gen_init(self, *args, **kwargs):
            seed = kwargs.pop('seed', None)

            # Call original __init__ function to make sure all generator attributes are defined
            orig_init(self, *args, **kwargs)

            self.field_gens = self._calculate_field_gens()
            self.item_cls = make_item_class(self)
            self.seed_generator = SeedGenerator()
            self.reset(seed)

        gen_cls.__init__ = gen_init
        return gen_cls


class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):

    def get_item_class_name(self):
        """
        Return the first part of the class name of this custom generator
        will be used for the namedtuple items produced by this generator.

        Examples:
            FoobarGenerator -> Foobar
            QuuxGenerator   -> Quux
        """
        return re.match('^(.*)Generator$', self.__class__.__name__).group(1)

    def reset(self, seed=None):
        """
        Reset generator using the given seed (unless seed is None, in which case this is a no-op).
        """
        # Reset the seed generator
        if seed is not None:
            self.seed_generator.reset(seed)

            # Reset each constituent generator with a new seed
            # produced by the seed generator.
            for g, x in zip(self.field_gens.values(), self.seed_generator):
                g.reset(x)

    def _calculate_field_gens(self):
        clsdict = self.__class__.__dict__
        instdict = self.__dict__
        return {name: gen._spawn() for name, gen in dict(**clsdict, **instdict).items() if isinstance(gen, BaseGenerator)}

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    def to_csv(self, path_or_buf=None, *, N, seed=None, fields=None, fmt_str=None, header=None, progressbar=True):
        """
        Generate N items and return the resulting CSV string or output to a file.

        Parameters
        ----------
        path_or_buf: string or file handle, default None
            File path or object. If None is provided the result
            is returned as a string.
        N: integer
            Number of items to generate.
        seed: integer (optional)
            Seed with which to initialise random generator.
        progressbar: boolean
            Whether to display a progressbar during item generation.

        The remaining arguments `fields`, `fmt_str`, `header`
        are passed on to CSVFormatter.
        """
        if fmt_str is None:
            fmt_str = getattr(self, 'CSV_FMT_STR', None)
        if fields is None and fmt_str is None:
            fields = getattr(self, 'CSV_FIELDS', self.fmt_dict)
        if header is None:
            header = getattr(self, 'CSV_HEADER', None)

        formatter = CSVFormatter(fmt_str=fmt_str, fields=fields, header=header)
        return formatter.to_csv(self.generate(N, seed=seed, progressbar=progressbar), path_or_buf=path_or_buf)

    def to_df(self, *, N, seed=None):
        """
        Return pandas DataFrame containing N items produced by this generator.
        """
        return self.generate(N, seed=seed).to_df()

    def to_psql(self, url, table_name, N, *, if_exists='fail', seed=None):
        """
        Generate N items and export them as rows in a PostgreSQL table.

        Parameters
        ----------

        url: string
            Connection string to connect to the database.
            Example: "postgresql://postgres@127.0.0.1:5432/testdb"

        table_name: string
            Name of the database table.

        N: integer
            Number of items to export.

        if_exists : {'fail', 'replace', 'append'}, default 'fail'
            - fail: If table exists, raise an error.
            - replace: If table exists, drop it, recreate it, and insert data.
            - append: If table exists, insert data. Create if does not exist.

        seed: integer (optional)
            Seed with which to initialise random generator.
        """
        self.generate(N, seed=seed).to_psql(url, table_name, if_exists=if_exists)
