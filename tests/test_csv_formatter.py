from collections import namedtuple
import pytest
import textwrap
from .context import tohu
from tohu.csv_formatter import CSVFormatter


class TestCSVFormatter:

    @classmethod
    def setup(cls):
        """
        Create a few records of type `Foobar` to be used in tests.
        """
        Foobar = namedtuple("Foobar", ["aaa", "bbb", "ccc"])
        cls.records = [
            Foobar(aaa='foobar_01', bbb=8, ccc='4898FE19'),
            Foobar(aaa='foobar_02', bbb=160, ccc='5825D187'),
            Foobar(aaa='foobar_03', bbb=99, ccc='3648A436')
        ]

    def test_init_with_field_dict(self):
        """
        Test that CSVFormatter can be initialised with a dictionary of field names and their format strings.
        """
        fields = {
            'Column 1': 'a=${aaa}',
            'Column 2': 'b=${bbb}',
            'Column 3': 'c=${ccc}',
        }
        csv_formatter = CSVFormatter(fields=fields)
        csv = csv_formatter.format_records(self.records)

        csv_expected = textwrap.dedent("""\
            #Column 1,Column 2,Column 3
            a=foobar_01,b=8,c=4898FE19
            a=foobar_02,b=160,c=5825D187
            a=foobar_03,b=99,c=3648A436
            """)

        assert csv == csv_expected

    def test_init_with_field_dict_and_custom_field_separator(self):
        """
        Test that custom field_separator is taken into account.
        """
        fields = {
            'Column 1': 'a=${aaa}',
            'Column 2': 'b=${bbb}',
            'Column 3': 'c=${ccc}',
        }
        csv_formatter = CSVFormatter(fields=fields, sep=" || ")
        csv = csv_formatter.format_records(self.records)

        csv_expected = textwrap.dedent("""\
            #Column 1 || Column 2 || Column 3
            a=foobar_01 || b=8 || c=4898FE19
            a=foobar_02 || b=160 || c=5825D187
            a=foobar_03 || b=99 || c=3648A436
            """)

        assert csv == csv_expected

    def test_init_with_format_string(self):
        """
        Test that CSVFormatter can be initialised with a formatting string.
        """
        fmt_str = "a=${aaa}, b: ${bbb}, c has value ${ccc}"
        csv_formatter = CSVFormatter(fmt_str=fmt_str)
        csv = csv_formatter.format_records(self.records)

        csv_expected = textwrap.dedent("""\
            a=foobar_01, b: 8, c has value 4898FE19
            a=foobar_02, b: 160, c has value 5825D187
            a=foobar_03, b: 99, c has value 3648A436
            """)

        assert csv == csv_expected

    def test_format_records_multiline_format_string(self):
        """
        Test that formatting a few records to CSV using a multiline format string produces the expected result.
        """

        header = "#Column_1,Column_2,LineNoOfRecord"
        fmt_str = "a=${aaa},b=${bbb},first_line\na=${aaa},c=${ccc},second_line"
        csv_formatter = CSVFormatter(fmt_str=fmt_str, header=header)
        csv = csv_formatter.format_records(self.records)

        csv_expected = textwrap.dedent("""\
            #Column_1,Column_2,LineNoOfRecord
            a=foobar_01,b=8,first_line
            a=foobar_01,c=4898FE19,second_line
            a=foobar_02,b=160,first_line
            a=foobar_02,c=5825D187,second_line
            a=foobar_03,b=99,first_line
            a=foobar_03,c=3648A436,second_line
            """)

        assert csv == csv_expected

    def test_write_csv_file(self, tmpdir):
        """
        Test that writing records to a CSV file produces the expected result.
        """
        filename = tmpdir.join("output.csv").strpath

        csv_formatter = CSVFormatter(fmt_str="${aaa},${bbb},${ccc}", header="# Custom header line")
        csv_formatter.write(filename, self.records)

        csv = open(filename).read()
        csv_expected = textwrap.dedent("""\
            # Custom header line
            foobar_01,8,4898FE19
            foobar_02,160,5825D187
            foobar_03,99,3648A436
            """)

        assert csv == csv_expected

    def test_subdirectories_are_created_if_necessary(self, tmpdir):
        """
        Test that
        """
        filename = tmpdir.join("foo/bar/output.csv").strpath

        assert not tmpdir.join("foo").exists()
        assert not tmpdir.join("foo/bar").exists()

        csv_formatter = CSVFormatter(fmt_str="${aaa},${bbb},${ccc}", header="# Custom header line")
        csv_formatter.write(filename, self.records)

        assert tmpdir.join("foo").exists()
        assert tmpdir.join("foo/bar").exists()

        csv = open(filename).read()
        csv_expected = textwrap.dedent("""\
            # Custom header line
            foobar_01,8,4898FE19
            foobar_02,160,5825D187
            foobar_03,99,3648A436
            """)

        assert csv == csv_expected



class TestCSVFormatterHeaderLine:
    """
    This class tests the various combinations of initialising
    a CSV formatter and the resulting header line of the
    generated CSV.
    """

    @classmethod
    def setup_class(cls):
        cls.fields = {
            "Column 1": "${}",
            "Column 2": "${}",
            "Column 3": "${}",
        }

    def test_init_with_field_dict_and_no_header_argument(self):
        formatter = CSVFormatter(fields=self.fields, header=None)
        assert formatter.format_records(records=[]) == "#Column 1,Column 2,Column 3\n"

    def test_init_with_field_dict_and_header_True(self):
        formatter = CSVFormatter(fields=self.fields, header=True)
        assert formatter.format_records(records=[]) == "#Column 1,Column 2,Column 3\n"

    def test_init_with_field_dict_and_header_False(self):
        formatter = CSVFormatter(fields=self.fields, header=False)
        assert formatter.format_records(records=[]) == ""

    def test_init_with_field_dict_and_custom_header(self):
        formatter = CSVFormatter(fields=self.fields, header="# This is a custom header line")
        assert formatter.format_records(records=[]) == "# This is a custom header line\n"

    def test_init_with_field_dict_and_custom_separator(self):
        formatter = CSVFormatter(fields=self.fields, sep=" || ", header=True)
        assert formatter.format_records(records=[]) == "#Column 1 || Column 2 || Column 3\n"

    def test_init_with_format_str_and_no_header_argument(self):
        formatter = CSVFormatter(fmt_str="", header=None)
        assert formatter.format_records(records=[]) == ""

    def test_init_with_format_str_and_header_False(self):
        formatter = CSVFormatter(fmt_str="", header=False)
        assert formatter.format_records(records=[]) == ""

    def test_init_with_format_str_and_custom_header(self):
        formatter = CSVFormatter(fmt_str="", header="# This is a custom header line")
        assert formatter.format_records(records=[]) == "# This is a custom header line\n"

    def test_init_with_format_str_and_header_True_raises_error(self):
        """
        This should raise an error because the header can't be automatically derived from the `fmt_str` argument.
        """
        with pytest.raises(ValueError):
            _ = CSVFormatter(fmt_str="", header=True)
