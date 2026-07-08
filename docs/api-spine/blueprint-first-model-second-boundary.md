# Blueprint First, Model Second Boundary

Date: 2026-07-08

Sprint: 203

Source prompt: local review of `2508.02721v2.pdf`,
`Blueprint First, Model Second: A Framework for Deterministic LLM Workflow`,
arXiv `2508.02721v2`.

## Purpose

This note records the useful architectural lesson from the paper review and the
follow-up discussion about Bernie.

The paper's useful principle is that deterministic workflow code should own the
workflow path, while a language model is invoked only for bounded subtasks. For
EMR4, that means Bernie is trained to stay in the correct operational lanes in
the same sense a novice medical-practice employee is trained to use a practice
management system. Bernie may learn the diary vocabulary, workflow sequence,
and clarification/refusal patterns, but the backend remains the source of
authority.

## EMR4 Mapping

| Paper concept | EMR4 mapping | Boundary |
|---|---|---|
| Expert-authored execution blueprint | API Spine, Diary action grammar, route authority contracts, proposal/confirm commands, release gates | Workflow path is code-owned. |
| Model as bounded specialist | Bernie interpretation, fake-provider-compatible projected frames, advisory context labels | Model output is interpretation, not authority. |
| Programmatic validation | Pydantic schemas, OpenAPI command envelopes, fixture replay, static route-contract tests, leakage lint, idempotency/audit checks | Outputs are accepted only after typed checks. |
| Deterministic executor | FastAPI command plane, backend revalidation, idempotency storage, audit correlation | Commands execute only through backend-owned routes. |
| Tool composition | Read models, proposal builders, confirm routes, audit read models | Tools are purpose-built controls, not raw database levers. |

## Bernie Training Frame

Bernie should be trained like a novice receptionist, not by giving the model
unbounded memory or direct write authority, but by progressively teaching the
practice-management lanes:

- recognise the diary task being requested;
- ask for clarification when patient, practitioner, date, reason, or action is
  ambiguous;
- distinguish read-only explanation from proposal staging;
- know which native Diary verbs are implemented and which are planned only;
- prepare appointment create, move, resize, cancel, or status-change proposals
  only through typed backend affordances;
- require staff confirmation and signed evidence before any write;
- refuse attempts to bypass confirmation, invent availability, call raw routes,
  or claim completion before the backend confirms it.

Bernie's eventual reach should be comparable to a trained human receptionist's
diary reach, but through safer under-the-hood controls. Bernie should not get a
generic "write appointment row" lever. Bernie should receive high-level,
auditable tools such as availability reads, explanation frames, proposal
builders, signed confirmation commands, and audit-backed result frames.

## API Spine Rule

The stable EMR4 rule is:

> Bernie interprets; the backend blueprint decides; signed command routes
> mutate.

Consequences:

- GraphQL remains a scoped read/context graph only.
- REST/OpenAPI command routes own irreversible, high-risk, external, or
  auditable actions.
- Appointment proposal commands resolve current backend state before presenting
  staff with a confirmable envelope.
- Confirmation commands echo signed evidence/freshness and revalidate before
  writing.
- Model responses cannot create live availability facts, choose between
  ambiguous people, grant write authority, skip staff confirmation, or bypass
  audit.
- Agent context frames are labelled inputs, not workflow-control authority.

## Innovation Posture

This review reduces architectural uncertainty rather than creating a pivot.
The deterministic-first principle is an emerging reliability pattern, not an
experimental gamble. EMR4's innovation is the application of that pattern to
Australian general-practice operations:

- Microsoft Word as the clinical front end;
- a diary and practice-management API spine designed for agent participation;
- receptionist language mapped into signed, auditable command proposals;
- historical diary evidence converted into safe aggregate/profile/test layers
  instead of raw retrieval or model training material;
- multi-agent development review around explicit gates and closeouts.

The main remaining risk is product integration: making Bernie useful enough
while preserving these lanes.

## Gates Still Closed

This note does not authorize:

- provider prompt wiring or live provider calls;
- provider dry-run wiring;
- GraphQL mutations;
- memory/RAG/GraphRAG runtime wiring;
- H15/H-series runtime imports;
- historical diary material access;
- broad historical diary trove mining;
- external patient clients;
- runtime FGA clients;
- raw route mutation authority;
- direct database writes by model output;
- model-to-database writes outside REST command handlers.

## Next Sprint Use

Use this note as vocabulary and a boundary check before any future Bernie
runtime/provider proposal:

1. Name the deterministic blueprint that owns the workflow path.
2. Name the exact bounded model subtask.
3. Name the typed validation that accepts or rejects the model output.
4. Name the backend command or read model that owns the real action.
5. Re-run the relevant readiness/provider boundary command before proposing any
   runtime or provider opening.
