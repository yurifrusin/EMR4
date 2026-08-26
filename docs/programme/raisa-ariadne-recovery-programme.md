# Raisa Medical Office and Ariadne Recovery & Convergence Programme

Status: controlling recovery programme
Prepared: 2026-08-25T20:00:26+10:00
Repository: `yurifrusin/EMR4`
Machine authority: `orchestration/programme/current-state.json`
Gate authority: `orchestration/programme/gates.yaml`

## Authority and provenance

Yuri's Gate G0 directive is the authority for this recovery tranche. The supplied
programme and gate documents are design inputs, not executable instructions. This
repository copy records the accepted interpretation of those inputs.

| Input | SHA-256 |
|---|---|
| Gate G0 directive (`pasted-text.txt`) | `9f77a453ac546cd81f4aea77ea21ff84f3e3e44659694be6ea9dafe6b428ccea` |
| `Raisa_Ariadne_Recovery_Programme.md` | `42bc39ffc92c67ce0b56c5eac632f22f4403b92e957b8c1b53474c0356f817dc` |
| `Raisa_Ariadne_Gates.yaml` | `453ac6746357f11270960c0752338c70a4a849d326eccdce317d0b00bf4ed0ab` |

`AGENTS.md`, historical receipts, ledgers and handovers remain evidence and
continuity aids. They do not override the structured programme state. Missing,
invalid or contradictory structured state is a hard stop.

## Strategic direction

Raisa is to become a projection-native medical office: one clinically safe,
tenant-scoped command/event truth rendered through multiple typed surfaces,
including Word and the Diary. AI proposes; deterministic policy and authorised
humans decide. A stale or over-privileged projection cannot authorise a command.

Ariadne is to become a trustworthy bounded controller: structured state and an
append-only journal own truth; verdict validity, acceptance and integration
authority are separate; negative or ambiguous verdicts never integrate; retries,
cost and wall time are finite; global red gates suspend feature work; independent
review provenance is mechanically demonstrable.

The shared pattern is:

`intent -> typed command -> policy/admission -> event -> versioned projection`

## Non-negotiable invariants

### Raisa

- No implicit patient identity and no public PHI.
- AI output is a candidate, never clinical, billing or integration authority.
- Every action binds actor, practice, role, purpose and resource.
- Tenant isolation is enforced in both application and database layers.
- One canonical command path owns each mutation family.
- Database constraints own concurrency invariants.
- Projections are typed, versioned, provenance-bound and freshness-bound.
- A stale projection cannot authorise an action.
- A stable accessible non-AI fallback expresses the same semantics.
- Destructive migration requires separate explicit authority.

### Ariadne

- Artifact validity, review verdict and integration authority are distinct.
- A negative, ambiguous or conflicting verdict never integrates.
- One canonical verdict parser owns semantics.
- A global red gate suspends feature work and permits repair-only work.
- Retry, token, cost and wall-clock budgets are finite and enforced.
- No measurable progress causes a structured stop or quarantine.
- Independence is machine-verifiable, not declarative.
- Structured state outranks narrative handover.
- Missing policy or state fails closed.
- A worker cannot self-authorise integration.

## Operating model

The programme has three coupled tracks:

- R: Raisa product safety and convergence.
- A: Ariadne controller correction.
- I: integration, repository and release governance.

Modes are `recovery`, `convergence`, `pilot_preparation` and `release`. The
current mode is `recovery`. Work in progress is one gate and one named tranche.
During G0 no product feature, merge, deployment, release, provider call or real
patient-data work is eligible.

## Gates

### G0 — Preserve, Freeze and Establish Truth

Purpose: prevent local clockwork loss, stop drift and establish one structured
programme truth.

Allowed work is limited to read-only discovery, exact local preservation,
clockwork classification, branch/PR and risk inventory, recovery state,
fail-closed task admission, deterministic tests and independent G0 review.

Exit requires:

