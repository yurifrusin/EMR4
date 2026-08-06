# Independent veto packet: Context Fabric Current operational weave

Date: 2026-08-06

You are the independent Gemini 3.6 Flash/high veto reviewer. Review only the
exact committed candidate below. Do not edit any file and do not implement a
repair.

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\cow-r1`
- Branch: `codex/review-context-fabric-current-operational-weave-d8bc059`
- Required HEAD: `d8bc059212e65a6ed2d7ac8d57734096d14b9139`
- Candidate branch is non-protected and must remain clean and unchanged.
- Accepted parent and task-branch base:
  `619dbc3b9d7ce5610c75031f76c14a4ebbd7fa5f`.

## Review objective

Determine whether this provider-free authored-synthetic Current operational
weave safely composes the exact four existing read shapes without creating new
authority, API, retrieval, runtime or command surfaces. Look for any material
defect that lets a candidate supply authority; widens Bureau, purpose, frame,
source, field, location, time, freshness, cardinality or bytes; permits source
substitution or stale/superseded/tampered release; merges distinct source
semantics; fails cross-source coherence or same-packet proofreading; leaks
private session material; or overstates what the evidence proves.

Inspect at least:

- `docs/raisa-provider-free-practice-context-fabric-current-operational-weave-plan.md`
- `docs/raisa-provider-free-practice-context-fabric-current-operational-weave-design.md`
- `docs/security/raisa-provider-free-practice-context-fabric-current-operational-weave-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-current-operational-weave/operational-weave-contract.schema.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-current-operational-weave/operational-weave-contract.example.json`
- `orchestration/continuity/raisa-provider-free-practice-context-fabric-current-operational-weave/provider-free-acceptance-evidence.json`
- `scripts/raisa_provider_free_practice_context_fabric_current_operational_weave.py`
- `scripts/raisa_provider_free_practice_context_fabric_current_operational_weave_acceptance.py`
- `tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py`
- the accepted parent Context Fabric contract and API Spine artifacts needed to
  verify the claimed source shapes and unchanged read/command separation.

Adversarially verify:

1. the candidate is closed and cannot supply principal, role, practice,
   session, consent, retention, command, provider or write authority;
2. backend authority, need, grant, every source, frame, frame set and trace are
   closed and digest-bound, and the proofreader independently recomputes need,
   grant, sources, coherence and the exact released packet;
3. scope intersection can only preserve or narrow Bureau, purpose, frame,
   source, field, location, half-open time, freshness, frame/item/byte limits;
4. exact frame/source/contract triples, practice/session/location binding,
   authored-synthetic labels, current supersession and freshness/expiry are
   fail-closed;
5. missing or duplicate required sources block atomically, waiting-room
   appointments resolve to Diary, all practitioner refs resolve to active
   directory entries, and session date/location/focus match the same Diary;
6. optional fields are projected only after backend field intersection, source
   identities and canonical order remain visible, and no frame becomes command
   or present-authority evidence;
7. the private session shape excludes prompts, turns, transcripts, credentials,
   authority envelopes, cached source rows and reader functions;
8. no GraphQL root/resolver/route, REST command, subscription, application
   source, provider, network, database, subprocess, filesystem-write, product
   runtime, deployment or protected surface was added; and
9. evidence uses canonical-LF artifact hashes with exact HEAD bound externally,
   never an impossible committed self-HEAD, and claims only provider-free
   authored-synthetic pure composition.

Provider-free tests are permitted. Use the primary checkout's Python runtime
while keeping this review worktree as cwd:

`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py tests/test_raisa_practice_context_fabric_direction.py tests/test_api_spine_artifacts.py tests/test_bernie_context_frames.py tests/test_ariadne_orchestrator_preflight.py tests/test_agents_acceptance_index.py tests/test_ariadne_agent_error_register.py`

Do not use or request additional cloud authentication or provider calls beyond
this authorised Antigravity review; do not inspect protected holdouts,
historical diary material, patient/clinical/product data or `docs/branding/`;
do not start a product runtime, database or browser; do not write, commit, push,
deploy, release, rebuild Pages or move any Git ref.

## Decision contract

Report concise evidence and every material finding with file and line. If any
material uncertainty remains, require revision. Complete and synchronously wait
for every command and test before returning the final object. Put the complete
evidence and findings in the `review` string and set `decision` exactly once to
`pass` or `revision_required`. Return only the closed schema-constrained object.
Do not write a `DECISION:` marker, provisional verdict, post-final status or
background-completion follow-up inside `review`.
