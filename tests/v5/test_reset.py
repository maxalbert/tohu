from unittest.mock import Mock


def test_reset_automatically_resets_internal_seed_generator(exemplar_generators):
    """
    Calling reset on a generator automatically calls reset on its internal seed generator with the same seed.
    """
    for g in exemplar_generators:
        g.seed_generator.reset = Mock()

        g.reset(seed=12345)
        g.seed_generator.reset.assert_called_once_with(12345)

        g.reset(seed=99999)
        g.seed_generator.reset.assert_called_with(99999)