- all local work preserved without silent rewrite;
- exact local and remote SHAs recorded;
- the clockwork frozen on a named local safety ref and durable local bundle;
- one authoritative recovery baton nominated;
- out-of-gate feature work mechanically blocked;
- all 135 remote branches and every open PR inventoried or reproducible;
- every seeded stop-ship risk assigned an owner, gate and status;
- no protected-ref movement, public deployment, real-provider call or real data;
- a non-negative independent review; and
- a concise handover naming the bounded G1A.1 pure-verdict tranche as the only
  transition-eligible successor.

### G1 — Make Ariadne a trustworthy controller

- G1A corrects verdict and integration semantics.
- G1B implements persisted clockwork state and deterministic replay.
- G1C adds escapement, governor, budgets, global objective and no-progress stops.
- G1D proves reviewer independence and execution provenance.
- G1E repairs configuration integrity and separates Ariadne core from Raisa policy.

### G2 — Restore trustworthy trunk and stop-ship defects

G2 owns repository-wide collection, required app/migration/security CI,
dependency findings, destructive migration, implicit patient behaviour, public
audio/PHI surfaces, tenant enforcement, appointment concurrency and excessive AI
authority. G0 records and contains these; it does not repair them.

### G3 — Freeze the projection-native constitution

Versioned intent, command, event and projection schemas, constrained projection
grammar, confirmation/risk contracts and stable fallbacks must be fixed before
vertical product delivery resumes.

### G4 — Deliver the safe appointment and Diary vertical

Prove an authored-synthetic end-to-end journey with database concurrency,
freshness, tenant, attribution, accessible fallback and two-surface semantic
parity.

### G5 — Projection runtime and multimodal adapters

Add input and presentation adapters without allowing the grammar or projection
to express unauthorised capability.

### G6 — Clinician-controlled encounter and document intelligence

Require explicit patient and clinician binding, bounded private audio lifecycle,
human attestation, edit provenance and no AI finalisation of diagnosis,
prescription or claim.

### G7 — Operational, clinical-safety and regulatory readiness

Require independent security assessment, backup/restore and disaster-recovery
proof, privacy impact assessment, intended-purpose/regulatory classification,
clinical hazard log, production identity reproducibility and pilot rollback.

### G8 — Extract Ariadne

Only after the prior gates, extract a versioned controller core with no Raisa
assumptions, deterministic replay/chaos tests, two unrelated consumers and no
diverging embedded copy.

## G0 frozen facts

