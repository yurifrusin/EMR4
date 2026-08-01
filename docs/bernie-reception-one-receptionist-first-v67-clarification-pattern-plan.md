# Reception One Receptionist-first v6.7 Clarification Pattern Plan

Status: active bounded repair plan
Recorded: 2026-07-30

## Purpose

Repair the sole v6.6 no-release terminal without revising any historical node.
The `b-clarify-fit` goal, typed operator, evidence bindings and internal note
were exact on both v6.6 turns. The deterministic proofreader rejected only
because the natural response used none of its frozen clarification markers
after the bounded correction ticket.

The complete original twenty-four-request authored-synthetic cohort will be
rerun, including every earlier pass. v6.6 remains immutable and no v6.6 ledger
may be reopened.

## Exact repair

The system instruction will teach one proofreader-compatible receptionist
clarification pattern:

- begin the natural response with exactly `Which do you mean:` or
  `Could you clarify:`;
- ask one focused question using only facts present in the request and typed
  desk context;
- where the ambiguity is fit-in versus ordinary booking, name those two
  alternatives without inventing a booking fact; and
- end with exactly `No booking was changed.`

After a correction ticket reports `receptionist_response_goal_mismatch` for
the clarification goal, the model must replace the complete natural response
using that pattern. It must not preserve or paraphrase the rejected wording.

The deterministic proofreader, including its frozen clarification marker
table, remains unchanged. The output schema, typed operator catalogue,
semantic-role constraint gate, desk context, 3072-token response ceiling,
temperature zero and 1024-token thinking budget remain unchanged.

## API Spine boundary

The model receives only typed, minimal, source-labelled, freshness-bound,
non-authoritative authored-synthetic context. It may interpret and propose.
The descendant adds no GraphQL read, REST command, async command authority,
product/database access, confirmation or appointment mutation.

## Frozen boundaries

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- identity:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: existing keyless impersonated service-account ADC;
- location: `australia-southeast1`;
- endpoint: `australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- 24 primaries and at most one terminal second call per case;
- absolute 48-call and USD 1 ceiling;
- no API key, static key, global endpoint, fallback, provider tool, grounding,
  retrieval, cache creation, product/database access, appointment write,
  product delivery, production, deployment or release; and
- raw prompts, raw provider responses, credentials, API-key information and
  hidden chain-of-thought are not retained.

The no-show-to-`dna` alias remains closed.

## Deterministic gates

Before an occupied call:

1. a safe but marker-free clarification response rejects with
   `receptionist_response_goal_mismatch`;
2. its correction ticket retains only the bounded field/code/path contract and
   no rejected prose;
3. an exact compatible replacement with the same typed form admits;
4. the system instruction explicitly teaches the complete response pattern and
   replacement action;
5. all twenty-four reference forms and all historical wrong forms retain their
   existing deterministic dispositions;
6. provider-blocked, real-isolation, focused, API Spine, Continuity, Compass,
   JSON, compilation, Ruff and whitespace gates pass;
7. the exact read-only Bernie/Sydney cloud-control preflight passes;
8. pre-run residue is zero; and
9. Continuity and the rendered Compass revisions bind the frozen candidate.

Once occupied execution starts, no prompt, schema, proofreader, desk-context or
generation-setting change is permitted.

## Acceptance

Capability acceptance requires all twenty-four terminal outcomes to match
their frozen oracle, all ledgers and audit chains to close, no call after the
terminal result and zero task residue. Any mismatch closes v6.7 candidly and
releases no product capability.

The evidence remains a reused development cohort, not an independent holdout.
The Sydney locational path does not prove Australian physical or sovereign
processing.
