# Ariadne agent error and correction register — revision 259

Date: 2026-08-12

Revision 259 records and corrects AER-0292. The register now contains 292
bounded known incidents with none open.

During status-confirm physical-representability discovery, Sol queried Git
filename metadata under the broad `app` path. Although no file content was
opened, the output enumerated prohibited protected authoring path names among
otherwise non-protected candidates. The output is discarded and prohibited
from planning, implementation, tests and acceptance. No repository file,
runtime, database, provider, credential, product data, command or ref was
mutated by the query.

This recurs the protected-scope family recorded by AER-0041, AER-0054,
AER-0092 and AER-0291, while preserving its distinct metadata-enumeration
signature. The strengthened control is narrower than AER-0291: near protected
evidence, neither content search nor filename-metadata discovery may name a
directory root. Candidate discovery must begin from exact already-known
non-protected paths and expand only through exact imports or exact migration
links found after a frozen plan authorizes reading those files.

The incident and control are registered before any physical-representability
plan or corrected source inspection. No protected path name from the failed
output is reproduced in durable evidence.
