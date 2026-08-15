# Sol acceptance — delete-confirm physical schema-and-transaction scaffold

Date: 2026-08-16

Timestamp: 2026-08-16T00:24:19+10:00 (Australia/Brisbane)

Decision: `accepted`

Result: `raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold_pass`

Reviewed candidate: `bdfea42a47c0ebcbfc9d4ac6ae5685a380079ca7`

Integrated source: `843769b415597f4545663d78044eaaad303c7692`

Reasoning level: material authority / migration / transaction implementation / Extra High

## Basis

I accept the scaffold because it lowers the exact approved cancellation
authority, private receipt, attributable audit and ordered transaction design
without opening a database or route. PostgreSQL owns the positive authority
generation; grants are normalized and default deny; canonical response bytes
and session binding are exact; replay is current-authority and integrity
gated; and the unmounted seam cannot commit an incomplete write set.

The deterministic evidence passes 20 source bindings, 117/117 hostile
mutations, 57 focused/conformance tests, 36 API Spine tests and the canonical
196-test fast profile. The first verifier attempt is rejected and preserved as
AER-0341 because one manifest command crossed checkout roots with relative
paths. Its corrected exact-candidate successor ran six zero-exit commands and
returned one clean Gemini 3.7 Flash/high `pass`. I reconciled both receipts,
all command exits, candidate HEAD and clean postcondition independently.

## Allocation and recovery

DeepSeek V4 Flash/high supplied bounded source and test work but did not accept
its own result. Native auditors supplied read-only omission checks. Sol owned
the recovery lease, semantic correction, integration and acceptance. Gemini
3.7 Flash/high supplied veto evidence only. No fallback model was used.

## Acceptance boundary

Runtime authority remains false. This acceptance grants no migration/DDL/SQL
or database execution, real lock or transaction proof, capability provisioning,
route/schema/OpenAPI change, product/patient/clinical data, product provider,
ADC, credentials/IAM, network, watcher/event, product command, deployment,
production, release, Pages or protected-ref movement.

The next safe candidate is the provider-free disposable PostgreSQL
parse/catalogue rehearsal, but Yuri explicitly requested a pause after this
closeout. It is not opened by this acceptance.
