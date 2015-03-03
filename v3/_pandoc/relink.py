#!/usr/bin/env python

"""
Pandoc filter to convert all .md links to .md.rst
"""

from pandocfilters import toJSONFilter, Link


def relink(key, value, format, meta):
    if key == 'Link':
        print(value)
        value[1][0] = value[1][0].replace(".md", ".md.rst")
        return Link(value[0], value[1])

if __name__ == "__main__":
    toJSONFilter(relink)
