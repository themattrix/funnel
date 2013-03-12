def split_last(seq):
    """
    Returns a tuple containing: (all-items-except-last, last-item)
    """
    return seq[:-1], seq[-1]


def tear(seq, fn):
    """
    Splits the items in 'seq' into two lists: the first containing items for which 'fn' evaluates to True, and the
    second for which it does not.
    """
    t = []
    f = []
    for s in seq:
        if fn(s):
            t.append(s)
        else:
            f.append(s)
    return t, f
