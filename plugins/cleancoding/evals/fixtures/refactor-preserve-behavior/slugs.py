"""URL slug helpers."""

import re


def mk_slug(s):
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")


def mk_slugs(xs):
    out = []
    for x in xs:
        out.append(mk_slug(x))
    return out
