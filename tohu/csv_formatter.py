import os
from mako.template import Template


class CSVFormatter:
    """
    This class formats an individual record or
    a sequence of records as CSV output.
    """

    def __init__(self, *, fields=None, fmt_str=None, sep=",", header=None):
        """
        Initialise CSV formatter.

        Either `fields` or `fmt_str` must be specified (but not both).

        If `fields` is given (which must be a dictionary of column names
        and associated format strings) then a header line is automatically
        created from the column names, i.e. the keys of the dictionary.
        However, this can be overriden by passing the `header` argument.

        Parameters
        ----------
        fmt_str: string
            Formatting string that specifies how an
            individual record should be formatted.

        sep: string
            Field separator. Default: ','

        header: string (optional)
            Header line to be used in the CSV output.
        """
        self.line_separator = "\n"
        self.sep = sep

        if fields is not None:
            if header is None or header is True:
                self.header_line = "#" + self.sep.join(fields.keys()) + self.line_separator
            elif header is False:
                self.header_line = ""
            elif isinstance(header, str):
                self.header_line = header + self.line_separator
            else:
                raise ValueError("Invalid 'header' argument: '{}' (must be string or boolean or None).".format(header))

            fmt_str = self.sep.join(fields.values())
            self.template = Template(fmt_str + self.line_separator)
        elif fmt_str is not None:
            if header is True:
                raise ValueError("Cannot automatically derive header. Please provide an explicit header string.")
            self.header_line = "" if (header is None or header is False) else (header + self.line_separator)
            self.template = Template(fmt_str + self.line_separator)
        else:
            raise ValueError("Either `fields` or `fmt_str` must be given.")

    def format_record(self, record):
        """
        Return formatted string representing the individual record.
        """
        return self.template.render(**record._asdict())

    def format_records(self, records):
        """
        Return CSV string of
        """
        s = self.header_line
        for r in records:
            s += self.template.render(**r._asdict())
        return s

    def write(self, filename, items):
        """
        Write items to file.
        """
        dirname = os.path.dirname(filename)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(filename, 'w') as f:
            f.write(self.header_line)
            for item in items:
                f.write(self.format_record(item))