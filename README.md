# LSF: Lightweight Study Format

A self-contained, offline-first file format for storing and sharing marked coursework with grading rubrics.

Status: BETA, specification complete, tests and examples in progress.

## Design Goals

- Self contained. All metadata, media, and course data live inside a single `.lsf` file.
- Offline. No external server communication needed for file authenticity.
- Human readable. The backbone is JSON, inspectable in any text editor.
- Content agnostic. Works for any subject with a marking rubric.
- Merge friendly. Multiple people can work independently on the same course and merge their files.
- Backward compatible. Stable `format_version` with clear SemVer rules; implementations MUST preserve unknown fields.
- Portable. A standard ZIP archive with the `.lsf` extension, zero OS-specific paths.
- No proprietary lock-in. An open standard any tool can implement.

## Quick Links

- [SPEC.md](SPEC.md): Full specification (v1.0.0)
- [examples/](examples/): Complete example `.lsf` file
- [tests/](tests/): Conformance test vectors
- [schemas/](schemas/): JSON Schema for `course.json`

## Repository

- Pre-release: https://git.dyno.cx/Sardiniangale/Lightweight_Study_Format
- Full release (GitHub): https://github.com/Sardiniangale/lsf-spec

## License

MIT License, see [LICENSE](LICENSE).
