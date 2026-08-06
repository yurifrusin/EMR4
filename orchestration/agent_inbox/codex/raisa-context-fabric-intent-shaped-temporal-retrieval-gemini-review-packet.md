# Independent veto packet: Context Fabric intent-shaped temporal retrieval

Date: 2026-08-06

You are the independent Gemini 3.6 Flash/high veto reviewer. Review only the
exact committed candidate below. Do not edit any file and do not implement a
repair.

## Exact candidate

- Worktree:
  `C:\Users\sarashera\EMR4-worktrees\context-fabric-intent-retrieval-review`
- Branch: `codex/review-context-fabric-intent-retrieval-be2ac70`
- Required HEAD: `b24b56bda296f3713b5e2c0e52545c749e71540a`
- Candidate branch is non-protected and must remain clean and unchanged.
- Exact implementation parent: `be2ac70ffb8594c6724b633414755e2ab7924033`.

## Review objective

Determine whether this provider-free, patient-free and unmounted rehearsal
safely converts one closed intent candidate into the minimum authorised
Current, Bureau Memory and/or bitemporal Historical components without creating
new identity, brand, provider, API, runtime, clinical or command authority.

The permanent architecture direction says Reception One and Clinician One are
branded workspace/projection families, not authorisation domains. Consultant,
requests/referrals, medicines/prescribing and billing/claims remain separately
governed future Bureaus. Verify that this candidate demonstrates read-context
interweaving only and cannot use a brand, screen, occupational label or another
Bureau's private state as authority.

Inspect at least:

- `docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-plan.md`
- `docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-design.md`
- `docs/security/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal/intent-shaped-temporal-retrieval-contract.schema.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal/intent-shaped-temporal-retrieval-contract.example.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal/provider-free-acceptance-evidence.json`
- `scripts/raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py`
- `scripts/raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal_acceptance.py`
- `tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py`
- the accepted Bureau Memory, Current operational and patient-free temporal
  parents plus API Spine artifacts needed to verify source semantics.

Adversarially verify:

1. the closed candidate cannot supply principal, role, practice, location,
   session, retention, provider, patient, prompt, SQL/vector query, source truth
   or command authority;
2. the backend binding—not Reception One, Clinician One, a screen or role
   label—owns exact Bureau, intent, component, profile, time, cardinality, byte,
   alternative, session-generation and bilateral-sharing authority;
3. accepted lowercase Memory and uppercase Current/Historical vocabularies use
   one exact mapping and never implicit case folding or guessed aliases;
4. the four-source Current weave remains one atomic coherence component while
   its projected facts are minimal; it cannot be shared across Bureaus because
   it contains private application-session state;
5. Bureau Memory may cross only through the exact bilateral
   `requesting<-origin:purpose` grant, and rejection is uniform without counts;
6. each upstream proofreader is recomputed before facts are projected, the
   backend binding seals the exact catalog digest, and every released component
   retains exact upstream packet, binding, proofreader, frame/source and
   revision provenance;
7. Current `REASSEMBLY_REQUIRED`/expired/superseded state and missing historical
   coverage fail closed; `valid_at` plus `known_at` distinguishes known-then
   from corrected-later and a gap is not treated as absence;
8. two equally admissible opaque recent-work references return bounded,
   canonical alternatives with `identity_asserted:false`, never a guessed
   person/patient/event;
9. the same-packet proofreader independently reconstructs plan, selection,
   projection, ambiguity, temporal state, provenance and digest bindings and
   blocks content or provenance tamper;
10. no GraphQL root/resolver/route, REST command, subscription, application
    source, provider, network, database, subprocess, filesystem-write, product
    runtime, clinical/prescribing/referral/billing operation, deployment or
    protected surface was added; and
11. the evidence uses canonical-LF artifact hashes with exact HEAD bound
    externally and claims only pure authored-synthetic selection.

Provider-free tests are permitted. Use the primary checkout's Python runtime
while keeping this review worktree as cwd:

`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py tests/test_raisa_practice_context_fabric_direction.py tests/test_api_spine_artifacts.py tests/test_ariadne_orchestrator_preflight.py tests/test_ariadne_agent_error_register.py -p no:cacheprovider`

Do not use or request additional cloud authentication or provider calls beyond
this authorised Antigravity review. Do not inspect protected holdouts,
historical Diary material, patient/clinical/product data or `docs/branding/`.
Do not start a product runtime, database or browser. Do not write, commit, push,
deploy, release, rebuild Pages or move any Git ref.

## Decision contract

Report concise evidence and every material finding with file and line. If any
material uncertainty remains, require revision. Complete and synchronously wait
for every command and test before returning the final object. Put the complete
evidence and findings in the `review` string and set `decision` exactly once to
`pass` or `revision_required`. Return only the closed schema-constrained object.
Do not write a `DECISION:` marker, provisional verdict, post-final status or
background-completion follow-up inside `review`.
