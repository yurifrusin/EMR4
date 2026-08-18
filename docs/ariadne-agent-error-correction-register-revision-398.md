# Ariadne agent error and correction register — revision 398

Date: 2026-08-18

Timestamp: 2026-08-18T17:29:56.0631711+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 398 carries forward AER-0454 through AER-0458 and adds AER-0459.

AER-0459 records that the pre-dispatch pinned-package mapping claimed the
enclosed worker would declare only `read`, `glob` and `edit`, while the exact
occupied request header declared seven model-facing tools: `edit`, `glob`,
`grep`, `read`, `read_image`, `str_replace_editor` and `write`. The isolated
broker correctly rejected the surplus tool declaration with
`tool-not-allowlisted` before provider I/O. The worker exited 1 in 761 ms with
`INVALID_REQUEST` / HTTP 400, zero provider calls, zero successful model steps,
zero tool calls and no candidate change.

The single occupied attempt is consumed and receives no retry. The negative
result is attributable and fail-closed: the raw four-frame session remained in
its disposable volume, while sanitized reduction established 17 logical rows,
one request header and the exact tool inventory without retaining prompt,
reasoning, response or tool-payload content. A future separately frozen
recovery must first prove a package-native scoped model tool view against a
provider-free composed request header. The broker allowlist is not broadened
to absorb unreviewed write, image, grep or editor aliases.

## Population

- incidents: 459;
- corrected or explicitly contained: 459;
- open: 0;
- latest id: `AER-0459`.
