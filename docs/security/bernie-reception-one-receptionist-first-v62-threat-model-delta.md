# Reception One Receptionist-first v6.2 Threat-model Delta

## Boundary classification

v6.2 changes a provider-bound, proposal-only agent context frame. It does not
open a GraphQL mutation, REST write, database read, product runtime, event
runtime, memory system or deployment path.

## New surfaces and controls

- **Readable context becomes excess disclosure.** The desk context includes one
  request-local selected appointment and grounded mentions only. It excludes
  unrelated Diary rows, broad patient history, clinical data and historical
  material.
- **Selected context overrides explicit intent.** The frozen resolution order
  gives the latest explicit staff instruction priority. Selected appointment
  context assists reference resolution but cannot turn an explicit create into
  a move.
- **Context is mistaken for authority.** Every context frame is labelled
  `context_only_no_command_authority`; the effect ceiling remains
  `proposal_only`, and the deterministic command boundary retains all writes.
- **Model and proofreader see different facts.** Both receive the same frozen
  turn input. The proofreader recomputes and verifies the desk-context and task
  hashes before admission.
- **Stale or superseded context is used.** Revision and timestamps are carried
  into the desk context and remain subject to the existing deterministic
  freshness and supersession review.
- **Dialogue grows into memory.** At most four current-request staff utterances
  are included. No cross-session memory, RAG or GraphRAG is introduced.
- **Natural speech becomes executable.** The receptionist response and decision
  note remain separately reviewed audit text and are never parsed into typed
  fields.
- **A readable identifier leaks into routine audit.** External audit retains
  context and task hashes plus admitted typed fields, not the raw prompt,
  provider packet or hidden reasoning.
- **A full-cohort rerun is presented as independent evidence.** All artifacts
  identify the twenty-four cases as the reused frozen v6 development cohort.
- **Repeated calls escape their budget.** Each case has one primary and at most
  one terminal second call, each with a distinct ledger; the absolute ceiling
  is forty-eight and USD 1.

All inherited exact Sydney endpoint, Gemini 2.5 Flash, Bernie project and
impersonated identity, keyless ADC, no-fallback, no-tool, no-product, cleanup
and audit controls remain unchanged.
