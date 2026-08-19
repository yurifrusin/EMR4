# Threat-model delta: clockwork-governed check-in successor resolution

Timestamp: 2026-08-19T14:26:41+10:00 (Australia/Brisbane)

## Scope

This delta covers a provider-free repository-governance decision and the generic second-tick repair needed to publish it. It opens no product, provider, practice, database, patient, appointment, clinical, deployment, release, Pages or protected-ref authority.

## Assets

- the seven canonical governance files;
- the three clockwork metadata files and live pointer;
- the exact current and predecessor Git generations;
- the active-operation authority and protected boundaries;
- the accepted check-in lineage and successor decision; and
- all user-owned untracked files, especially `docs/branding/`.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A caller supplies an abbreviated, stale or fabricated Git binding. | The tick accepts no caller-authored object binding; it machine-resolves clean `HEAD` to a full 40-character commit and verifies ancestry and protected refs. |
| A second publisher bypasses the live owner. | The existing retirement guards remain active; the generic tick uses the same `clockwork` writer identity, root, pointer and exclusive lease. |
| A stale prepared tick overwrites a newer generation. | The prepared bundle binds the complete predecessor pointer; publication rereads and requires exact equality before any replacement. |
| A partial filesystem failure leaves mixed canonical or metadata state. | All files are staged and reread, prior bytes are retained, and every pre-pointer exception restores canonical files, metadata files and the pointer before releasing the lease. |
| The pointer advances before the generation is complete. | `current.json` is replaced last and is the sole commit point. |
| Rollback returns to an ambiguous or reconstructed state. | The predecessor's canonical, metadata and pointer bytes are loaded from one bound full Git commit, digest-checked and restored under a new lease sequence. |
| Predecessor-specific protected boundaries leak into the successor. | The intent carries an exact next-boundary list; the reducer replaces inherited boundaries and validates the complete latch before publication. |
| Semantic input smuggles derived IDs, revisions, counts, digests or paths. | Recursive forbidden-key validation rejects all derived bindings; safe-path and exact-key schemas constrain the remaining inputs. |
| A physical newline conversion changes the generation. | Every prior canonical renderer input is loaded from the exact Git blob; portability tests vary physical line endings in a Git-clean worktree. |
| The successor decision accidentally enables ordinary practice. | The next tranche is architecture-only and default-off; secret values, database roles/sessions, practice selection and product/config changes remain forbidden. |
| A reviewer or worker gains write authority. | DeepSeek and native subagents are declined; Gemini, if used, receives one exact-candidate read-only veto package in an isolated clean worktree. |
| User-owned untracked evidence is swept into a commit. | Explicit-path staging is mandatory; `git add .` and `git add -A` are forbidden and `docs/branding/` remains outside every clockwork path. |

## Residual risk

The generic tick reduces repository closeout transcription and partial-publication risk; it does not prove occupied provider behavior or ordinary-practice safety. Filesystem replacement is not a multi-file OS transaction, so exact pre-pointer restoration and pointer-last visibility remain required. The first three qualifying live closeouts continue to report validation trips, rollback events, legacy-guard trips, manual derived-field edits and post-publication reruns so efficacy is measured rather than assumed.
