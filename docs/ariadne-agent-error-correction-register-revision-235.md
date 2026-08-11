# Ariadne agent error and correction register — revision 235

Date: 2026-08-11

Revision 235 adds AER-0270. The register now contains 270 bounded known
incidents.

## AER-0270 — first CF-D1 implementation veto missed the entrypoint defect

The first fresh Gemini 3.6 Flash/high implementation review returned `pass` and
reported no schema/runtime mismatch. The reviewed harness nevertheless imported
the repository package before installing its root path, and attempt 001 failed
at that exact line before any runtime effect.

That decision is rejected for runtime admission. The corrected candidate must
receive a genuinely fresh exact-HEAD review whose allowlisted checks include the
new direct child-process entrypoint test before attempt 002 can open.
