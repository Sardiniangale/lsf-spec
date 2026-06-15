# LSF Examples

This directory contains complete example LSF files for implementors.

---

## course.json

A full standalone example for a Real Analysis course (MIT 18.100B). It exercises:

- Three grading criteria (rigor, clarity, notation)
- One past paper (Midterm 1) with two questions
  - Q1: epsilon-delta proof: student answer with media, self-assessment
  - Q2: sequence convergence: verified by peer, full LaTeX solution
- Two practice items
  - Spivak 5.12: textbook problem with PDF media
  - Uniform convergence drill: disputed quality flag
- Full lineage with create, edit, and merge events
- Quality flags showing both "verified" and "disputed" statuses

---

## Merge Example

Four files demonstrating the merge workflow defined in SPEC §9:

### Input Files

- `merge-alice.json`: Alice's LSF file (author_id: aaaaaaaa-...)
- `merge-bob.json`: Bob's LSF file (author_id: bbbbbbbb-...)

Both files share the same course.id (MIT 18.100B), making them merge candidates.

### Merge Scenarios Exercised

Same id, identical content, same author (dedup):
  The practice item "Spivak 5.12" (d1d1d1d1-...) appears in both files with identical
  fields and the same author_id (Alice). It is deduplicated to a single copy with no
  user intervention required. See SPEC §9.2.

New object from one side only (no conflict):
  Bob's Final Exam paper (d99243aa-...) and its questions, plus Bob's Rudin 2.4
  practice item (6395b02d-...): these appear only in Bob's file and are added to
  the merged output without conflict. See SPEC §9.2.

Same id, different content, different author (conflict):
  Q1 of Midterm 1 (b1b1b1b1-...) has Alice's answer in one file and Bob's answer in
  the other, with different author_ids. The user must choose one version: a tool
  MUST NOT auto-resolve this. The output shows the resolved state (user chose
  Alice's version). See SPEC §9.3.

Quality flag conflict:
  Q2 of Midterm 1 (c1c1c1c1-...) is flagged "verified" by Alice and "disputed" by
  Bob. The user must choose which flag to keep. The output shows Alice's "verified"
  flag retained. See SPEC §9.3 and §10.

Curriculum mismatch warning:
  Alice's file has curriculum_version "2024-2025", Bob's has "2023-2024". The tool
  MUST warn the user before merging (SPEC §9.5). The output records this in
  course.extensions for audit purposes.

### Output File

- `merge-output.json`: the merged result after user conflict resolution

Key changes from the inputs:
  - Lineage: union of both input lineage arrays, deduplicated by event_id, sorted
    ascending by at, with a new "merge" event appended at the end.
  - metadata.last_modified: updated to the merge time.
  - metadata.created_by: set to the user who performed the merge (cccccccc-...).
  - Individual objects marked with non-normative `_merge_note` fields for clarity.
    These fields are tools for reading this example: they are preserved per the
    forward-compatibility rules in SPEC §6 but have no normative meaning.

### Usage

Each file can be zipped into an .lsf archive for testing:

```
zip course.lsf course.json
```

Or, if media files were present:

```
zip -r course.lsf course.json media/
```

### Media Files

The examples reference these media paths (not included: set `available` to
false or provide your own):

- `media/midterm1_q1_scan.jpg`
- `media/spivak_5_12_solution.pdf`
