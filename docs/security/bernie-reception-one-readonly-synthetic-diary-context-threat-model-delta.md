# Threat-model delta: read-only synthetic Diary-context bridge

The new trust crossing is from the existing trusted product-context adapter to
the isolated frozen v6.8 work cell. The adapter owns all database reads and the
opaque-handle map. The cell receives neither the database session nor that map.

Controls:

- exact development-only, practice-allowlisted, authored-synthetic fixture;
- bounded practice-scoped queries and one selected appointment;
- request-scoped opaque handles, source labels and two-minute freshness;
- model-visible packet contains no raw UUID, full Diary or unselected
  appointment payload;
- identical hash-bound packet is evaluated by the deterministic proofreader;
- proposal-only output, human confirmation required, no command execution;
- default-off route and no change to the legacy interpreter/provider gate;
- credential-free cell, one-use broker, regional Vertex allowlist and complete
  cleanup.

Fail closed on cross-practice selection, stale context, schema drift, source
label drift, UUID leakage, unexpected model-visible context, proofreader
rejection, endpoint or identity mismatch, open ledger or cleanup residue.
