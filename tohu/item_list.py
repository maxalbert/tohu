import pandas as pd
from operator import attrgetter


class ItemList:

    def __init__(self, items, N):
        assert isinstance(items, list)
        self.items = items
        self.N = N

    def __repr__(self):
        return f"<ItemList containing {self.N} items>"

    def __len__(self):
        return self.N

    def __getitem__(self, idx):
        return self.items[idx]

    def __iter__(self):
        return iter(self.items)

    def _get_output_items(self, fields):
        get_attr_funcs = [(field_name, attrgetter(attr_name)) for (field_name, attr_name) in fields.items()]
        return [pd.Series({field_name: func(x) for (field_name, func) in get_attr_funcs}) for x in self.items]

    def to_df(self, fields):
        return pd.DataFrame(self._get_output_items(fields))

    def to_csv(self, fields, *, filename, mode='w', sep=',', header=True, header_prefix='#'):
        header_names = [name for name in fields.keys()]
        attr_getters = [attrgetter(attr_name) for attr_name in fields.values()]
        newline = '\n'

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

        with open(filename, mode) as f:
            f.write(header_line)

            for x in self.items:
                line = sep.join([str(func(x)) for func in attr_getters]) + newline
                f.write(line)
