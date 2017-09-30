from mako.template import Template

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

    def __init__(self, items):
        self.items = list(items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return "<ItemCollection of length {}>".format(len(self))

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def write(self, filename, fields, sep=",", line_separator="\n"):
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
        line_separator: string
            Line separatore. Default: '\n' (= newline).
        """

        template = make_mako_template(fields, sep=sep, line_separator=line_separator)
        header_line = "#" + sep.join(fields.keys()) + line_separator

        with open(filename, 'w') as f:
            f.write(header_line)
            for item in self.items:
                f.write(template.render(item=item))