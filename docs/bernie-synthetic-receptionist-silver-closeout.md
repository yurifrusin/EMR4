# Bernie Synthetic Receptionist-to-Assistant Silver Corpus Closeout

Date: 2026-07-17

Status: `accepted_development_silver`

## Outcome

EMR4 now has a bounded synthetic corpus for Bernie's actual language target:
instructions from a trained receptionist to an assistant. It contains 192
deterministic noisy dialogue candidates over 96 ordinary LC development
semantic anchors, with two variants per anchor and balanced coverage of eight
dialogue forms.

The accepted exact candidate is:

- file: `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`;
- source commit: `b1380f6aaf6eb21d9af763cfcc8db5130cba138d`;
- file payload hash:
  `sha256:193b705e0ce06fa32b72a063dec659e52a584fc489137bd7cbad8e511940e37f`;
- canonical record hash:
  `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`;
- admission manifest:
  `tests/fixtures/bernie_synthetic_noise/admission.json`.

All 192 are admitted as ordinary development Silver evidence. Their immutable
generation records retain `adjudication=pending`; the separate admission
manifest records Sol's post-review decision so the reviewed candidate hash is
not rewritten after review.

## Coverage

- Actions: create, move, resize, cancel, status change, and schedule
  explanation, 32 candidates each.
- Dialogue forms: one-shot, clarification, correction, reversal, ellipsis,
  anaphora, repetition, and session restart, 24 candidates each.
- Noise levels: 96 medium and 96 high.
- Surfaces include fillers, abbreviations, staff shorthand, reordered slots,
  speech disfluency, transcript-like fragmentation, explicit correction,
  reversal, ellipsis, and anaphora.
- Every evidence span exactly slices the generated receptionist utterance.
- Every authority field is false.

## Provenance and review sequence

No external dialogue or historical diary data was used. A dialogue-free seed
exporter derived semantic anchors from the ordinary LC development corpus;
protected V1-V10 material remained sealed.

The first three-model generation wave was rejected before admission because a
Sol-owned exporter selected the wrong dialogue-form variant for 84 anchors.
Sol corrected the exporter and adopted only the Codex generator source as an
untrusted recovery input. The resulting first reviewed hash passed DeepSeek
and Gemini, but Sol found 18 unsupported `correction` operation labels and
returned it as `revision_required`.

After the metadata-only amendment, fresh contexts independently reviewed all
192 records on the final hash:

- DeepSeek V4 Flash/high: `pass`, accept 192, quarantine 0, reject 0;
- Gemini 3.5 Flash/medium: `pass`, accept 192, quarantine 0, reject 0;
- Sol: `accept_development_silver`, accept 192, quarantine 0, reject 0.

The correction loop did not change dialogue, semantic anchors, evidence
spans, provenance, or authority. It removed only 18 unsupported operation
labels and added a regression check that every remaining correction label has
an explicit text surface.

## Verification

```text
seed manifest check: pass, 96 anchors
central candidate validator: pass, 192 candidates
focused pytest: 12 passed
DeepSeek round 2: pass, 192/192 accepted
Gemini round 2: pass, 192/192 accepted
```

## Bounded meaning

This corpus is useful for ordinary development evaluation, synthetic-noise
robustness work, and future development candidate generation. It does not
establish that the language distribution matches a real Australian practice,
and it is not clinical validation, Gold evidence, a protected holdout, or
certification evidence.

Nothing in this closeout opens T3.5, a live provider, runtime prompts,
confirmation, routes, API/database/UI changes, deployment, release, or diary
write authority. The native backend remains authoritative.

## Next safe work

The corpus pilot is complete. A future separately authorized development
sprint may use the admitted Silver set to measure current interpreter
robustness and identify ordinary-development gaps. It must not tune against or
reopen protected holdouts, and any material parser/policy behavior decision
returns to Yuri's boundary.

DECISION: accept_development_silver
ACCEPT: 192
QUARANTINE: 0
REJECT: 0
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
