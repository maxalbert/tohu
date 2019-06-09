import inspect
import re

from .apply import Apply


class fstr(Apply):
    """
    Helper function for easy formatting of tohu generators.

    Usage example:

        >>> g1 = Integer(100, 200)
        >>> g2 = Integer(300, 400)
        >>> g3 = g1 + g2
        >>> h = fstr('{g1} + {g2} = {g3}')
        >>> print(next(h))
        122 + 338 = 460
        >>> print(next(h))
        165 + 325 = 490
    """

    def __init__(self, spec):

        # FIXME: this pattern is not yet compatible with the full f-string spec.
        # For example, it doesn't recognise double '{{' and '}}' (for escaping).
        # Also it would be awesome if we could parse arbitrary expressions inside
        # the curly braces.
        pattern = '{([^}:]+)(:.*)?}'

        gen_names = [gen_name for (gen_name, _) in re.findall(pattern, spec)]

        # TODO: do we ever need to store and pass in the original namespace when spawning generators?
        namespace = inspect.currentframe().f_back.f_globals
        namespace.update(inspect.currentframe().f_back.f_locals)

        gens = {name: namespace[name] for name in gen_names}

        def format_items(**kwargs):
            return spec.format(**kwargs)

        super().__init__(format_items, **gens)