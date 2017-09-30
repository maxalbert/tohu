import pytest
import textwrap
from collections import namedtuple
from tohu.csv_formatter_v1 import CSVFormatterV1


@pytest.fixture
def csvfmt(scope="module"):
    return CSVFormatterV1(
        {"Column 1": "a=${a}",
         "Column 2": "b: ${b}",
         "Column 3": "c has value ${c}"
         })


class TestCSVFormatterV1:

    def setup(self):
        Foobar = namedtuple("Foobar", ["a", "b", "c"])
        self.item1 = Foobar(1234, "quux_01", 9.8765)
        self.item2 = Foobar(5678, "quux_02", 2.2222)
        self.items = [self.item1, self.item2]

    def test_format_single_item(self, csvfmt):
        """
        Test that formatting a single item produces the expected string.
        """
        assert csvfmt.format_item(self.item1) == "a=1234,b: quux_01,c has value 9.8765"
        assert csvfmt.format_item(self.item2) == "a=5678,b: quux_02,c has value 2.2222"

    def test_default_csv_formatting(self, csvfmt):
        """
        Test that formatting multiple items produces the expected CSV string.
        """
        expected_csv = textwrap.dedent("""\
            #Column 1,Column 2,Column 3
            a=1234,b: quux_01,c has value 9.8765
            a=5678,b: quux_02,c has value 2.2222
            """)

        csv = csvfmt.to_csv(self.items)

        assert csv == expected_csv

    def test_csv_formatting_without_header_line(self, csvfmt):
        """
        Test that `header=False` produces the expected CSV string (without header line).
        """
        expected_csv = textwrap.dedent("""\
            a=1234,b: quux_01,c has value 9.8765
            a=5678,b: quux_02,c has value 2.2222
            """)

        csv = csvfmt.to_csv(self.items, header=False)

        assert csv == expected_csv

    def test_csv_formatting_with_custom_header_line(self, csvfmt):
        """
        Test that passing a string as 'header' argument uses this string for the header line.
        """
        expected_csv = textwrap.dedent("""\
            # This is a custom header line
            a=1234,b: quux_01,c has value 9.8765
            a=5678,b: quux_02,c has value 2.2222
            """)

        csv = csvfmt.to_csv(self.items, header="# This is a custom header line")

        assert csv == expected_csv

    def test_custom_separator(self):
        """
        Test that the `sep` argument is used as field separator.
        """
        csvfmt = CSVFormatterV1(
            {"Column 1": "a=${a}",
             "Column 2": "b: ${b}",
             "Column 3": "c has value ${c}"
             },
            sep=" || ")

        expected_csv = textwrap.dedent("""\
            #Column 1 || Column 2 || Column 3
            a=1234 || b: quux_01 || c has value 9.8765
            a=5678 || b: quux_02 || c has value 2.2222
            """)

        csv = csvfmt.to_csv(self.items)

        assert csv == expected_csv

    def test_csv_export_to_file_with_given_name(self, csvfmt, tmpdir):
        """
        Test that passing the `path_or_buf` argument exports to the given file.
        """
        expected_csv = textwrap.dedent("""\
            #Column 1,Column 2,Column 3
            a=1234,b: quux_01,c has value 9.8765
            a=5678,b: quux_02,c has value 2.2222
            """)

        filename = tmpdir.join("output.txt")
        csvfmt.to_csv(self.items, filename)
        assert open(filename).read() == expected_csv

    def test_csv_export_to_file_with_given_filehandle(self, csvfmt, tmpdir):
        """
        Test that passing the `path_or_buf` argument exports to the given file.
        """
        expected_csv = textwrap.dedent("""\
            #Column 1,Column 2,Column 3
            a=1234,b: quux_01,c has value 9.8765
            a=5678,b: quux_02,c has value 2.2222
            """)

        filename = tmpdir.join("output.txt")
        fh = open(filename, 'w')
        csvfmt.to_csv(self.items, fh)
        fh.close()
        assert open(filename, 'r').read() == expected_csv
