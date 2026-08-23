# Raisa local-only historical Diary document-story time-coordinate bounded measurement recovery rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T07:14:21.5476552+10:00 (Australia/Brisbane)

Result: `revision_required`

Reviewed source: `5df44bd28ae60db773b6fd833d0d8cdecca45611`

Empirical source: `54eb390e0b0007c13cfb28615e4c9041db41696a`

## Conclusion

The operational recovery succeeded and the mapping hypothesis did not. The
sole fresh run opened and parsed all 80 bound snapshots within the 1,800-second
terminal, processed 12,557 structural segments, preserved 199 stable records
and 448 adjacent changes, and cleaned up Word without disturbing the user's
pre-existing process. Count-only progress made the run observable throughout.

Across the complete fixed slice, however, Word returned zero complete time
tokens in the main document story outside tables. Consequently every segment
was `same_page_anchor_unavailable`, no time was mapped and no interval mode was
available. This is a useful negative result: the main-story coordinate
hypothesis is closed rather than merely timing out.

## Privacy and first use

Source-value leakage and provider/model calls were zero. No source text,
filename, path, timestamp, page, coordinate, distance, key or mapping was
emitted. The private manifest, projection, Word control and progress sidecars
are absent; only generic aggregate, bind, cleanup and terminal readings remain
under the ignored local attempt root.

The internal structural uniqueness diagnostics are not a mathematical
probability of reconstructing a person's identity, and no such universal
probability is claimed. They reinforce the decision to evaluate any future
reusable derivative specifically. No reusable candidate exists here and the
first-use gate remains closed.

## Workflow issue and correction

Post-run verification found that the count-only progress sidecar survived the
normal cleanup. It contained no source values, but the plan required it absent.
The exact sidecar was removed, the cleanup routine now removes both process
control and progress state, and 190 provider-free controls plus all static
checks pass. Historical content was not retried.

A separate prepublication check rejected two draft Git bindings whose full
object IDs had been expanded from abbreviations instead of resolved. Every
binding was replaced with `git rev-parse` output before commit. Nothing had
been published. The distinct agent-origin binding lapse and repository-origin
cleanup defect are recorded as AER-1146 and AER-1147.

## Next work

Earlier committed aggregate evidence reported 78 time-like substrings in the
whole document, while two stricter measurements now show zero complete tokens
as table-cell segments and zero complete tokens in the main story outside
tables. The narrow next hypothesis is therefore a strictly leading explicit
time token within a table-cell segment—not a free embedded substring and not a
layout inference. The next tranche is authored-synthetic and provider-free
only; it cannot access the historical archive or open first use.
