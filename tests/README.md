# LSF Conformance Tests

## Test Vectors

`test-vectors.md` — Normative course ID generation test vectors. Implementors
MUST validate their implementations against these vectors.

## Runnable Test Suite

`run_tests.py` — Reference implementation of the course ID algorithm with all
test vectors from test-vectors.md embedded as assertions. Requires Python 3.7+
(standard library only, no dependencies).

```
python3 run_tests.py
```

Output: 16 passed, 0 failed out of 16

Implementors in other languages can use this as a reference to port the
algorithm and verify their output against the expected values.

## Coming Soon

- JSON Schema validation test suite
- Round-trip conformance tests
- Merge conflict resolution tests
- Edge case ZIP archives
