# The .lsf standard

It is currently in the very early testing phase. I want to hit these design standards

- Self contained. All metadata pdf's ect ect must be all contained within a single .lsf
- Offline. There is zero need for communication to any external server for file authenticity 
- Human readable. The entire backbone is written in JSON, it must be easily inspectable in any text editor
- Content agnostic. It needs to be able to work for any subject with a marking rubric
- Merge friendly. It needs to be able to work with multiple people such that they can all independently work on the same course at the same/similar time. User controlled merging at its core
- Backward compatible. A stable format_version with clear SemVer rules; implementations must preserve unknown fields.
- Portable. Its a standard ZIP archive renameable to .lsf, with zero OS specific paths.
- No proprietary lock in. The format is an open standard any tool can implement it.

---

Im primarily designing this so I can implement it into another oss study app later on. But I figured I might as well make the standard open and public while I am at it. I will write a base design doc very soon (within week) and it will also be availible on github as well, however this is just where I can mess around before making public.

---

This repo is specifically for the official standardized version. Testing and design is done here: https://git.dyno.cx/Sardiniangale/Lightweight_Study_Format

---

If you have any questions or issues feel free to write a mail at asm@cadaxity.it
