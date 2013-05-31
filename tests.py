from datetime import datetime
import unittest

from intervals import interval, _get_before_inside_after


class TestIntervals(unittest.TestCase):
    def test_init(self):
        interv = interval(1, 2)
        self.assertEqual(interv.subintervals, [(1, 2)])

    def test_init_naught(self):
        interv = interval()
        self.assertEqual(interv.subintervals, [])

    def test_from_intervals(self):
        intervs = [(1, 2), (3, 4), (5, 6)]
        interv = interval._from_intervals(intervs)
        self.assertEqual(interv.subintervals, intervs)
        self.assertIsNot(interv.subintervals, intervs)

    def test_init_one_argument(self):
        self.assertRaises(TypeError, interval, 0)

    def test_init_invalid_intervals(self):
        self.assertRaises(TypeError, interval, 0, -1)
        self.assertRaises(TypeError, interval, 0, 0)

    def test_null_interval(self):
        interv = interval()
        self.assertEqual(interv.subintervals, [])
        self.assertNotIn(1, interv)
        self.assertNotIn(-1, interv)

    def test_contains(self):
        interv = interval(-1, 1)
        self.assertIn(0, interv)
        self.assertIn(-1, interv)
        self.assertIn(1, interv)
        self.assertNotIn(-1.1, interv)
        self.assertNotIn(1.1, interv)

    def test_datetimes(self):
        start = datetime(1, 1, 1, 20, 0)
        end = datetime(1, 1, 1, 23, 30)
        interv = interval(start, end)
        self.assertIn(datetime(1, 1, 1, 23, 0), interv)

    def test_add(self):
        interv = interval(1, 3) + interval(6, 10)
        self.assertEqual(interv.subintervals, [(1, 3), (6, 10)])
        self.assertIn(2, interv)
        self.assertIn(7, interv)
        self.assertNotIn(0, interv)
        self.assertNotIn(4, interv)
        self.assertNotIn(11, interv)

    def test_add_integrated(self):
        i = interval
        # before
        self.assertEqual(
            (i(1, 3) + i(3, 4)).subintervals,
            [(1, 4)])
        # after
        self.assertEqual(
            (i(3, 4) + i(1, 3)).subintervals,
            [(1, 4)])
        # absorb
        self.assertEqual(
            (i(4, 5) + i(1, 10)).subintervals,
            [(1, 10)])
        # absorbed
        self.assertEqual(
            (i(1, 10) + i(4, 5)).subintervals,
            [(1, 10)])

    def test_add_collapses_intervals(self):
        self.assertEqual(
            interval(1, 2) + interval(2, 3),
            interval(1, 3))

    def test__get_before_inside_after(self):
        bif = _get_before_inside_after
        self.assertEqual(
            bif(10, 20, [(11, 12)]),
            ((), [(11, 12)], (), ()))
        self.assertEqual(
            bif(11, 12, [(10, 20)]),
            ((), [], (), (10, 20)))
        self.assertEqual(
            bif(10, 20, [(5, 11), (11, 12), (19, 21)]),
            ((5, 11), [(11, 12)], (19, 21), ()))
        self.assertEqual(
            bif(10, 20, [(5, 10), (11, 12), (20, 21)]),
            ((5, 10), [(11, 12)], (20, 21), ()))

    def test_equity(self):
        self.assertEqual(
            interval(1, 2),
            interval(1, 2))
        self.assertEqual(
            interval(1, 2) + interval(3, 4),
            interval(3, 4) + interval(1, 2))

    def test_equity_datetime(self):
        d, i = datetime, interval

        date_interval_a = i(d(2000, 1, 1), d(2000, 1, 2))
        date_interval_b = i(d(2000, 10, 1), d(2000, 10, 2))

        self.assertEqual(
            date_interval_a + date_interval_b,
            date_interval_b + date_interval_a)

    def test_equity_error(self):
        try:
            interval(1, 4) == 10
        except TypeError as e:
            self.assertIn(repr(int), repr(e))
        else:
            assert False

    def test_repr(self):
        self.assertEqual(
            repr(interval(1, 2)),
            '<interval: [(1, 2)]>')
        self.assertEqual(
            repr(interval()),
            '<interval: null interval>')

    def test_sub(self):
        i = interval

        # absorb
        self.assertEqual(i(2, 5) - i(1, 10), i())

        # reduce before or after
        self.assertEqual(i(1, 10) - i(0, 2), i(2, 10))
        self.assertEqual(i(1, 10) - i(9, 11), i(1, 9))

        # reduce before or after (removing any null-intervals)
        self.assertEqual(i(1, 10) - i(1, 2), i(2, 10))
        self.assertEqual(i(1, 10) - i(9, 10), i(1, 9))

        # split
        self.assertEqual(i(1, 10) - i(2, 3), i(1, 2) + i(3, 10))

        # noop
        self.assertEqual(i(1, 10) - i(10, 11), i(1, 10))
        self.assertEqual(i(1, 10) - i(0, 1), i(1, 10))

    def test_multisub(self):
        i = interval

        self.assertEqual(
            (i(1, 10) + i(11, 20)) - i(9, 12),
            i(1, 9) + i(12, 20))

        self.assertEqual(
            i(1, 10) - (i(1, 2) + i(2, 4)),
            i(4, 10))

        self.assertEqual(
            (i(1, 2) + i(2, 4)) - i(1, 10),
            i())

    def test_len(self):
        interv = interval(1, 2) + interval(3, 4)
        self.assertEqual(interv.length(), 2)

        self.assertAlmostEqual(interval(10.0, 20.1).length(), 10.1)

        interv = interval(datetime(1, 1, 1), datetime(1, 1, 10))
        self.assertEqual(interv.length().days, 9)


if __name__ == '__main__':
    unittest.main()
