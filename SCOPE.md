# LSF Scope & Boundaries
## Version 1.0.0

This document defines what belongs in the core LSF specification and what
should live elsewhere. It is referenced by SPEC §11 (Governance).

---

## What LSF Is

LSF is a file format for storing and sharing marked coursework. It defines:

- A physical container (ZIP archive with .lsf extension).
- A JSON schema for structured course data (course.json).
- A deterministic course identity algorithm for merge detection.
- Object identity and merge semantics for collaborative workflows.
- A lightweight quality flagging system for peer review.
- A lineage mechanism for provenance tracking.

LSF is NOT a study application, a sync protocol, a spaced-repetition system,
or a grading tool. It is the file format those tools read and write on.

---

## In Scope for the Core Spec

The core specification (SPEC.md) covers everything that MUST be standardised
for two independent implementations to produce interoperable files.

In scope:

- Physical container format and internal path rules.
- course.json schema: all required fields, their types, and validation rules.
- The deterministic course.id algorithm (section 4 of the spec).
- UUID4-based object identity for papers, questions, and practice items.
- Merge semantics at the data level (conflict detection, field-level rules).
- Quality flag statuses and their display requirements.
- Lineage event types and the append-only rule.
- Format versioning (SemVer) and forward-compatibility rules.
- Writer and reader conformance requirements.
- Extension mechanism (the extensions field and its preservation rules).
- Media handling conventions (content-addressed naming, stripped media).
- Test vectors for normative algorithms.

A change to any of the above requires a spec revision.

---

## Out of Scope for the Core Spec

The following are intentionally out of scope. They MAY be built on top of LSF
but SHOULD NOT be added to the core specification.

Out of scope:

- Spaced-repetition algorithms, ease factors, or scheduling data.
- Colour themes, UI layout preferences, or display hints beyond exam_type.
- Font choices, rendering engines, or user-defined LaTeX macro definitions (\newcommand, \renewcommand). The core spec defines a minimum math subset (SPEC §5.12) that readers MUST render; arbitrary custom macros remain tool territory.
- Grade calculation, GPA integration, or transcript generation.
- Network protocols for sync, sharing, or discovery.
- Authentication, digital signatures (the signature field is reserved but
  the spec does not define a signing scheme), or DRM.
- Encryption at rest (the ZIP MUST NOT contain encrypted entries per §3).
- Server-side storage formats or database schemas.
- Import/export from other formats (CSV, Anki, Moodle XML, etc.).
- Analytics, progress tracking, or study-time logging.
- Accessibility metadata beyond what is already expressible in the schema.

---

## Extensions vs Community Profiles

Extension (noun):
  A key-value pair inside an extensions object on any major schema object.
  Extensions are tool-specific or user-specific data that travels with the
  file. Examples: "com.example.mytool": { "spaced_repetition_due": "..." }.

Community profile (noun):
  A separately published document that defines an agreed-upon set of extension
  keys for a specific use case. Multiple tools can implement the same profile
  and interoperate on that extension data.

Guidelines:

- If only one tool needs the data: use an extension key namespaced to that
  tool (reverse-domain notation RECOMMENDED).
- If multiple tools would benefit from interoperating on the data: propose a
  community profile that standardises the extension keys and their semantics.
- Community profiles MUST NOT contradict the core spec. They MAY add
  constraints (e.g. "max_score MUST be an integer") but MUST NOT relax them.
- Community profiles are published separately from the core spec repository.
  The core spec does not endorse or mandate any specific profile.

---

## Proposing Changes to Scope

For v1.x:
  The original author holds final decision authority on scope questions.
  Proposals are discussed in the repository issue tracker.

For v2.0+:
  An RFC process is used (see SPEC §11). Scope changes follow the same
  process as spec changes.

When evaluating whether something belongs in the core spec, ask:

  1. Would two independent implementations produce incompatible files if
     this were not standardised?
  2. Is this a property of the file format itself, or of the tool that
     reads it?
  3. Can this be expressed as an extension without breaking interoperability?

If the answer to (1) is "no" and the answer to (2) is "the tool", it does
not belong in the core spec.

---

## Version History

1.0.0 Initial scope document. Defines boundaries for the v1.x spec series.
