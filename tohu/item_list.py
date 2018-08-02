import io
import logging
import re
import pandas as pd
from operator import attrgetter
from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateSchema

logger = logging.getLogger('tohu')


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


def _extract_schema_if_given(table_name):
    """
    Return a pair (schema, table) derived from the given `table_name`
    (anything before the first '.' if the name contains one; otherwise
    the return value of `schema` is None).

    Examples:

        >>> _extract_schema_if_given('some_schema.my_table')
        ('some_schema', 'my_table')

        >>> _extract_schema_if_given('my_awesome_table')
        (None, 'my_awesome_table')
    """
    pattern = '^(([^.]+)\.)?(.+)$'
    m = re.match(pattern, table_name)
    schema, table_name = m.group(2), m.group(3)
    return schema, table_name


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

    def to_sql(self, url, table_name, *, schema=None, if_exists="fail"):
        """
        Export items as rows in a PostgreSQL table.

        Parameters
        ----------

        url: string
            Connection string to connect to the database.
            Example: "postgresql://postgres@127.0.0.1:5432/testdb"

        table_name: string
            Name of the database table. Note that if this name contains a dot ('.')
            and `schema` is not specified, the first part of the name before the dot
            will be interpreted as the schema name.

        schema : string, optional
            Specify the schema (if database flavor supports this). If None,
            use default schema or derive the schema name from `table_name`.

        if_exists : {'fail', 'do_nothing', 'replace', 'append'}, default 'fail'
            - fail: If table exists, raise an error.
            - do_nothing: If table exists, do nothing and immediately return.
            - replace: If table exists, drop it, recreate it, and insert data.
            - append: If table exists, insert data. Create if does not exist.
        """
        if schema is None:
            schema, table_name = _extract_schema_if_given(table_name)

        engine = create_engine(url)
        ins = inspect(engine)

        if schema is not None and schema not in ins.get_schema_names():
            logger.debug(f"Creating non-existing schema: '{schema}'")
            engine.execute(CreateSchema(schema))

        if table_name in ins.get_table_names(schema=schema) and if_exists == 'do_nothing':
            logger.debug("Table already exists (use if_exists='replace' or if_exists='append' to modify it).")
            return

        if if_exists == 'do_nothing':
            # we handled the 'do nothing' case above; change to an option that pandas will understand
            if_exists = 'fail'

        with engine.begin() as conn:
            self.to_df().to_sql(table_name, conn, schema=schema, index=False, if_exists=if_exists)