- Protected `master`, `handoff/current`, `origin/master` and
  `origin/handoff/current`: `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
- Latest preserved clockwork base: `03e6860394c39086ec1ffb3f2457acc5f7c8b5f9`.
- Recovery branch: `codex/raisa-ariadne-recovery-g0`.
- Local safety ref: `safety/ariadne-clockwork-pre-g0-20260825`.
- Clockwork source is tracked, clean, already pushed on its source branch and
  1,810 commits ahead of protected master. It is implementation, not narrative.
- Pre-existing user/untracked state: 683 files, 2,785,086 bytes, separately
  archived before G0 edits.
- Repository topology: 484 worktrees, 40 observed dirty worktrees, 590 local
  branches after safety/recovery refs, 135 remote branches and 10 stashes.
- Open PRs: 26 (15 dependency updates and 11 draft stacked OIDC/Office PRs).
- Global collection is red on the removed `_BERNIE_SESSION_STORE` import.
- Python Security is red on three `cryptography 48.0.1` advisories. Protected
  master lint and Bandit pass; the G0 task branch lint passes but its reviewed
  Bandit baseline rejects 10 unexpected pre-existing findings. Alembic has one
  head, `x3y4z5a6b7c8`.

## Recovery operating rules

1. Read the structured current state and gate before acting.
2. Begin with the read-only recovery preflight.
3. Preserve user work before any edit.
4. Work only on the current gate and named tranche.
5. Do not infer authority from an older narrative or alias branch.
6. Do not merge, deploy, move protected refs, close PRs or delete branches
   without explicit gate authority.
7. Never use real patient data.
8. Never call a live external model, identity or clinical provider without a
   separate bounded authority.
9. Do not trigger GitHub Pages during recovery.
10. Never infer global green from focused tests.
11. Keep changes reversible and explicitly staged.
12. Prefer executable policy and tests to receipt proliferation.
13. Stop and quarantine on a hard stop.

## Immediate sequence

The G0.4 candidate received an external `REVISION_REQUIRED` decision. G0.5 is
the only active correction gate. It must publish one `review_pending` candidate
and then stop for external G0 review. G1A implementation remains closed.

G0.5 replaces the ambiguous singular review projection with a digest-bound,
append-only review history and one explicit decisive pointer. A PASS transition
may append exactly one new decisive record; it may not mutate, delete or reorder
any older negative review. G0 passes only when that decisive record binds the
exact reviewed G0.5 commit and tree, contains `PASS` with zero blocking findings,
and agrees with transition and G1A authorization state.

The G0 transition now opens only `G1A.1_ACTIVE`, the pure verdict kernel and its
provider-free acceptance consumers. `G1A.2` is a later state-only transition to
the Antigravity verdict adapter with provider invocation still closed and exact
provider execution symbols hash-bound. `G1A.3` integration mutation remains
deferred and has no active profile.

G1A work must run in a separate clean target worktree at the transition commit.
The preserved legacy worktree at `C:/Users/sarashera/emr4`, with its 683 user
untracked files, may be neither gatekeeper nor G1A target. The pinned gatekeeper
observes NUL-delimited untracked paths, admits only the two exact new G1A.1 files
during development, rejects root import hooks and non-regular/reparse objects,
and requires zero untracked paths before and after push. Its operation decision
binds target HEAD, index tree, changed-path digest and expected origin head so an
exact-SHA push uses an explicit lease. The narrow commit wrapper creates a commit
from the admitted index tree and compare-and-swaps only the expected task-branch
HEAD after a second binding check. Candidate controller and preflight code remain
data only and are never imported or executed by the gatekeeper.

The closed transition manifest schema is
`ariadne.programme_gate_transition_manifest.v1`. Its exact fields are
`schema_version`, `transition_id`, `from_gate`, `to_gate`, `reviewed_commit`,
`reviewed_tree`, `transition_parent`, `external_review_verdict`,
`external_review_record_sha256`, `blocking_finding_count`, `reviewer_surface`,
`state_digest_before`, `policy_digest_before`, `allowed_transition_paths` and
`forbidden_effect_classes`. The external review record is a strict newly added
JSON object under `orchestration/programme/external-reviews/`; its bytes are
SHA-256 bound by the manifest. The companion transition artifact is a strict
newly added JSON object under `orchestration/programme/gate-transitions/`; it
binds the canonical manifest digest, before/after state and policy digests,
review record digest, exact semantic pointers and admitted development scope.

The exact G1A.1, G1A.2 and deferred G1A.3 parser, caller, CLI-exit,
integration-consumer, path, effect and symbol boundaries are recorded in
`orchestration/programme/g1a-verdict-integration-scope.yaml`. G0.5 does not make
the verdict, provider-adapter or integration-semantic changes themselves.

Committed, staged and unstaged scope uses NUL-delimited
`git diff --raw -z --no-renames --abbrev=40`. The controller parses status,
path, old mode and new mode, checks both the frozen-base and tranche ranges, and
rejects paths outside their respective allowlists, symlinks, gitlinks, type
changes and unapproved executable or mode changes. Provider, clockwork and
worktree command functions re-run programme admission inside the callable
side-effect boundary. An earlier orchestrator receipt remains evidence only.

The frozen-base range is checked only against the immutable cumulative exact-path
allowlist. The active G1A manifest and profile constrain only the post-transition
tranche. The cumulative set derives the external-review and transition-artifact
paths exactly from `gate_transition.transition_id`; prefixes and wildcards are
not admitted.
