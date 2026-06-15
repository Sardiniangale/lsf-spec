# LSF Conformance Test Vectors
## Version 1.0.0

Implementors MUST validate their course ID generation against these vectors.
Each test provides the raw inputs and the expected output at each step of the algorithm defined in SPEC §4.

The algorithm, in order: trim → NFC normalize → casefold → collapse whitespace → strip non-alphanumeric (Unicode L + Nd categories, hyphen, space).

---

## Normalisation Tests

### TV1: Worked Example (from SPEC §4)

```
institution     = "Massachusetts Institute of Technology"
course_code     = "18.100B"

step 2a (trim)        → "Massachusetts Institute of Technology"
step 2b (nfc)         → "Massachusetts Institute of Technology"
step 2c (casefold)    → "massachusetts institute of technology"
step 2d (collapse)    → "massachusetts institute of technology"
step 2e (strip)       → "massachusetts institute of technology"

step 2a (trim)        → "18.100B"
step 2b (nfc)         → "18.100B"
step 2c (casefold)    → "18.100b"
step 2d (collapse)    → "18.100b"
step 2e (strip)       → "18100b"

step 3 (concat)       → "massachusetts institute of technology|18100b"
step 6 (sha256[:32])  → 40f559945e0fe13c82a1339e7a12c7fd
```

### TV2: Whitespace Normalisation

```
institution     = "  University   of   Cambridge  "
course_code     = "  MATHS   Tripos  "

normalised_inst    → "university of cambridge"
normalised_code    → "maths tripos"
concatenated       → "university of cambridge|maths tripos"
course.id          → a61e2d59497746ca1f19727ddb613cea
```

### TV3: Unicode Non-Breaking Space (U+00A0)

```
institution     = "University of Cambridge"
course_code     = "Maths Tripos"

normalised_inst    → "university of cambridge"
normalised_code    → "maths tripos"
concatenated       → "university of cambridge|maths tripos"
course.id          → a61e2d59497746ca1f19727ddb613cea
```

Note: TV2 and TV3 produce the same course.id. U+00A0 is whitespace per the spec and collapses to ASCII space.

### TV4: Special Characters Stripped (Comma)

```
institution     = "University of California, Berkeley"
course_code     = "CS 61A"

normalised_inst    → "university of california berkeley"
normalised_code    → "cs 61a"
concatenated       → "university of california berkeley|cs 61a"
course.id          → a100f7030df49bf99c15bb9473bc4a27
```

### TV5: Accented Latin Letters Preserved

```
institution     = "Université de Paris"
course_code     = "MATH101"

normalised_inst    → "université de paris"
normalised_code    → "math101"
concatenated       → "université de paris|math101"
course.id          → ef62cf87cf1e1159c0adfd5b8cf803aa
```

Note: The accented 'é' is preserved, not stripped. "Université" and "Universite" now produce different course IDs: this is intentional.

### TV6: Periods Stripped

```
institution     = "St. Andrews University"
course_code     = "MT1001"

normalised_inst    → "st andrews university"
normalised_code    → "mt1001"
concatenated       → "st andrews university|mt1001"
course.id          → 14688e80c82c1f843b502a13ab09c6ab
```

Note: "St. Andrews" and "St Andrews" produce the same ID (period stripped). This is a known collision class.

### TV7: Hyphens Preserved

```
institution     = "University of Wisconsin-Madison"
course_code     = "MATH 521"

normalised_inst    → "university of wisconsin-madison"
normalised_code    → "math 521"
concatenated       → "university of wisconsin-madison|math 521"
course.id          → c0978c0ac198884286e8861182f572f0
```

### TV8: Non-ASCII + Numbers + Hyphens (Umlaut Preserved)

```
institution     = "ETH Zürich"
course_code     = "401-0231-00L"

normalised_inst    → "eth zürich"
normalised_code    → "401-0231-00l"
concatenated       → "eth zürich|401-0231-00l"
course.id          → 2ab1b32d34b147c9df3b21697db26081
```

### TV9: Tab and Newline as Whitespace

```
institution     = "University\tof\nQueensland"
course_code     = "MATH2400"

normalised_inst    → "university of queensland"
normalised_code    → "math2400"
concatenated       → "university of queensland|math2400"
course.id          → 8159ce26eec9963451e79e1c5e2597be
```

---

## Non-Latin Script Tests

### TV10: Cyrillic Preserved

```
institution     = "Московский университет"
course_code     = "MATH101"

normalised_inst    → "московский университет"
normalised_code    → "math101"
concatenated       → "московский университет|math101"
course.id          → e37de5ce18fb56c366afd320945a21a3
```

### TV11: Japanese Preserved

```
institution     = "東京大学"
course_code     = "MATH101"

normalised_inst    → "東京大学"
normalised_code    → "math101"
concatenated       → "東京大学|math101"
course.id          → 4f626a48dc43fb4cc5bd072b12d1a88a
```

### TV12: Chinese Preserved

```
institution     = "北京大学"
course_code     = "MATH101"

normalised_inst    → "北京大学"
normalised_code    → "math101"
concatenated       → "北京大学|math101"
course.id          → a6425b183a61b62722ac76fe98e198db
```

Note: TV10, TV11, and TV12 all use the same course_code but produce different course IDs. Non-Latin scripts no longer collapse to the same degenerate value.

---

## NFC Normalisation Tests

### TV13: Precomposed Accent (U+00E9)

```
institution     = "Université de Paris"          (é as single code point U+00E9)
course_code     = "MATH101"

normalised_inst    → "université de paris"
concatenated       → "université de paris|math101"
course.id          → ef62cf87cf1e1159c0adfd5b8cf803aa
```

### TV14: Decomposed Accent (U+0065 U+0301)

```
institution     = "Université de Paris"          (é as e + combining acute accent U+0301)
course_code     = "MATH101"

normalised_inst    → "université de paris"       (NFC collapses to single code point)
concatenated       → "université de paris|math101"
course.id          → ef62cf87cf1e1159c0adfd5b8cf803aa
```

Note: TV13 and TV14 produce the same course.id. This is the purpose of NFC normalization: two byte-level representations of the same visual text must not produce different IDs.

---

## Edge Case Tests

### TV15: Both Inputs Only Special Characters

```
institution     = "!!!"
course_code     = "###"

normalised_inst    → ""        (empty string)
normalised_code    → ""        (empty string)
concatenated       → "|"
course.id          → cbe5cfdf7c2118a9c3d78ef1d684f3af
```

### TV16: Empty Inputs

```
institution     = ""
course_code     = ""

normalised_inst    → ""
normalised_code    → ""
concatenated       → "|"
course.id          → cbe5cfdf7c2118a9c3d78ef1d684f3af
```

Warning: TV15 and TV16 produce the same course.id. Implementations SHOULD reject files where either institution or course_code normalises to an empty string.

---

## Collision Awareness

These are the known collision classes under the current algorithm. All are
deliberate trade-offs for simplicity.

Period vs space:
  "St. Andrews" → normalises to "st andrews university"
  "St Andrews" → normalises to "st andrews university"
  Collide? Yes. The period is stripped; the space remains.

Precomposed vs decomposed (NFC makes these collide by design):
  "Université" (U+00E9) and "Université" (U+0065 U+0301)
  Collide? Yes. This is the intended behaviour of step 2b: they are the same text.

Both inputs normalise to empty:
  "!!!" and "###" with any course code that also normalises to empty
  Collide? Yes. Tools SHOULD reject empty normalised strings.

These collisions are acceptable because the course.id is an identity hint for
merge detection, not a security mechanism. Users who encounter an unexpected
merge prompt due to a collision can decline the merge.
