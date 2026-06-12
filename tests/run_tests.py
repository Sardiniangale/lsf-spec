#!/usr/bin/env python3
# lsf test suite — validate course ID algorithm against normative test vectors
# usage: python3 run_tests.py
# requires: python 3.7+ (standard library only)

import hashlib
import re
import sys
import unicodedata

UNICODE_WS = ' \t\n\r\xa0'

def normalize(s):
    # step 2a: trim unicode whitespace
    s = s.strip(UNICODE_WS)
    # step 2b: NFC normalize
    s = unicodedata.normalize('NFC', s)
    # step 2c: unicode case folding
    s = s.casefold()
    # step 2d: collapse internal whitespace runs to single ascii space
    s = re.sub(r'[\s]+', ' ', s)
    # step 2e: strip non-unicode-alphanumeric non-hyphen non-space
    result = []
    for c in s:
        if c.isalpha() or c.isdigit() or c == '-' or c == ' ':
            result.append(c)
    s = ''.join(result)
    return s

def course_id(institution, course_code):
    ni = normalize(institution)
    nc = normalize(course_code)
    concat = ni + "|" + nc
    h = hashlib.sha256(concat.encode('utf-8')).hexdigest()
    return h[:32], ni, nc, concat


# -- test cases ----------------------------------------------------------
# each: (label, institution, course_code, expected_normalized_inst,
#         expected_normalized_code, expected_concatenated, expected_course_id)

TESTS = [
    ("TV1: worked example (MIT)",
     "Massachusetts Institute of Technology", "18.100B",
     "massachusetts institute of technology", "18100b",
     "massachusetts institute of technology|18100b",
     "40f559945e0fe13c82a1339e7a12c7fd"),

    ("TV2: leading/trailing whitespace + mixed case",
     "  University   of   Cambridge  ", "  MATHS   Tripos  ",
     "university of cambridge", "maths tripos",
     "university of cambridge|maths tripos",
     "a61e2d59497746ca1f19727ddb613cea"),

    ("TV3: unicode non-breaking space (U+00A0)",
     "University\xa0of Cambridge", "Maths Tripos",
     "university of cambridge", "maths tripos",
     "university of cambridge|maths tripos",
     "a61e2d59497746ca1f19727ddb613cea"),

    ("TV4: special characters stripped (comma)",
     "University of California, Berkeley", "CS 61A",
     "university of california berkeley", "cs 61a",
     "university of california berkeley|cs 61a",
     "a100f7030df49bf99c15bb9473bc4a27"),

    ("TV5: accented latin letters preserved",
     "Université de Paris", "MATH101",
     "université de paris", "math101",
     "université de paris|math101",
     "ef62cf87cf1e1159c0adfd5b8cf803aa"),

    ("TV6: periods stripped",
     "St. Andrews University", "MT1001",
     "st andrews university", "mt1001",
     "st andrews university|mt1001",
     "14688e80c82c1f843b502a13ab09c6ab"),

    ("TV7: hyphens preserved",
     "University of Wisconsin-Madison", "MATH 521",
     "university of wisconsin-madison", "math 521",
     "university of wisconsin-madison|math 521",
     "c0978c0ac198884286e8861182f572f0"),

    ("TV8: umlaut preserved",
     "ETH Zürich", "401-0231-00L",
     "eth zürich", "401-0231-00l",
     "eth zürich|401-0231-00l",
     "2ab1b32d34b147c9df3b21697db26081"),

    ("TV9: tab and newline as whitespace",
     "University\tof\nQueensland", "MATH2400",
     "university of queensland", "math2400",
     "university of queensland|math2400",
     "8159ce26eec9963451e79e1c5e2597be"),

    ("TV10: cyrillic preserved",
     "Московский университет", "MATH101",
     "московский университет", "math101",
     "московский университет|math101",
     "e37de5ce18fb56c366afd320945a21a3"),

    ("TV11: japanese preserved",
     "東京大学", "MATH101",
     "東京大学", "math101",
     "東京大学|math101",
     "4f626a48dc43fb4cc5bd072b12d1a88a"),

    ("TV12: chinese preserved",
     "北京大学", "MATH101",
     "北京大学", "math101",
     "北京大学|math101",
     "a6425b183a61b62722ac76fe98e198db"),

    ("TV13: precomposed accent (U+00E9)",
     "Université de Paris", "MATH101",
     "université de paris", "math101",
     "université de paris|math101",
     "ef62cf87cf1e1159c0adfd5b8cf803aa"),

    ("TV14: decomposed accent (U+0065 U+0301)",
     "Université de Paris", "MATH101",
     "université de paris", "math101",
     "université de paris|math101",
     "ef62cf87cf1e1159c0adfd5b8cf803aa"),

    ("TV15: only special characters — empty",
     "!!!", "###",
     "", "",
     "|",
     "cbe5cfdf7c2118a9c3d78ef1d684f3af"),

    ("TV16: empty inputs",
     "", "",
     "", "",
     "|",
     "cbe5cfdf7c2118a9c3d78ef1d684f3af"),
]

if __name__ == '__main__':
    passed = 0
    failed = 0

    for label, inst, code, exp_ni, exp_nc, exp_concat, exp_id in TESTS:
        cid, ni, nc, concat = course_id(inst, code)
        ok = (ni == exp_ni and nc == exp_nc and concat == exp_concat and cid == exp_id)

        if ok:
            print(f"  PASS  {label}")
            passed += 1
        else:
            print(f"  FAIL  {label}")
            if ni != exp_ni:
                print(f"        normalized_inst:  got {repr(ni)}")
                print(f"                          exp {repr(exp_ni)}")
            if nc != exp_nc:
                print(f"        normalized_code:  got {repr(nc)}")
                print(f"                          exp {repr(exp_nc)}")
            if concat != exp_concat:
                print(f"        concatenated:     got {repr(concat)}")
                print(f"                          exp {repr(exp_concat)}")
            if cid != exp_id:
                print(f"        course.id:        got {cid}")
                print(f"                          exp {exp_id}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed out of {len(TESTS)}")

    if failed > 0:
        sys.exit(1)
