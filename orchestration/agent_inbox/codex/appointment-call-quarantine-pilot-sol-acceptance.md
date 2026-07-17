# Appointment-Call Quarantine Pilot — Sol Acceptance

Date: 2026-07-17

Decision: `pass_stop_before_content_download`

The pilot correctly applied its ordered fail-closed contract. Public metadata
and the first public file-list page were inspected only to establish identity,
scope, and provenance. The required clinic/data-controller identity,
jurisdiction, collection basis, uploader authority, content-rights chain,
redaction method, and residual-identifier audit remain absent. The listed PDDL
label does not independently establish that the uploader owns every right
needed to dedicate the calls and transcript contents.

The correct accepted outcome is therefore to stop before content download.
Filesystem readback found no `local_data/appointment-call-quarantine/` root and
no matching appointment-call corpus archive or transcript. No corpus text was
opened or transmitted. No development, protected-evaluation, provider,
runtime, product, write, database, deployment, or release boundary moved.

The durable contract, evidence, and closeout are:

- `docs/bernie-appointment-call-quarantine-pilot-contract.md`;
- `docs/bernie-appointment-call-quarantine-pilot-evidence.json`; and
- `docs/bernie-appointment-call-quarantine-pilot-closeout.md`.

The source remains quarantined and inadmissible unless Yuri authorizes external
provenance coordination and a verifiable rights/privacy package resolves every
preliminary blocker.
