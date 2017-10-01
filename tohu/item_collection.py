from mako.template import Template
from .csv_formatter import CSVFormatter

__all__ = ['ItemCollection']


def wrap_field_for_mako(fld):
    """
    Helper function which wraps a field name such as 'foo'
    into the mako expression '${item.foo}'.
    """
    return "${item." + fld + "}"


def make_mako_template(fields, *, sep=",", line_separator="\n"):
    """
    Helper function. Returns a mako Template which renders
    an individual item to a string.
    """
    field_strings = [wrap_field_for_mako(x) for x in fields.values()]
    return Template(sep.join(field_strings) + line_separator)


class ItemCollection:
    """
    Class representing a collection of items.
    """

    def __init__(self, items, N):
        self.items = items
        self.N = N

    def __len__(self):
        return self.N

    def __repr__(self):
        return "<ItemCollection of length {}>".format(len(self))

    def __iter__(self):
        return iter(self.items)

    def to_csv(self, filename, *, fmt_str=None, fields=None, sep=",", header=None):
        """
        Write item collection to CSV file.

        Parameters
        ----------
        filename: string
            Name of the output CSV file.
        fields: dict
            Dictionary of the form {<column_name>: <field_name>, ...}
        sep: string
            Field separator. Default: ','
        """

        formatter = CSVFormatter(fmt_str=fmt_str, fields=fields, sep=sep, header=header)
        formatter.write(filename, self.items)
