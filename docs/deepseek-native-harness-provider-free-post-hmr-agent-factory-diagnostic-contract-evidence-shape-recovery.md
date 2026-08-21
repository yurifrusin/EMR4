# Native agent-factory diagnostic contract-evidence shape recovery

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

Status: **corrected before commands or canonical publication**

The first prospective closeout intent placed three ordinary contract/schema
file paths in the Continuity node's `contract_evidence` field. That field is a
structured graph surface, not an alternative artifact list. The clockwork
rejected `contract_evidence_object_required` before running the command
manifest or changing canonical state.

The corrected intent retains all three paths under `evidence.artifacts` and
uses an empty `contract_evidence` list. Future intents route ordinary files
through the evidence inventory and use `contract_evidence` only for objects
that satisfy the graph's structured schema.
