from mako.template import Template


class CSVFormatter:
    """
    This class is responsible for formatting items to strings
    representing individual rows in a CSV file, and for exporting
    collections of items to CSV files.
    """

    def __init__(self, fmt_dict, sep=","):
        """
        Initialise CSV formatter.

        Parameters
        ----------
        fmt_dict: dict
            Dictionary which maps column names to mako templating
            strings. The column names are used as the headers when
            exporting a collection of items to a CSV file (but are
            ignored when formatting single items).
        sep: string, default ','
            Delimiter between individual fields in each row.
        """
        self.fmt_dict = fmt_dict
        self.sep = sep
        self.default_header_line = "#" + sep.join(fmt_dict.keys()) + "\n"
        self.fmt_template = Template(sep.join(fmt_dict.values()))
        self.line_separator = "\n"

    def format_item(self, item):
        """
        Return a string representation of `item`.

        Parameters
        ----------
        item: namedtuple
            The item to be formatted.
        """
        return self.fmt_template.render(**item._asdict())

    def get_header_line(self, header):
        if isinstance(header, str):
            return header + self.line_separator
        elif header is True:
            return self.default_header_line
        elif header is False:
            return ""
        else:
            raise ValueError("Invalid 'header' argument (must be boolean or string): '{}'".format(header))

    def to_csv(self, items, path_or_buf=None, *, header=True):
        """
        Export items to CSV file.

        Parameters
        ----------
        items: iterable
            The items to export. Each item corresponds to
            one row in the CSV file.
        path_or_buf: string or file handle, default None
            File path or object, if None is provided the
            result is returned as a string.
        header: boolean or list of string, default True
            Write out a header line with column names. If
            a list of string is given it is assumed to be
            aliases for the column names
        """
        csv = self.get_header_line(header)
        for item in items:
            csv += self.format_item(item) + self.line_separator

        if path_or_buf is None:
            return csv
        else:
            if isinstance(path_or_buf, str):
                with open(path_or_buf, 'w') as f:
                    f.write(csv)
            else:
                path_or_buf.write(csv)
