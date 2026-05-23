# LSF: Lightweight Study Format Specification
## Version 1.0.0 (pre-release NOT YET FULLY RELEASED)

Status: Release Candidate
License: MIT
Repository pre-release: https://git.dyno.cx/Sardiniangale/Lightweight_Study_Format
Repository full-release: https://github.com/Sardiniangale/lsf-spec

---

## Table of Contents

1. [Terminology](#1-terminology)
2. [Philosophy & Goals](#2-philosophy--goals)
3. [Physical Container](#3-physical-container)
4. [Deterministic Course Identity](#4-deterministic-course-identity)
5. [The course.json Schema](#5-the-coursejson-schema)
   - 5.1 [Top Level](#51-top-level)
   - 5.2 [course Object](#52-course-object)
   - 5.3 [Grading Criterion](#53-grading-criterion)
   - 5.4 [Self-Assessment Object](#54-self-assessment-object)
   - 5.5 [Answer Object](#55-answer-object)
   - 5.6 [Quality Flag Object](#56-quality-flag-object)
   - 5.7 [Past Paper Object](#57-past-paper-object)
   - 5.8 [Question Object](#58-question-object)
   - 5.9 [Practice Item Object](#59-practice-item-object)
   - 5.10 [Metadata Object](#510-metadata-object)
   - 5.11 [Lineage Event Object](#511-lineage-event-object)
6. [Extensions](#6-extensions)
7. [Media Handling](#7-media-handling)
8. [Authorship & Identity](#8-authorship--identity)
9. [Merging](#9-merging)
   - 9.1 [Merge Trigger](#91-merge-trigger)
   - 9.2 [Merge Unit & Conflict Detection](#92-merge-unit--conflict-detection)
   - 9.3 [Field-Level Merge Rules](#93-field-level-merge-rules)
   - 9.4 [Lineage After Merge](#94-lineage-after-merge)
   - 9.5 [Curriculum Mismatch Warning](#95-curriculum-mismatch-warning)
   - 9.6 [Merge Safety & Backups](#96-merge-safety--backups)
10. [Quality Flagging](#10-quality-flagging)
11. [Format Versioning & Governance](#11-format-versioning--governance)
12. [Conformance](#12-conformance)
    - 12.1 [Writer Conformance](#121-writer-conformance)
    - 12.2 [Reader Conformance](#122-reader-conformance)
13. [Validation Rules](#13-validation-rules)
14. [Test Vectors](#14-test-vectors)
15. [Complete Example](#15-complete-example)
16. [Changelog](#16-changelog)

---

## 1. Terminology

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in RFC 2119.

Term: LSF file
Definition: A ZIP archive with the .lsf extension conforming to this specification.

Term: course.json
Definition: The single required JSON file inside an LSF file containing all structured data.

Term: merge
Definition: The act of combining two LSF files with the same course.id into one.

Term: author
Definition: Any person who creates or modifies content within an LSF file.

Term: compliant writer
Definition: A tool that produces LSF files conforming to section 12.1.

Term: compliant reader
Definition: A tool that consumes LSF files conforming to section 12.2.

Term: UUID4
Definition: A randomly generated UUID per RFC 4122 section 4.4, represented as a lowercase hyphenated string (e.g., 550e8400-e29b-41d4-a716-446655440000).

---

## 2. Philosophy & Goals

LSF is built on the following principles, listed in priority order. When principles conflict, earlier ones take precedence.

1. Self-contained — One file holds everything: metadata, questions, answers, self-assessments, and media. No external references are required to read or use the file.
2. Offline & private — No server, no account, no API key. All data stays local. The format does not and will not require network access for any core function.
3. Human-readable at its core — JSON backbone. Any text editor can open course.json after unzipping. Field names are English words, not codes.
4. Content-agnostic — Works for any subject with a rubric: mathematics, history, chemistry, programming, languages, law, and beyond.
5. Merge-friendly — Multiple people can independently work on the same course and combine their files later. Merging is user-controlled; nothing is silently overwritten.
6. Backward-compatible — A stable format_version with clear SemVer rules. Parsers MUST preserve unknown fields. See section 11.
7. Portable — A standard ZIP archive with no OS-specific paths, no symlinks, no extended attributes. Runs on any platform that can open a ZIP file.
8. No proprietary lock-in — An open standard under MIT. Any tool can implement it without permission or fees.

---

## 3. Physical Container

An LSF file is a ZIP archive (using Deflate or Store compression) with the file extension .lsf. No other container format is permitted.

Internal Structure:

<filename>.lsf        ZIP archive
├── course.json       REQUIRED
└── media/            OPTIONAL directory
    ├── example.jpg
    ├── solution.pdf
    └── ...

Rules:

- course.json MUST be present at the root of the archive (not inside a subdirectory).
- course.json MUST be encoded as UTF-8 without a BOM.
- All paths inside the archive MUST use forward slashes (/) as separators. Backslashes are not permitted.
- The media/ directory is OPTIONAL. It MUST be named exactly media (lowercase).
- Files inside media/ MUST be referenced by their relative path from the archive root (e.g., media/scan.jpg).
- No symlinks, hard links, or executable bits are permitted inside the archive.
- Additional files or directories outside media/ (e.g .git) MUST be ignored by compliant readers and MUST NOT be written by compliant writers.
- The archive MUST NOT contain encrypted ZIP entries.

File Naming:

The RECOMMENDED default filename is {Institution}_{CourseCode}.lsf (e.g., MIT_18.100B.lsf). The extension MUST be .lsf. Tools MAY allow users to choose any filename.

---

## 4. Deterministic Course Identity

Every LSF file carries a course.id that uniquely identifies the course without any central registry. Two people who independently enter the same institution and course code will produce the same ID, enabling automatic merge detection.

Algorithm:

Apply each step in order:

1. Take the institution string and the course_code string as entered by the user.
2. Normalize each string independently:
   a. Trim all leading and trailing whitespace (Unicode whitespace, including U+0020, U+0009, U+000A, U+000D, U+00A0).
   b. Convert to lowercase using Unicode case folding (not locale-specific lowercasing).
   c. Collapse all runs of internal whitespace (any sequence of one or more whitespace characters) to a single ASCII space (U+0020).
   d. Remove all characters that are not ASCII alphanumeric (a–z, 0–9), ASCII hyphen (-), or ASCII space (U+0020). This step strips periods, punctuation, and non-ASCII letters.
3. Concatenate: normalized_institution + "|" + normalized_course_code
4. Encode the concatenated string as UTF-8 bytes.
5. Compute the SHA-256 hash of those bytes.
6. Take the first 32 hexadecimal characters (128 bits) of the hash, in lowercase.
7. Store this string as course.id.

Worked Example:

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
Step 6: first 32 hex chars → (see section 14 for verified value)

Important Notes:

- Year and semester are NOT part of the course ID. All past papers from any year belong to the same LSF file.
- Two inputs that normalize identically produce the same ID. This is intentional.
- The ID algorithm is fixed for all 1.x versions. Changes to the algorithm require a major version bump.

---

## 5. The course.json Schema

### 5.1 Top Level

{
  "format_version": "1.0.0",
  "course": { },
  "papers": [ ],
  "practice_items": [ ],
  "metadata": { }
}

Field: format_version
Type: string (SemVer)
Required: REQUIRED
Description: Version of the LSF spec this file conforms to. MUST be a valid SemVer string.

Field: course
Type: object
Required: REQUIRED
Description: Course identity and rubric. See section 5.2.

Field: papers
Type: array
Required: REQUIRED
Description: List of past paper objects. MAY be empty ([]). See section 5.7.

Field: practice_items
Type: array
Required: REQUIRED
Description: List of standalone practice items. MAY be empty ([]). See section 5.9.

Field: metadata
Type: object
Required: REQUIRED
Description: File-level metadata. See section 5.10.

No other top-level fields are defined by this specification. Unknown top-level fields MUST be preserved per section 6.

---

### 5.2 course Object

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

Field: id
Type: string
Required: REQUIRED
Description: Deterministic course identifier (section 4). MUST be exactly 32 lowercase hex characters.

Field: institution
Type: string
Required: REQUIRED
Description: Full institution name as entered by the user. MUST NOT be empty.

Field: course_code
Type: string
Required: REQUIRED
Description: Official course code (e.g., "18.100B"). MUST NOT be empty.

Field: course_name
Type: string
Required: REQUIRED
Description: Human-readable course name. MUST NOT be empty.

Field: curriculum_version
Type: string
Required: OPTIONAL
Description: Free-form syllabus or curriculum identifier. Used for merge warnings (section 9.5).

Field: criteria
Type: array
Required: REQUIRED
Description: Grading rubric (section 5.3). MUST contain at least one criterion.

Field: exam_type
Type: string
Required: OPTIONAL
Description: Hint for tools. Suggested values: "proof_based", "written", "mixed", "lab", "multiple_choice". Tools MUST accept unknown values.

Field: extensions
Type: object
Required: OPTIONAL
Description: See section 6.

---

### 5.3 Grading Criterion

Each element in course.criteria:

{
  "id": "rigor",
  "name": "Logical Rigor",
  "max_score": 5,
  "description": "Correctness and completeness of proofs"
}

Field: id
Type: string
Required: REQUIRED
Description: Unique key within course.criteria. MUST match the regex ^[a-z0-9_-]+$.

Field: name
Type: string
Required: REQUIRED
Description: Human-readable name.

Field: max_score
Type: number
Required: REQUIRED
Description: Maximum achievable score. MUST be a positive number.

Field: description
Type: string
Required: OPTIONAL
Description: Explanation of what this criterion measures.

Uniqueness: All id values across course.criteria MUST be unique. Duplicate criterion IDs are a validation error.

---

### 5.4 Self-Assessment Object

{
  "obtained_marks": {
    "rigor": 4,
    "clarity": 3
  },
  "notes": "Forgot to justify the base case."
}

Field: obtained_marks
Type: object
Required: REQUIRED
Description: Map of criterion id → score (number).

Field: notes
Type: string
Required: OPTIONAL
Description: Free-form reflection on this attempt.

Constraint: Every key in obtained_marks MUST correspond to an id in course.criteria. Scores MUST be non-negative numbers and SHOULD NOT exceed the criterion's max_score (tools MAY warn but MUST NOT reject). Unknown criterion keys are a validation error.

---

### 5.5 Answer Object

{
  "text": "Let $\\epsilon > 0$. Choose $\\delta = \\epsilon / 2$...",
  "media": [
    {
      "path": "media/midterm1_q1.jpg",
      "mime_type": "image/jpeg",
      "description": "Scanned handwritten proof",
      "available": true
    }
  ]
}

Field: text
Type: string
Required: OPTIONAL
Description: Typed answer. Markdown and LaTeX ($...$, $$...$$) are permitted.

Field: media
Type: array
Required: OPTIONAL
Description: List of attached files. MAY be empty or absent.

Each entry in media:

Field: path
Type: string
Required: REQUIRED
Description: Relative path from archive root. MUST start with media/.

Field: mime_type
Type: string
Required: REQUIRED
Description: IANA media type (e.g., "image/jpeg", "application/pdf").

Field: description
Type: string
Required: OPTIONAL
Description: Human-readable description of the attached file.

Field: available
Type: boolean
Required: OPTIONAL
Description: If false, the file was intentionally stripped (e.g., for privacy or size). Readers MUST NOT treat a missing file as a parse error when available is false. Defaults to true when absent.

Constraint: Referenced media/ paths MUST point to a file that exists inside the ZIP, unless available is explicitly false.

Both absent: If both text and media are absent or empty, the answer object represents an unattempted item. This is valid; tools SHOULD indicate the item has no answer.

---

### 5.6 Quality Flag Object

Used to mark an item as disputed or verified. Appears as an OPTIONAL field quality_flag on any question, paper, or practice item.

{
  "status": "disputed",
  "reason": "The formula in Q3 is incorrect. See Spivak p.142.",
  "flagged_by": "550e8400-e29b-41d4-a716-446655440000",
  "flagged_at": "2026-05-10T14:00:00Z"
}

Field: status
Type: string
Required: REQUIRED
Description: One of: "unreviewed", "disputed", "verified".

Field: reason
Type: string
Required: OPTIONAL
Description: Human-readable explanation. SHOULD be present when status is "disputed".

Field: flagged_by
Type: string (UUID4)
Required: REQUIRED
Description: The author_id of the person setting this flag.

Field: flagged_at
Type: string (datetime)
Required: REQUIRED
Description: UTC datetime in YYYY-MM-DDTHH:MM:SSZ format.

Status semantics:

- "unreviewed" — Default. No flag has been deliberately set. Absence of quality_flag is equivalent to "unreviewed".
- "disputed" — The flagger believes this content contains an error. Tools MUST display a visible warning to the user when rendering disputed items.
- "verified" — The flagger has checked this content and believes it is correct.

Merge rule: When two files contain different quality_flag values on the same item, the user MUST be shown both and asked to choose. A tool MUST NOT silently resolve a flag conflict.

---

### 5.7 Past Paper Object

Each element in the top-level papers array:

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "label": "Midterm 1",
  "title": "Midterm 1",
  "date": "2025-03-15",
  "academic_year": "2024-2025",
  "term": "Spring",
  "total_time_minutes": 90,
  "questions": [ ],
  "reflection": "Need more practice with uniform convergence.",
  "source": "official_exam",
  "author_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "imported_from": null,
  "quality_flag": null,
  "extensions": { }
}

Field: id
Type: string (UUID4)
Required: REQUIRED
Description: Globally unique identifier for this paper. MUST be a UUID4. Generated once at creation and never changed.

Field: label
Type: string
Required: OPTIONAL
Description: Short display label (e.g., "Midterm 1"). Used by tools as the primary display name.

Field: title
Type: string
Required: REQUIRED
Description: Full title of the exam or paper.

Field: date
Type: string
Required: REQUIRED
Description: Date the exam was taken. MUST be in YYYY-MM-DD format.

Field: academic_year
Type: string
Required: OPTIONAL
Description: e.g., "2024-2025".

Field: term
Type: string
Required: OPTIONAL
Description: e.g., "Spring", "Fall", "Semester 1".

Field: total_time_minutes
Type: number
Required: OPTIONAL
Description: Duration of the exam in minutes. MUST be a positive integer if present.

Field: questions
Type: array
Required: REQUIRED
Description: List of question objects (section 5.8). MAY be empty.

Field: reflection
Type: string
Required: OPTIONAL
Description: Free-form post-exam notes.

Field: source
Type: string
Required: OPTIONAL
Description: Origin. Suggested values: "official_exam", "mock_exam", "peer_shared". Tools MUST accept unknown values.

Field: author_id
Type: string (UUID4)
Required: REQUIRED
Description: UUID4 of the person who created this entry (section 8).

Field: imported_from
Type: string (UUID4) or null
Required: OPTIONAL
Description: If this paper was imported from another person's file, their author_id. null if created by the author directly.

Field: quality_flag
Type: object or null
Required: OPTIONAL
Description: See section 5.6. null or absent means "unreviewed".

Field: extensions
Type: object
Required: OPTIONAL
Description: See section 6.

Uniqueness: All id values across the papers array MUST be unique. Duplicate paper IDs are a validation error.

---

### 5.8 Question Object

Each element in a paper.questions array:

{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "label": "Q1",
  "topic_tags": ["limits", "epsilon-delta"],
  "difficulty": 3,
  "question_text": "Prove that $f(x) = x^2$ is continuous at $x = 2$.",
  "hints": [
    "Start by writing the definition of continuity.",
    "Consider the triangle inequality."
  ],
  "student_answer": { },
  "self_assessment": { },
  "quality_flag": null,
  "extensions": { }
}

Field: id
Type: string (UUID4)
Required: REQUIRED
Description: Globally unique identifier for this question. MUST be a UUID4. Generated once at creation and never changed.

Field: label
Type: string
Required: OPTIONAL
Description: Display label (e.g., "Q1", "Question 3b"). If absent, tools MAY display a truncated id.

Field: topic_tags
Type: array of strings
Required: OPTIONAL
Description: Labels for filtering and organisation. Each tag MUST be a non-empty string.

Field: difficulty
Type: number
Required: OPTIONAL
Description: Difficulty rating. RECOMMENDED range is 1–5. Tools MUST accept values outside this range.

Field: question_text
Type: string
Required: REQUIRED
Description: The question itself. Markdown and LaTeX are permitted. MUST NOT be empty.

Field: hints
Type: array of strings
Required: OPTIONAL
Description: Ordered list of progressive hints. Each hint MUST be a non-empty string.

Field: student_answer
Type: object
Required: OPTIONAL
Description: The student's answer. See section 5.5.

Field: self_assessment
Type: object
Required: OPTIONAL
Description: Self-scoring against rubric. See section 5.4.

Field: quality_flag
Type: object or null
Required: OPTIONAL
Description: See section 5.6.

Field: extensions
Type: object
Required: OPTIONAL
Description: See section 6.

Uniqueness: All id values across questions within a single paper MUST be unique. IDs SHOULD be globally unique across all questions in all papers, since UUID4 collision is astronomically unlikely.

---

### 5.9 Practice Item Object

Practice items share all fields with a question object (section 5.8), plus:

{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "label": "Spivak 5.12",
  "source": "textbook",
  "source_detail": "Spivak, Calculus, Chapter 5, Problem 12",
  "date_added": "2025-04-01",
  "author_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "topic_tags": ["integration"],
  "difficulty": 4,
  "question_text": "...",
  "student_answer": { },
  "hints": [ ],
  "self_assessment": { },
  "quality_flag": null,
  "extensions": { }
}

Additional fields beyond section 5.8:

Field: source
Type: string
Required: OPTIONAL
Description: Origin. Suggested: "textbook", "weekly_quiz", "online", "lecture_problem_set".

Field: source_detail
Type: string
Required: OPTIONAL
Description: Full bibliographic reference.

Field: date_added
Type: string
Required: OPTIONAL
Description: Date added by the student. MUST be in YYYY-MM-DD format if present.

Field: author_id
Type: string (UUID4)
Required: REQUIRED
Description: UUID4 of the person who added this item (section 8).

Uniqueness: All id values across the practice_items array MUST be unique.

---

### 5.10 Metadata Object

{
  "last_modified": "2026-05-10T14:00:00Z",
  "created_at": "2025-09-01T09:00:00Z",
  "software": "lsf-tool v0.1.0",
  "created_by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "signature": null,
  "lineage": [ ],
  "extensions": { }
}

Field: last_modified
Type: string (datetime)
Required: REQUIRED
Description: UTC datetime of last save. MUST be in YYYY-MM-DDTHH:MM:SSZ format.

Field: created_at
Type: string (datetime)
Required: OPTIONAL
Description: UTC datetime the file was first created. MUST be in YYYY-MM-DDTHH:MM:SSZ format if present.

Field: software
Type: string
Required: OPTIONAL
Description: Name and version of the tool that last saved the file.

Field: created_by
Type: string (UUID4)
Required: OPTIONAL
Description: author_id of the original creator of this file.

Field: signature
Type: string or null
Required: OPTIONAL
Description: Reserved for digital signatures (e.g., base64-encoded PGP detached signature). null if unused.

Field: lineage
Type: array
Required: REQUIRED
Description: Ordered list of provenance events (section 5.11). MAY be empty. MUST NOT be absent.

Field: extensions
Type: object
Required: OPTIONAL
Description: See section 6.

---

### 5.11 Lineage Event Object

Each element in metadata.lineage:

{
  "event_id": "b6d5f8a2-1c3e-4f7a-9d0b-2e4c6a8b0d1f",
  "type": "create",
  "by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "at": "2025-09-01T09:00:00Z",
  "software": "lsf-tool v0.1.0",
  "merged_sources": null
}

Field: event_id
Type: string (UUID4)
Required: REQUIRED
Description: Globally unique identifier for this event. Used for deduplication during merge.

Field: type
Type: string
Required: REQUIRED
Description: One of: "create", "merge", "edit". Tools MUST accept unknown types.

Field: by
Type: string (UUID4)
Required: REQUIRED
Description: author_id of the person who performed this action.

Field: at
Type: string (datetime)
Required: REQUIRED
Description: UTC datetime of the event. MUST be in YYYY-MM-DDTHH:MM:SSZ format.

Field: software
Type: string
Required: OPTIONAL
Description: Tool name and version that generated this event.

Field: merged_sources
Type: array of UUID4 or null
Required: OPTIONAL
Description: For "merge" events: list of author_id values from the files that were merged into this one. null or absent for non-merge events.

Append-only rule: Tools MUST NOT delete or modify existing lineage events. When saving after any edit, tools MUST append a new "edit" event. When saving after a merge, tools MUST append a new "merge" event.

Merge deduplication: When two files are merged, the resulting lineage array is the union of both input arrays, deduplicated by event_id, then sorted ascending by at. If two events share an event_id but differ in other fields, the event from the file with the later last_modified wins.

---

## 6. Extensions

Every major object in this spec (course, paper, question, practice_item, self_assessment, metadata, and any answer) MAY contain an extensions field. The extensions field, if present, MUST be a JSON object.

Rules for All Implementations

- Implementations MUST preserve all extensions keys when reading and re-saving a file, even if the keys are not understood.
- Implementations MUST NOT reject a file solely because it contains unknown extensions keys.
- Implementations MUST NOT reject a file solely because it contains unknown top-level or nested fields (forward compatibility).
- Interpretation of extension data is the sole responsibility of the tool that wrote it.

Namespacing Convention

Extension keys SHOULD be namespaced to avoid collisions:

"extensions": {
  "com.example.mytool": {
    "spaced_repetition_due": "2026-06-01",
    "ease_factor": 2.5
  }
}

The RECOMMENDED format for namespace keys is reverse-domain notation. Tools MAY use any string key, but SHOULD namespace to prevent collisions with future spec fields.

Extension Profiles

Community-defined extension profiles (documents describing agreed-upon extension keys for a specific use case) MAY be published separately. The core spec does not enumerate or mandate any extension profile.

---

## 7. Media Handling

- All binary or large files MUST be stored in the media/ directory inside the ZIP archive.
- References to media in course.json use forward-slash relative paths starting with media/ (e.g., media/scan.jpg).
- Media filenames MUST NOT contain path separators (i.e., no / or \ within the filename itself).
- Filenames SHOULD be lowercase ASCII with hyphens or underscores, to maximise cross-platform compatibility. Unicode filenames are permitted but SHOULD be avoided.

Content-Addressed Deduplication (RECOMMENDED)

To avoid storing the same file multiple times across merged versions, compliant writers SHOULD use the following naming convention:

media/<sha256-prefix>-<original-name>

Where <sha256-prefix> is the first 16 hex characters of the SHA-256 hash of the file's byte content. This ensures that identical files receive identical paths, and a merge that encounters duplicate paths with identical content can safely keep one copy.

Implementations that do not use content-addressed names MUST NOT rename existing media/ files during a merge without updating all references in course.json.

Stripped Media

When a user intentionally removes media files before sharing (e.g., for privacy or to reduce file size), all references in course.json MUST be updated to set "available": false on the affected media entries. Tools MUST NOT treat a missing file as a parse error when available is false. Tools SHOULD display a clear indicator that media is unavailable.

---

## 8. Authorship & Identity

Author ID

Each user has an author_id, which is a UUID4 generated locally by the tool. It is used to attribute papers, practice items, quality flags, and lineage events.

Generation rules:

- A compliant writer MUST generate an author_id UUID4 on first run if none exists.
- The author_id MUST be persisted in a local configuration file (location is tool-defined) and reused for all subsequent operations.
- If a user works across multiple tools, the author_id SHOULD be exportable and importable so the same identity is used everywhere.
- The author_id is not a security credential. It is a stable identifier for attribution, not authentication. Two users who accidentally share an author_id will produce a naming collision, not a security breach. The probability of UUID4 collision is negligible.

Display Name

Tools SHOULD allow users to set a display_name alongside their author_id. This name is purely for human display and has no normative function.

Tools SHOULD maintain a map of author_id → display_name within the extensions object or in local configuration. This spec does not mandate a storage location for the display name.

---

## 9. Merging

### 9.1 Merge Trigger

A merge is triggered when a user presents two or more LSF files to a compliant tool and requests they be combined. Tools MAY also offer to merge automatically when two LSF files in the same workspace share the same course.id. Any automatic merge detection MUST still require explicit user confirmation before writing any output.

Two LSF files are candidates for merging if and only if their course.id values are identical (section 4). Files with different course.id values MUST NOT be merged and MUST NOT be offered to the user as merge candidates.

### 9.2 Merge Unit & Conflict Detection

The merge unit is the individual object identified by its id field. Specifically:

- Papers are identified by paper.id (UUID4).
- Questions are identified by question.id (UUID4).
- Practice items are identified by practice_item.id (UUID4).
- Lineage events are identified by lineage_event.event_id (UUID4).
- Criteria are identified by criterion.id (short string).

Conflict definition: A conflict exists when two files contain an object with the same id but with at least one differing field value (excluding extensions, which is merged field-by-field per section 9.3).

No conflict: If two files contain an object with the same id and identical field values, it is the same object and MUST be deduplicated to a single copy with no user intervention required.

New object: If an id appears in only one of the two input files, it is a new object and MUST be added to the merged output without conflict.

### 9.3 Field-Level Merge Rules

When a conflict is detected on an object, the following rules apply:

Scenario: Same id, different content, different author_id
Required behaviour: MUST show side-by-side preview. User MUST choose one version or manually edit. Tool MUST NOT auto-resolve.

Scenario: Same id, different content, same author_id
Required behaviour: SHOULD show a diff. Tool MAY offer "keep newer" based on last_modified. User MUST confirm.

Scenario: Same id, only extensions differ
Required behaviour: Merge extensions objects by key union. If a key exists in both with differing values, treat as a conflict on that key alone and surface to user.

Scenario: quality_flag differs
Required behaviour: MUST show both flags to user. User MUST choose. See section 5.6.

Scenario: New field added by one file (forward compat)
Required behaviour: The field is preserved in the merge output regardless of which file contributed it.

Author protection: An author's own entries (where author_id matches the current user's author_id) MUST NOT be silently overwritten by content from another file. The user MUST be informed if an incoming file would modify their own content.

### 9.4 Lineage After Merge

After a merge is completed and the user has resolved all conflicts, the tool MUST:

1. Compute the union of both files' lineage arrays, deduplicated by event_id, sorted ascending by at.
2. Append a new "merge" event with:
   - A freshly generated event_id (UUID4).
   - type: "merge".
   - by: the current user's author_id.
   - at: the current UTC time.
   - merged_sources: list of created_by values from all input files (or author_id of the dominant contributor if created_by is absent).
3. Update metadata.last_modified to the current UTC time.

### 9.5 Curriculum Mismatch Warning

If two files being merged have different course.curriculum_version values, or if one file has the field and the other does not, the tool MUST display a warning before proceeding:

"These files were created under different curriculum versions (X vs Y). Content may not align with your current syllabus. Review carefully before merging."

The user MAY proceed. The merged file MUST retain both version strings in an extensions field (or as a list if the spec is extended in a minor version). Papers and practice items from each source remain attributable by author_id.

### 9.6 Merge Safety & Backups

All merges MUST be non-destructive:

1. Before any merge, the tool MUST create a timestamped backup of each input file. The backup location is tool-defined but SHOULD be discoverable by the user.
2. The merge result MUST be written as a new file or confirmed overwrite, never a silent in-place replace.
3. The tool SHOULD provide an "Undo Merge" function that restores the pre-merge backups.
4. Backup files MUST remain even after further edits to the merged file.

---

## 10. Quality Flagging

Quality flagging is a lightweight peer-review signal. It is intentionally simple: one status, one reason, one author.

How It Works

Any user who receives an LSF file MAY set a quality_flag (section 5.6) on any question, paper, or practice item. The flag travels with the file when it is shared onward.

Abuse Resistance

The format provides natural resistance to flagging abuse through its social structure:

- There is no central authority and no upvote/downvote counter. A malicious flagger cannot influence files they have not personally received.
- A user who flags everything maliciously produces a file full of warnings. Recipients will observe this and stop propagating that user's version.
- Flags carry flagged_by (the flagger's author_id), making the source transparent.
- Each user's copy is their own. A bad-faith file does not affect other branches of the file's propagation.

Tools MUST

- Display a clear, visible warning when rendering any item with status: "disputed".
- Display a clear, positive indicator when rendering any item with status: "verified".
- Show the reason field when displaying the flag.
- Allow users to override any incoming flag on their own copy.
- During a merge, surface conflicting flags to the user (section 9.3).

Tools MUST NOT

- Prevent a user from accessing or reading disputed content. The flag is a warning, not a lock.
- Silently remove flags from incoming files.
- Apply a flag to multiple items in a single action without explicit per-item user confirmation.

---

## 11. Format Versioning & Governance

LSF uses Semantic Versioning 2.0.0 on the format_version field.

Change types and their meanings:

- Patch (1.0.x): Clarifications, typo fixes, non-semantic editorial changes to the spec text. No change to valid or invalid file content. Example: 1.0.1
- Minor (1.x.0): New OPTIONAL fields or objects. New RECOMMENDED values for existing enum fields. All 1.x parsers remain forward-compatible. Example: 1.1.0
- Major (x.0.0): Any breaking change: field removals, renames, changes to the course ID algorithm, changes to required fields, container restructuring. Example: 2.0.0

Compatibility Guarantee

Any LSF file with format_version 1.x.y MUST be readable by any compliant 1.a.b reader where a >= x. Unknown fields encountered due to a newer minor version MUST be preserved on round-trip.

Version Checking by Readers

- If the major version of format_version equals the reader's supported major version: proceed normally.
- If the major version of format_version is greater than the reader's supported major version: the reader MUST warn the user that the file may use unsupported features, and MUST NOT silently corrupt or discard data.
- If the major version of format_version is less than the reader's supported major version: the reader SHOULD offer to migrate the file to the current major version, and MUST NOT do so without explicit user confirmation.

Governance

- v1.x: The original author holds final decision authority.
- v2.0+: An RFC process is used. Proposals are submitted as GitHub discussion, undergo a public comment period of no less than 30 days, and are decided by the core team.
- The file SCOPE.md in the repository defines what belongs in the core spec. Everything else lives in extensions or separate community profiles.
- Minor releases: no more than 2 per calendar year. Patches: as needed, batched quarterly.

---

## 12. Conformance

### 12.1 Writer Conformance

A compliant writer MUST:

1. Produce a valid ZIP archive with the .lsf extension.
2. Include course.json at the archive root, encoded as UTF-8 without BOM.
3. Use only forward slashes in all internal paths.
4. Set format_version to a valid SemVer string matching the spec version implemented.
5. Generate course.id using the exact algorithm in section 4 and store 32 lowercase hex characters.
6. Generate UUID4 values for all id fields on papers, questions, and practice items.
7. Generate a UUID4 author_id on first run and persist it for reuse.
8. Set metadata.lineage to a valid array (MAY be empty for new files).
9. Append a lineage event on every save operation.
10. Set metadata.last_modified to the current UTC time on every save.
11. Use YYYY-MM-DD for date-only fields and YYYY-MM-DDTHH:MM:SSZ for datetime fields.
12. Place all binary files inside the media/ directory.
13. Not include symlinks, executable bits, or encrypted entries in the ZIP.

A compliant writer SHOULD:

- Use content-addressed filenames for media (section 7).
- Set metadata.software to a tool name and version string.
- Set metadata.created_by on newly created files.

### 12.2 Reader Conformance

A compliant reader MUST:

1. Accept any valid ZIP file with the .lsf extension.
2. Parse course.json as UTF-8 JSON.
3. Preserve all unknown fields (fields not defined in this spec) when re-saving.
4. Preserve all extensions keys when re-saving.
5. Not reject a file solely due to unknown fields or unknown extension keys.
6. Warn the user if format_version has a major version greater than the reader's supported major version, and not corrupt the file.
7. Not treat a missing media file as a parse error when available is false.
8. Display a warning when rendering items with quality_flag.status === "disputed".
9. Not silently overwrite an author's own content during a merge.
10. Require explicit user confirmation before performing any merge.
11. Create backups before merging (section 9.6).

A compliant reader SHOULD:

- Validate course.id against the algorithm in section 4 and warn if there is a mismatch (without rejecting the file).
- Validate obtained_marks keys against course.criteria and warn on unknown keys.

---

## 13. Validation Rules

The following are hard validation errors. A compliant reader MUST surface these to the user, and a compliant writer MUST NOT produce files that violate them.

1. format_version is absent or not parseable as SemVer.
2. course.id is not exactly 32 lowercase hexadecimal characters.
3. course.criteria is absent or empty.
4. Any criterion.id is not unique within course.criteria.
5. Any self_assessment.obtained_marks key does not correspond to a criterion.id in course.criteria.
6. Any paper.id, question.id, or practice_item.id is not a valid UUID4 string.
7. Duplicate id values within the papers array.
8. Duplicate id values within the practice_items array.
9. Any date-only field not matching YYYY-MM-DD.
10. Any datetime field not matching YYYY-MM-DDTHH:MM:SSZ.
11. Any paper.author_id or practice_item.author_id is absent.
12. Any referenced media/ path does not start with media/.
13. Any referenced media/ path points to a file not present in the ZIP, and available is not false.
14. metadata.lineage is absent (it MAY be an empty array, but MUST be present).
15. Any lineage.event_id is not a valid UUID4 string.

The following are warnings. A compliant reader SHOULD surface these to the user but MUST NOT reject the file.

1. course.id does not match the result of running the section 4 algorithm on the stored institution and course_code.
2. A self_assessment.obtained_marks score exceeds the criterion's max_score.
3. format_version major version exceeds the reader's supported major version.
4. paper.author_id or practice_item.author_id is present but does not appear to be a UUID4.

---

## 14. Test Vectors

Implementors MUST verify their course ID algorithm against these vectors. All produce a deterministic SHA-256; the first 32 hex characters are the expected course.id.

Vector 1

Input:
  institution = "Massachusetts Institute of Technology"
  course_code  = "18.100B"

Normalization:
  institution → "massachusetts institute of technology"
  course_code → "18100b"

Concatenated: "massachusetts institute of technology|18100b"

SHA-256: 8b9a1f2e4c6d0b3a7e5c9d1f3b5a7e2c4d6f8a0b2e4c6d8f0a2b4c6d8e0f2a4b
course.id: "8b9a1f2e4c6d0b3a7e5c9d1f3b5a7e2c"

Note: The SHA-256 value above is illustrative. The authoritative test vectors, with computed-and-verified SHA-256 values, are published in the repository as test-vectors.json. Implementors MUST use the repository values, not the values in this document, as the normative reference. This document will be updated when the repository vectors are finalised.

Vector 2 — Whitespace and case normalisation

Input:
  institution = "  MIT  "
  course_code  = "  18.100b  "

Normalization:
  institution → "mit"
  course_code → "18100b"

Concatenated: "mit|18100b"

Note: this produces a DIFFERENT course.id from Vector 1, because "MIT" and "Massachusetts Institute of Technology" normalize differently. Users entering different institution strings for the same school will get different IDs. Tools SHOULD prompt users to use their institution's full official name.

Vector 3 — Unicode institution name

Input:
  institution = "Université de Paris"
  course_code  = "MATH-201"

Normalization:
  institution → "universit de paris"   (é removed, non-ASCII)
  course_code → "math-201"             (hyphen preserved)

Concatenated: "universit de paris|math-201"

---

## 15. Complete Example

Archive Layout

RealAnalysis.lsf
├── course.json
└── media/
    ├── proof1.jpg
    └── midterm_solutions.pdf

course.json

{
  "format_version": "1.0.0",
  "course": {
    "id": "8b9a1f2e4c6d0b3a7e5c9d1f3b5a7e2c",
    "institution": "Massachusetts Institute of Technology",
    "course_code": "18.100B",
    "course_name": "Real Analysis",
    "curriculum_version": "2024-2025",
    "criteria": [
      {
        "id": "rigor",
        "name": "Logical Rigor",
        "max_score": 5,
        "description": "Correctness and completeness of proofs"
      },
      {
        "id": "clarity",
        "name": "Clarity",
        "max_score": 5,
        "description": "Clear and well-structured mathematical writing"
      }
    ],
    "exam_type": "proof_based",
    "extensions": {}
  },
  "papers": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "label": "Midterm 1",
      "title": "Midterm Examination 1",
      "date": "2025-03-15",
      "academic_year": "2024-2025",
      "term": "Spring",
      "total_time_minutes": 90,
      "source": "official_exam",
      "author_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "imported_from": null,
      "reflection": "Struggled with uniform convergence in Q3. Revisit.",
      "quality_flag": null,
      "questions": [
        {
          "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
          "label": "Q1",
          "topic_tags": ["continuity", "epsilon-delta"],
          "difficulty": 2,
          "question_text": "Prove that $f(x) = x^2$ is continuous at $x = 2$.",
          "hints": [
            "Write out the $\\epsilon$-$\\delta$ definition of continuity.",
            "Factor $|x^2 - 4| = |x-2||x+2|$ and bound $|x+2|$."
          ],
          "student_answer": {
            "text": "Let $\\epsilon > 0$. We need $\\delta > 0$ such that...",
            "media": [
              {
                "path": "media/proof1.jpg",
                "mime_type": "image/jpeg",
                "description": "Scanned handwritten proof",
                "available": true
              }
            ]
          },
          "self_assessment": {
            "obtained_marks": {
              "rigor": 4,
              "clarity": 5
            },
            "notes": "Clean proof but I should have bounded |x+2| more carefully."
          },
          "quality_flag": null,
          "extensions": {}
        },
        {
          "id": "3f4a5b6c-7d8e-9f0a-1b2c-3d4e5f6a7b8c",
          "label": "Q2",
          "topic_tags": ["uniform-convergence"],
          "difficulty": 4,
          "question_text": "Prove or disprove: $f_n(x) = x^n$ converges uniformly on $[0,1]$.",
          "hints": [],
          "student_answer": {
            "text": "The sequence does not converge uniformly...",
            "media": []
          },
          "self_assessment": {
            "obtained_marks": {
              "rigor": 2,
              "clarity": 3
            },
            "notes": "Got the conclusion right but the proof was incomplete."
          },
          "quality_flag": {
            "status": "disputed",
            "reason": "My proof of the pointwise limit is wrong at x=1. The limit is 1, not 0.",
            "flagged_by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "flagged_at": "2026-05-10T14:00:00Z"
          },
          "extensions": {}
        }
      ],
      "extensions": {}
    }
  ],
  "practice_items": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "label": "Spivak 5.12",
      "source": "textbook",
      "source_detail": "Spivak, Calculus, 4th ed., Chapter 5, Problem 12",
      "date_added": "2025-04-01",
      "author_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "topic_tags": ["integration", "riemann-sums"],
      "difficulty": 3,
      "question_text": "Prove that every bounded monotone function on $[a,b]$ is Riemann integrable.",
      "hints": [
        "Partition $[a,b]$ into $n$ equal subintervals.",
        "Bound the difference of upper and lower Riemann sums."
      ],
      "student_answer": {
        "text": "Let $f$ be bounded and increasing on $[a,b]$...",
        "media": []
      },
      "self_assessment": {
        "obtained_marks": {
          "rigor": 5,
          "clarity": 4
        },
        "notes": "Happy with this one."
      },
      "quality_flag": null,
      "extensions": {}
    }
  ],
  "metadata": {
    "last_modified": "2026-05-10T14:00:00Z",
    "created_at": "2025-09-01T09:00:00Z",
    "software": "lsf-tool v0.1.0",
    "created_by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "signature": null,
    "lineage": [
      {
        "event_id": "b6d5f8a2-1c3e-4f7a-9d0b-2e4c6a8b0d1f",
        "type": "create",
        "by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "at": "2025-09-01T09:00:00Z",
        "software": "lsf-tool v0.1.0",
        "merged_sources": null
      },
      {
        "event_id": "c7e6f9b3-2d4f-5a8b-0e1c-3f5a7b9c1e2d",
        "type": "edit",
        "by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "at": "2026-05-10T14:00:00Z",
        "software": "lsf-tool v0.1.0",
        "merged_sources": null
      }
    ],
    "extensions": {}
  }
}

---

## 16. Changelog

1.0.0 — Initial Release

- First public release of the LSF specification.
- Defines ZIP+JSON container format.
- Defines deterministic course ID algorithm (SHA-256).
- Defines UUID4-based object identity for papers, questions, and practice items.
- Defines quality flagging system with three statuses.
- Defines append-only lineage array for generational provenance.
- Defines RFC 2119 conformance language.
- Defines writer and reader conformance requirements separately.
- Defines merge semantics at the data level.
- Defines missing media handling via available field.

---

LSF Specification v1.0.0
Licensed under MIT
Contributions welcome on Github
