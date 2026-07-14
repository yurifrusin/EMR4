# LC4R4 Normalization/Entity Evidence Repair — Sprint Contract

Date: 2026-07-14

Active Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator: GPT Sol. Planning mode is
`sol_direct_routine`. DeepSeek V4 Flash/high through Claude Code `--bare` owns
one bounded implementation/test lane. Gemini 3.5 Flash through Antigravity
owns the independent veto review. DeepSeek Pro is not a Conductor or worker
for this sprint.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only profiling isolated a small deterministic
entity-state repair and a normalization evidence-classification task. There is
no architecture or product-policy dispute. External models do not plan,
allocate, accept, or integrate this sprint.

## Protected evidence boundary

Use only the ordinary Silver/pending LC4 development partition and new
independently authored synthetic regressions. Do not open, enumerate, import,
load, regenerate, evaluate, hash-check, infer from, or tune against protected
holdout v1 or any of its fixtures, support modules, seals, receipts, or
reports. Do not inspect historical diary material or transmit patient/practice
data. No provider inference, T3.5 adapter, route/API, database, UI, deployment,
memory, RAG/GraphRAG, confirmation, or write authority is permitted.

The worker must not edit generated development fixtures or use expected
scenario fields inside interpretation. Selection and interpretation must
derive from utterance surfaces only; scenario expectations remain scorer
oracles.

## Frozen development evidence

LC4R3 leaves 584 one-repeat `aligned_failure` records. Among these, Sol froze
two genuine patient-entity surface families:

| Surface-derived family | Current miss | Aligned records | Selection hash |
|---|---|---:|---|
| standalone `someone` patient reference | `omitted` instead of `ambiguous` | 70 | `50260edcf0fa2c0d` |
| an initially ambiguous patient reference followed in a non-correction turn by an explicit name | remains `ambiguous` instead of resolving to `exact` | 13 | `485cd258fd5ebd60` |

The implementation naturally affects every matching development surface, but
the accepted target remains the frozen 83 aligned misses. The report must also
record full-partition effects so improvements outside that target are not
hidden or relabelled as adjudicated coverage.

Sol also classified all 489 aligned normalized-value failure records by their
field-level evidence. At scenario level the mutually observed signatures are:

| Difference signature | Records |
|---|---:|
| unsupported expected value without a source span only | 298 |
| surface value disagrees with contract plus unsupported expected value | 114 |
| surface value disagrees with contract only | 31 |
| observed surface value absent from contract plus unsupported expected value | 17 |
| all three conflict types | 15 |
| observed surface value absent from contract plus surface disagreement | 12 |
| observed surface value absent from contract only | 2 |

No aligned normalized-value failure is a missing observed value backed by a
matching explicit source span and matching Silver value. LC4R4 must therefore
report these conflicts and make no normalization parser change merely to echo
unsupported defaults or contradictory labels.

## Objective A — Patient entity semantics

Extend the pure, oracle-free patient entity detector so a standalone
`someone` reference is explicitly ambiguous. In multi-turn reduction, allow a
later non-correction turn containing an explicit patient name to resolve a
previously `omitted` or `ambiguous` patient reference to `exact`.

Do not weaken actual correction semantics: a correction that changes one
explicit patient name to another remains `corrected`. Do not infer a patient
from pronouns alone, and do not add appointment, practitioner, location,
appointment-type, duration, action, tool, route, or authority assumptions.

## Objective B — Honest normalization gap report

Add a deterministic LC4R4 report/check which recomputes the frozen aligned
selection and classifies every aligned normalized-value failure using only:

- expected key/value evidence in the scorer contract;
- observed extraction values;
- explicit source-span presence; and
- the already established aligned-development audit category.

The classification is diagnostic only. It must not feed expected values or
source-span labels into extraction. It must fail closed if a new category
appears, the corpus changes, a target selection changes, or a normalization
parser result is silently altered.

## Objective C — Authored regressions and boundaries

Add focused authored tests proving:

- `Book someone with Dr Shera tomorrow at 3pm` yields patient `ambiguous`;
- a later explicit patient name resolves an initial `a patient` reference;
- pronouns such as `she`, `he`, or `they` do not become exact patients;
- explicit-name-to-explicit-name corrections remain `corrected`;
- standalone words containing the substring `someone` do not overmatch;
- lossless normalized turns and exact `tomorrow at 3pm` values remain intact;
- unsafe, negated, clarification, and tool/authority boundaries do not change;
- mutating expected scenario fields cannot change the oracle-free observation;
  and
- no normalized value is synthesized from an expected default without surface
  evidence.

## Owned implementation surface

The worker may edit:

- `app/services/bernie/semantic_extraction.py`;
- focused LC4R4 and semantic extraction tests under `tests/`;
- one LC4R4 report/check script under `scripts/`;
- one deterministic JSON report and concise implementation note under `docs/`;
  and
- one completion artifact under `orchestration/agent_inbox/codex/`.

The worker must not edit `AGENTS.md`, generated scale fixtures or generators,
scenario schema, replay/audit policy, action grammar or route contracts,
providers, routes/API/OpenAPI/GraphQL, database/migrations, UI, T3 gates,
deployment, or protected-evidence surfaces.

## Acceptance

The pre-LC4R4 full-development semantic baseline is:

- intended action `880/1152`;
- action semantics `730/1152`;
- temporal relation `628/1152`;
- normalized values `101/1152`;
- entity semantics `255/1152`;
- clarification `698/1152`; and
- safety `1152/1152`.

Acceptance requires:

- patient field correctness for the frozen surface target `83/83`;
- the standalone-`someone` family `70/70` and resolved-additive family `13/13`;
- full entity-semantics pass count at least `300/1152`, with every full-partition
  effect disclosed;
- normalized values exactly preserved at `101/1152` and the 489 failure
  signatures reproduced exactly, unless Sol explicitly rejects an evidenced
  classifier defect;
- all other semantic baselines do not regress;
- safety `1152/1152` and measured per-scenario repeat variance zero;
- selection hashes and corpus hash reproduced deterministically;
- no fixture edits, expected-answer echo, pronoun promotion, or substring
  overmatch;
- focused tests, exact route regression, broad proportional LC1-LC4 and
  T1/T2/T3.1-T3.4 checks, blocked shadow gate, report `--check`, and
  `git diff --check` pass;
- Gemini returns `DECISION: pass` on the exact candidate head; and
- no protected-evidence, provider, T3.5, route/API, DB, UI, deployment, or
  write-authority boundary opens.

Sol will independently verify, own any recovery amendment, integrate, commit,
and push. Pause only at a documented user decision boundary.

Sprint engine state: continuing.
