#!/usr/bin/env python3
"""
Updates ctable.c with translation table information
built from the 'transtab' database.

Derived from translitcodec's update_table.py

:copyright: the translitcodec authors and developers, see AUTHORS.
:license: MIT, see LICENSE for more details.
"""
import sys, os, csv, string

csv.register_dialect("transtab", delimiter=";")


def read_tables(paths=["transtab/transtab", "transtab.extra"]):
    long, short, single = {}, {}, {}

    for path in paths:
        with open(path) as t:
            for line in t.readlines():
                if not line.startswith("<"):
                    continue
                from_spec, raw_to = line.strip().split(" ", 1)
                from_ord = int(from_spec[2:-1], 16)
                if from_ord <= 128:
                    continue

                raw = next(csv.reader([raw_to], "transtab"))
                long_char = _unpack_uchrs(raw[0])
                if len(raw) < 2:
                    short_char = long_char
                else:
                    short_char = _unpack_uchrs(raw[1])

                long[from_ord] = long_char
                short[from_ord] = short_char
                if len(short_char) == 1:
                    single[from_ord] = short_char
    return long, short, single


def _unpack_uchrs(packed):
    chunks = packed.replace("<U", " ").strip().split()
    return u"".join(chr(int(spec[:-1], 16)) for spec in chunks)


def binary_tree(table, keys=None, array=None, start=0, label=None):
    if array is None:
        tsize = 1
        while tsize < len(table):
            tsize = tsize << 1
        array = [(None, None)] * tsize
    if keys is None:
        keys = list(table.keys())
        keys.sort()
    #print("start", start, len(keys), label, len(array))
    pivot = len(keys) // 2
    array[start] = (keys[pivot], table[keys[pivot]])
    if pivot > 0:
        binary_tree(table, keys[:pivot], array, 2 * start + 1, "left")
    if pivot < len(keys) - 1:
        binary_tree(table, keys[pivot + 1 :], array, 2 * start + 2, "right")
    return array

def c_escape(s):
    out = []
    for b in s:
        if chr(b) in string.printable:
            out.append(chr(b).replace('\\', '\\\\').replace('"', '\\"'))
        else:
            out.append('\\%o' % b)
    return ''.join(out)

def update_ctable(long, short, single, path="ctable.c"):
    strings = {}
    intern = []
    i = 0
    for table in long, short, single:
        for k, v in table.items():
            assert k > 0
            assert k < 65535
            v = v.encode('utf-8')
            if v in strings:
                pass
            else:
                strings[v] = i
                intern.append(v)
                i += 1
    assert i < 65535

    src = open(path, "w")
    print("static const char *ctlc_strings[] = {", file=src)
    for s in intern:
        
        print('  "' + c_escape(s) + '",',
              file=src)
    print("  NULL\n};", file=src)

    for name, table in (("long", long), ("short", short), ("single", single)):
        tree = binary_tree(table)
        while tree[-1] == (None, None):
            tree.pop()
        print("static const int", "ctlc_" + name + "_tlen = %d;" % len(tree),
              file=src)
        print("static const node", "ctlc_" + name + "_table[] = {", file=src)
        for val, s in tree:
            if val is not None:
                s = s.encode('utf-8')
                print("  {%d, %d, %d}," % (val, strings[s], len(s)), file=src)
            else:
                print("  {0, -1, -1},", file=src)
        print("  {0, -1, -1}\n};", file=src)

    src.close()


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        print("This script requires to be run under Python 3")
        sys.exit(-1)

    if not os.path.exists("transtab"):
        print("Can not find transtab/ directory.")
        sys.exit(-1)
    tables = read_tables()
    update_ctable(*tables)
    all = ''.join(chr(cp) for cp in tables[0].keys())
    f = open('long.txt', 'w', encoding='utf-8')
    f.write(all)
    f.close()
