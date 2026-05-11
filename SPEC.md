# LSF: Lightweight Study File Specification
## Version 0.1.0

License: MIT License

Repository pre-release: (https://git.dyno.cx/Sardiniangale/Lightweight_Study_Format)

Repository full-release: (https://github.com/Sardiniangale/lsf-spec)

---

## Table of Contents

1. [Terminology](#1-terminology)
2. [Philosophy & Goals](#2-philosophy--goals)
3. [Physical Container](#3-physical-container)
4. [Deterministic Course Identity](#4-deterministic-course-identity)

---

## 1. Terminology

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted exactly as described as in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

Terms & Definitions

LSF file: A ZIP archive with the `.lsf` extension conforming to this specification
course.json: The single required JSON file inside an LSF file containing all structured data
merge: The act of combining two LSF files with the same `course.id` into one.
author: Any person who creates or modifies content within an LSF file.
compliant writer: A tool that produces LSF files conforming to §12.1.
compliant reader: A tool that consumes LSF files conforming to §12.2.
UUID4: A randomly generated UUID per [RFC 4122 §4.4](https://www.rfc-editor.org/rfc/rfc4122#section-4.4), which is a lowercase hyphenated string for example something like: 550e8400-e29b-41d4-a716-446655440000

---

## 2. Philosophy & Goals

LSF is built on the following principles, listed in priority order. When principles conflict, earlier ones take precedence.

1. Self-contained: One file holds everything from metadata, questions, answers, self-assessments, and media.
2. Offline: No server required, no account, no API key. All data stays local. The format does not and will not require network access for any core function.
3. As human readable as possible: Any text editor can open `course.json` after unzipping. Field names need to be english words.
4. Content agnostic: Works for any subject with a rubric.
5. Merge friendly: Multiple people can independently work on the same course and combine their files later. Merging is user controlled
6. Backward compatible: A stable `format_version` with clear SemVer rules. Parsers MUST preserve unknown fields. See §11.
7. Portable: A standard ZIP archive with no OS-specific paths, no symlinks, no extended attributes.
8. No proprietary lock in: An open standard under the MIT licence. Anyone can implement it in whatever way they wish without permission or fees.

---

## 3. Physical Container

An LSF file is just a ZIP archive with the file extension `.lsf`. No other container format is permitted.

### Internal Structure

```
<filename>.lsf
├── course.json
└── media/
    ├── example.jpg
    ├── solution.pdf
    └── ...
```

### Rules

- `course.json` MUST be present at the root of the archive.
- `course.json` MUST be encoded as UTF-8 without a BOM.
- All paths inside the archive MUST use forward slashes as separators. Backslashes are not permitted.
- The `media/` directory is OPTIONAL. It MUST be named exactly `media` (lowercase).
- Files inside `media/` MUST be referenced by their relative path from the archive root for example `media/scan.jpg`.
- As already mentioned above but there MUST NOT be any symlinks, hard links and executable bits inside the archive
- Additional files or directories outside `media/` for example `.git` MUST be ignored by compliant readers and MUST NOT be written by compliant writers.
- The archive MUST NOT contain encrypted ZIP entries.

### File Naming

The RECOMMENDED default filename is `{Institution}_{CourseCode}.lsf` for example `MIT_18.100B.lsf`. The extension MUST be `.lsf`. Tools MAY allow users to choose any filename.

---

## 4. Deterministic Course Identity

Every LSF file carries a `course.id` that uniquely identifies the course without any central registry. Two people who independently enter the same institution and course code will produce the same ID, enabling automatic merge detection.

### Algorithm

Apply each step in order:

1. Take the `institution` string and the `course_code` string as entered by the user.
2. Normalize each string independently:
   a. Trim all leading and trailing whitespace (Unicode whitespace, including U+0020, U+0009, U+000A, U+000D, U+00A0).
   b. Convert to lowercase using Unicode case folding (not locale-specific lowercasing).
   c. Collapse all runs of internal whitespace (any sequence of one or more whitespace characters) to a single ASCII space (U+0020).
   d. Remove all characters that are not ASCII alphanumeric (`a–z`, `0–9`), ASCII hyphen (`-`), or ASCII space (U+0020). This step strips periods, punctuation, and non-ASCII letters.
3. Concatenate: `normalized_institution + "|" + normalized_course_code`
4. Encode the concatenated string as UTF-8 bytes.
5. Compute the SHA-256 hash of those bytes.
6. Take the first 32 hexadecimal characters (128 bits) of the hash, in lowercase.
7. Store this string as `course.id`.

### Basic Worked Example

```
institution  = "Massachusetts Institute of Technology"
course_code  = "18.100B"

Step 2 (institution):
  Trim      → "Massachusetts Institute of Technology"
  Lowercase → "massachusetts institute of technology"
  Collapse  → "massachusetts institute of technology"
  Strip     → "massachusetts institute of technology"

Step 2 (course_code):
  Trim      → "18.100B"
  Lowercase → "18.100b"
  Collapse  → "18.100b"
  Strip     → "18100b"

Step 3: "massachusetts institute of technology|18100b"
Step 5: SHA-256("massachusetts institute of technology|18100b")
Step 6: first 32 hex chars → (see §14 for verified value)
```

### Important Notes

- Year and semester are NOT part of the course ID. All past papers from any year belong to the same LSF file.
- Two inputs that normalize identically produce the same ID. This is intentional.
- The ID algorithm is fixed for all 1.x versions. Changes to the algorithm require a major version bump.

(unsure on how to handle if the same course has a diffrent course id, tbd)

---

## 5. The course.json Schema (still working on this)

### 5.1 Top Level

```json
{
  "format_version": "1.0.0", (assuming this is for the full release)
  "course": { },
  "papers": [ ],
  "practice_items": [ ],
  "metadata": { }
}
```

Field, Type, Required, Description 

`format_version`, string (SemVer), REQUIRED, Version of the LSF spec this file conforms to. MUST be a valid SemVer string. 
`course`, object, REQUIRED, Course identity and rubric. See §5.2. 
`papers`, array, REQUIRED, List of past paper objects. MAY be empty (`[]`). (refrences future) 
`practice_items`, array, REQUIRED, List of standalone practice items. MAY be empty (`[]`). (refrences future) 
`metadata`, object, REQUIRED, File-level metadata. 

No other top-level fields are defined by this specification. Unknown top-level fields MUST be preserved per ---

---

### 5.2 course Object

```json
{
  "id": "1a79a4d60de6718e8e5b326e338ae533",
  "institution": "Massachusetts Institute of Technology",
  "course_code": "18.100B",
  "course_name": "Real Analysis",
  "curriculum_version": "2024-2025",
  "criteria": [ ],
  "exam_type": "proof_based",
  "extensions": { }
}
```

Field, Type, Required, Description

`id`, string, REQUIRED, Deterministic course identifier (§4). MUST be exactly 32 lowercase hex characters.
`institution`, string, REQUIRED, Full institution name as entered by the user. MUST NOT be empty.
`course_code`, string, REQUIRED, Official course code for example `"18.100B"`. MUST NOT be empty.
`course_name`, string, REQUIRED, Readable course name. MUST NOT be empty.
`curriculum_version`, string, OPTIONAL, Free-form syllabus or curriculum identifier. Used for merge warnings.
`criteria`, array, REQUIRED, Grading rubric (§5.3). MUST contain at least one criterion.
`exam_type`, string, OPTIONAL, Hint for tools. For example some suggested values: `"proof_based"`, `"written"`, `"mixed"`, `"lab"`, `"multiple_choice"`. Tools MUST accept unknown values.
`extensions`, object, OPTIONAL, ---.

---

### 5.3 Grading Criterion

Each element in `course.criteria`:

```json
{
  "id": "rigor",
  "name": "Logical Rigor",
  "max_score": 5,
  "description": "Correctness and completeness of proofs"
}
```

Field, Type, Required, Description

`id`, string, REQUIRED, Unique key within `course.criteria`. MUST match the regex `^[a-z0-9_-]+$`.
`name`, string, REQUIRED, Name.
`max_score`, number, REQUIRED, Maximum achievable score. MUST be a positive number.
`description`, string, OPTIONAL, Gives description of what the criteria is describing.

Uniqueness: All `id` values across `course.criteria` MUST be unique. Duplicate IDs for criteria will result in a validation error.

---

### 5.4 Self-Assessment Object

```json
{
  "obtained_marks": {
    "rigor": 4,
    "clarity": 3
  },
  "notes": "Made a typo in line 3."
}
```

Field, Type, Required, Description

`obtained_marks`, object, REQUIRED, Map of criterion `id` -> score (number).
`notes`, string, OPTIONAL, Free-form reflection on this attempt. |

Constraint: Every key in `obtained_marks` MUST correspond to an `id` in `course.criteria`. Scores MUST be non-negative numbers and SHOULD NOT exceed the criterion's `max_score`, tools MAY warn but MUST NOT reject. Unknown criterion keys are a validation error.

---

### 5.5 Answer Object

