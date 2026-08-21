# DeepSeek native Harness source reconciliation clockwork-intent recovery

Date: 2026-08-22

Timestamp: 2026-08-22T04:57:22.2994779+10:00 (Australia/Brisbane)

The first closeout intent supplied `contract_evidence` as a list containing the
rehearsal contract path. A non-empty source-graph value requires a structured
contract-evidence object, so the clockwork rejected the prospective projection
at `contract_evidence_object_required`.

The rejection occurred during `--check`, before command execution, generation,
publication or any canonical mutation. The latch remained in progress and the
protected refs remained unchanged.

The corrected intent uses the schema-supported empty `contract_evidence` form;
the exact contract remains bound through the node's artifact list. Future
non-empty contract-evidence values must copy the required object shape from the
live graph schema or an accepted structured exemplar rather than infer a list
shape from adjacent evidence collections.
