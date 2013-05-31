from itertools import imap
import operator


class interval(object):
    """An interval. Boolean operations, a length function and checking
    whether a value is within the interval.

    Because of the boolean operations being able to split the interval
    into several, the class actually operates on multiple intervals.

    The class works with any type, but you will want to make sure that
    all values you use in a single instance of `interval` are of the
    same type. So far it's tested with ints, floats and datetimes, but
    it should work with intervals of strings.

    Here is an interval between the integers 1 and 5:
    >>> interv = interval(1, 5)
    >>> interv.length()
    4
    >>> 3 in interv
    True

    >>> two_intervals = interv + interval(6, 10)
    >>> 3 in two_intervals
    True
    >>> 5.5 in two_intervals
    False
    >>> 7 in two_intervals
    True
    >>> two_intervals.length()
    8

    """

    def __init__(self, start=None, end=None):
        """Initialize an interval.

        >>> interval()
        <interval: null interval>
        >>> interval(1, 5)
        <interval: [(1, 5)]>

        """

        self.subintervals = []
        if start is None and end is None:
            return

        if start is not None and end is not None:
            if start >= end:
                raise TypeError('invalid interval')
            self.subintervals.append((start, end))
        else:
            raise TypeError(
                'must supply both start and end values, or neither')

    @classmethod
    def _from_intervals(cls, intervals):
        """Construct an interval from a list of intervals

        """

        instance = cls()
        instance.subintervals = list(intervals)
        return instance

    def length(self):
        """Compute the length of the interval by adding up all 
        subintervals' lengths.

        >>> interval(1, 5).length()
        4
        >>> (interval(0.1, 0.2) + interval(1, 5)).length()
        4.1

        """

        def differences_of_each_interval():
            for start, end in self.subintervals:
                yield end - start

        return reduce(operator.add, differences_of_each_interval())

    def __eq__(self, oth):
        """Equality operation, to compare with another interval

        """

        if type(oth) != interval:
            raise TypeError(
                'Cannot compare an interval to %r' % type(oth))

        equality = imap(
            operator.eq,
            sorted(self.subintervals),
            sorted(oth.subintervals))

        return all(equality)

    def __add__(self, oth):
        """Boolean join of two intervals. All work done in
        _add_one_interval.

        """

        new = interval._from_intervals(self.subintervals)

        for start, end in oth.subintervals:
            new._add_one_interval(start, end)

        return new

    def _add_one_interval(self, start, end):
        before, inside, after, absorbed = _get_before_inside_after(
            start, end, self.subintervals)

        if absorbed:
            return  # cancel insert

        for pair in inside:
            self._remove_existing(pair)

        if before:
            to_replace = self.subintervals.index(before)
            s, e = self.subintervals[to_replace]
            selfstart, selfend = min((s, start)), max((e, end))
            self.subintervals[to_replace] = selfstart, selfend

        if after:
            to_replace = self.subintervals.index(after)
            s, e = self.subintervals[to_replace]
            selfstart, selfend = min((s, start)), max((e, end))
            self.subintervals[to_replace] = selfstart, selfend

        if not before and not after:
            self.subintervals.append((start, end))

    def __sub__(self, oth):
        """Boolean subtraction of intervals. All work done in
        _remove_one_interval. Returns a new interval.

        """

        new = interval._from_intervals(self.subintervals)

        for start, end in oth.subintervals:
            new._remove_one_interval(start, end)

        return new

    def _remove_one_interval(self, start, end):
        def subtract_inside(outer, inner):
            """When `inner` is completely inside `outer`, boolean
            subtraction will produce 2 new intervals. Return them.

            Example:
                 inner:        [inn]
                 outer:  [outerouterouter]
                result:  [first]   [secnd]

            Returns the "first" and "second" intervals as seen above.

            """

            start, end = outer
            mid1, mid2 = inner

            return (start, mid1), (mid2, end)

        before, inside, after, absorbed = _get_before_inside_after(
            start, end, self.subintervals)

        remove = self._remove_existing

        if absorbed:
            remove(absorbed)
            new_intervals = subtract_inside(absorbed, (start, end))
            for start, end in new_intervals:
                if start != end:
                    self.subintervals.append((start, end))

        for pair in inside + [before, after]:
            remove(pair)

    def _remove_existing(self, pair):
        """Remove an item we know is either inside our list, or ().

        """

        if pair:
            self.subintervals.remove(pair)

    def __contains__(self, item):
        """Returns if an item is inside the collection.

        """

        for start, end in self.subintervals:
            if start <= item <= end:
                return True

    def __repr__(self):
        subs = self.subintervals
        if len(subs) == 0:
            return '<interval: null interval>'
        else:
            return '<interval: %r>' % subs


def _get_before_inside_after(start, end, intervals):
    """Get intervals that are intersecting before, inside and
    intersecting after the given interval, and whether the given
    interval is contained in one of the intervals.

    Example when the interval is bigger than the others:

    given interval:       [                          ]
    intervals:      [<before>]  [<inside>][<inside>][<after>]

    We see here what is "before"


    Example when the interval is absorbed by an existing interval:

    given interval:        [  ]
    intervals:          [<absorbed>]


    This function is used when we want to do boolean operations on
    several intervals. In such a case, we want to know how each
    interval interacts with others.

    """

    before = ()
    inside = []
    after = ()
    absorbed = ()

    for istart, iend in intervals:
        if istart > end or iend < start:
            pass
        elif istart > start and iend < end:
            inside.append((istart, iend))
        elif istart <= start <= end <= iend:
            absorbed = istart, iend
            break
        elif iend > end:
            after = (istart, iend)
        elif istart < start:
            before = (istart, iend)

    return before, inside, after, absorbed

if __name__ == '__main__':
    import doctest
    doctest.testmod()