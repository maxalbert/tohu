from mako.template import Template


class CSVFormatter:
    """
    This class formats an individual record or
    a sequence of records as CSV output.
    """

    def __init__(self, *, fields=None, fmt_str=None, header=None):
        """
        Initialise CSV formatter.
        Either `fields` or `fmt_str` (but not both) must be specified.

        If `fields` is given (which must be a dictionary of column names
        and associated format strings) then a header line is automatically
        created from the column names, i.e. the keys of the dictionary.
        However, this can be overriden by passing the `header` argument.

        Parameters
        ----------
        fmt_str: string
            Formatting string that specifies how an
            individual record should be formatted.

        header: string (optional)
            Header line to be used in the CSV output.
        """
        self.line_separator = "\n"
        self.sep = ","

        if fields is not None:
            if header is None or header is True:
                self.header = "#" + self.sep.join(fields.keys()) + self.line_separator
            elif header is False:
                self.header = ""
            elif isinstance(header, str):
                self.header = header + self.line_separator
            else:
                raise ValueError("Invalid 'header' argument: '{}' (must be string or boolean or None).".format(header))

            fmt_str = self.sep.join(fields.values())
            self.template = Template(fmt_str + self.line_separator)
        elif fmt_str is not None:
            if header is True:
                raise ValueError("Cannot automatically derive header. Please provide an explicit header string.")
            self.header = "" if (header is None or header is False) else (header + self.line_separator)
            self.template = Template(fmt_str + self.line_separator)
        else:
            raise ValueError("Either `fields` or `fmt_str` must be given.")

    def format_records(self, records):
        """
        Return CSV string of
        """
        s = self.header
        for r in records:
            s += self.template.render(**r._asdict())
        return s