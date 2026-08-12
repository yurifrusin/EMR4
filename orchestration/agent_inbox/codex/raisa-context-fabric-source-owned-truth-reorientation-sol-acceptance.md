# Sol acceptance — Context Fabric source-owned-truth reorientation

Date: 2026-08-12

Decision: `accepted`

Accepted result:
`raisa_context_fabric_source_owned_truth_conditional_command_reorientation_pass`

I accept reviewed source `037eed060d4519f2f3d6721135143ecb6f70e358`.
The contract places correctness at the authoritative command service, keeps
Context Frames read-only and expiring, and limits events to acceleration hints.
It correctly distinguishes freshness, confirmation, idempotency and audit and
recognizes that appointment creation needs schedule-domain serialization
rather than a nonexistent target-row lock.

The selected watcher topology is one logical consumer per database event
partition. One physical watcher is sufficient initially; any future replicas
are active/standby under external fencing, with idempotent duplicate delivery.
CF-D1 remains evidence and CF-D2 can return only through a new observability-
first plan for the deferred Durable Event and Cue Delivery extension.

All 28 hostile mutations, 53 focused tests and 191 canonical fast-profile tests
pass. One schema-constrained Sydney Vertex `gemini-2.5-flash` review of the
exact candidate reported no P0-P2 finding. It used no tools or fallback and
received no patient/product data. The preceding expired-ADC attempt made zero
provider calls and remains preserved.

This acceptance opens no route, database, watcher, source, persistence,
patient/product data, executable, command, deployment, release, Pages or
protected-ref authority. The provider-free unmounted conditional-command
admission rehearsal is the next safe descendant under standing continuation
authority.
