# Ariadne agent error and correction register — revision 236

Date: 2026-08-11

Revision 236 closes AER-0269 and AER-0270 after a genuinely fresh exact-HEAD
Gemini 3.6 Flash/high recovery review passed source
`d007188c574d5c61a270a5911b4d16d3fc019d98`.

The corrected harness now installs the repository root before importing its
parent package and carries a child-process file-path entrypoint test. The fresh
review independently reran all 251 AER and CF-D1 checks, verified that the only
harness changes were the import bootstrap and attempt-002 evidence name, and
performed zero Docker, database, provider, product or external-network
operations.

Attempt 001 remains rejected and supplies no concurrency evidence. Attempt 002
is the next eligible bounded runtime attempt.
