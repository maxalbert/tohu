import io
import pandas as pd
from operator import attrgetter
from sqlalchemy import create_engine


def _generate_csv_header_line(*, header_names, header_prefix='', header=True, sep=',', newline='\n'):
    """
    Helper function to generate a CSV header line depending on
    the combination of arguments provided.
    """
    if isinstance(header, str):  # user-provided header line
        header_line = header + newline
    else:
        if not (header is None or isinstance(header, bool)):
            raise ValueError(f"Invalid value for argument `header`: {header}")
        else:
            if header:
                header_line = header_prefix + sep.join(header_names) + newline
            else:
                header_line = ""
    return header_line



class ItemList:

    def __init__(self, items, N):
        self.items = items if isinstance(items, list) else list(items)
        self.N = N

    def __repr__(self):
        return f"<ItemList containing {self.N} items>"

    def __eq__(self, other):
        return self.items == other

    def __len__(self):
        return self.N

    def __getitem__(self, idx):
        return self.items[idx]

    def __iter__(self):
        return iter(self.items)

    def to_df(self, fields=None):
        if fields is None:
            return pd.DataFrame([x.to_series() for x in self.items])
        else:
            attr_getters = [(field_name, attrgetter(attr_name)) for (field_name, attr_name) in fields.items()]
            return pd.DataFrame([pd.Series({field_name: func(x) for (field_name, func) in attr_getters}) for x in self.items])

    def to_csv(self, filename=None, *, fields=None, append=False, header=True, header_prefix='', sep=',', newline='\n'):
        """
        Parameters
        ----------
        filename: str or None
            The file to which output will be written. By default, any existing content is
            overwritten. Use `append=True` to open the file in append mode instead.
            If filename is None, the generated CSV output is returned instead of written
            to a file.
        fields: dict
            Dictionary which maps output field names to attribute names of the generators.
            Example: `fields={'CSV_COL1': 'field_name_1', 'CSV_COL2': 'field_name_2'}
        append: bool
            If `True`, open the file in 'append' mode to avoid overwriting existing content.
            Default is `False`, i.e. any existing content will be overwritten.
            This argument only has an effect if `filename` is given (i.e. if output happens
            to a file instead of returning a CSV string).
        header: bool or str or None
            If `header=False` or `header=None` then no header line will be written.
            If `header` is a string then this string will be used as the header line.
            If `header=True` then a header line will be automatically generated from
            the field names of the custom generator.
        header_prefix: str
            If `header=True` then the auto-generated header line will be prefixed
            with `header_prefix` (otherwise this argument has no effect). For example,
            set `header_prefix='#'` to make the header line start with '#'. Default: ''
        sep: str
            Field separator to use in the output. Default: ','
        newline: str
            Line terminator to use in the output. Default: '\n'

        Returns
        -------
        The return value depends on the value of `filename`.
        If `filename` is given, writes the output to the file and returns `None`.
        If `filename` is `None`, returns a string containing the CSV output.
        """
        assert isinstance(append, bool)

        if fields is None:
            raise NotImplementedError("TODO: derive field names automatically from the generator which produced this item list")

        header_line = _generate_csv_header_line(header=header, header_prefix=header_prefix, header_names=fields.keys(), sep=sep, newline=newline)

        file_or_string = open(filename, 'a' if append else 'w') if (filename is not None) else io.StringIO()

        retval = None
        attr_getters = [attrgetter(attr_name) for attr_name in fields.values()]
        try:

            file_or_string.write(header_line)

            for x in self.items:
                line = sep.join([format(func(x)) for func in attr_getters]) + newline
                file_or_string.write(line)

            if filename is None:
                retval = file_or_string.getvalue()

        finally:
            file_or_string.close()

        return retval

    def to_sql(self, url, table_name, *, if_exists="fail"):
        """
        Export items as rows in a PostgreSQL table.

        Parameters
        ----------

        url: string
            Connection string to connect to the database.
            Example: "postgresql://postgres@127.0.0.1:5432/testdb"

        table_name: string
            Name of the database table.

        if_exists : {'fail', 'replace', 'append'}, default 'fail'
            - fail: If table exists, raise an error.
            - replace: If table exists, drop it, recreate it, and insert data.
            - append: If table exists, insert data. Create if does not exist.
        """
        engine = create_engine(url)
        with engine.begin() as conn:
            self.to_df().to_sql(table_name, conn, index=False, if_exists=if_exists)
