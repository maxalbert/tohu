from .context import tohu
from tohu.v7.primitive_generators import Integer, Incremental
from tohu.v7.derived_generators import Apply, fstr


def test_apply_generator():
    func = lambda x: x * 101
    g = Integer(10, 99)
    h = Apply(func, g)

    g.reset(seed=99999)
    items_g_expected = [30, 34, 80, 57, 82, 29, 77, 94, 67, 43, 79, 46, 97, 94, 73]
    items_h_expected = [3030, 3434, 8080, 5757, 8282, 2929, 7777, 9494, 6767, 4343, 7979, 4646, 9797, 9494, 7373]

    assert items_g_expected == g.generate(num=15)
    assert items_h_expected == h.generate(num=15)

    func = lambda x, y: x * 100 + y
    a = Integer(10, 99)
    b = Integer(10, 99)
    c = Apply(func, a, b)

    a.reset(seed=11111)
    b.reset(seed=22222)
    items_a_expected = [73, 81, 52, 50, 31, 56, 90, 12, 87, 51, 67, 46, 63, 78, 63]
    items_b_expected = [18, 76, 74, 73, 66, 55, 80, 24, 80, 77, 63, 82, 46, 63, 92]
    items_c_expected = [7318, 8176, 5274, 5073, 3166, 5655, 9080, 1224, 8780, 5177, 6763, 4682, 6346, 7863, 6392]

    assert items_a_expected == a.generate(num=15)
    assert items_b_expected == b.generate(num=15)
    assert items_c_expected == c.generate(num=15)


def test_fstr():
    g1 = Incremental(start=1)
    g2 = Integer(1, 20)
    h = fstr("#{g1}: {g2:.1f}")

    g1.reset(seed=11111)
    g2.reset(seed=22222)

    items_g1_expected = [1, 2, 3, 4, 5, 6, 7, 8]
    items_g2_expected = [3, 17, 17, 16, 15, 12, 18, 4]
    items_h_expected = ["#1: 3.0", "#2: 17.0", "#3: 17.0", "#4: 16.0", "#5: 15.0", "#6: 12.0", "#7: 18.0", "#8: 4.0"]

    assert items_g1_expected == g1.generate(num=8)
    assert items_g2_expected == g2.generate(num=8)
    assert items_h_expected == h.generate(num=8)
