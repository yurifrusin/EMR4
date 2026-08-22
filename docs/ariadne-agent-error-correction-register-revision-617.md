# Ariadne agent error and correction register — revision 617

Date: 2026-08-22

Timestamp: 2026-08-22T15:07:52.9378905+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 617
incident_count: 957
new_incident_ids: AER-0957
open_incident_count: 0
-->

This revision adds one bounded preexecution observation from the typed native-
Harness useful-worker recovery. It caused no attempt preparation, lease
consumption, worker, provider, product or protected-ref effect and is corrected.

## AER-0957 — contract generated before bound schema bytes were final

The first published control candidate generated its deterministic contract and
then removed trailing blank lines from copied schemas. That harmless byte
normalization made the contract's candidate-schema digest stale. The shell-free
preexecution validation runner rejected both exact contract equality and the
provider-free controller check before any occupied authority was consumed.

The corrected descendant regenerates the contract from the final normalized
bytes. Existing exact-equality tests and the provider-free check are the control:
they must pass before the attempt root can be prepared or its lease consumed.

## Register reading

This is a useful clockwork catch rather than a Harness result. It demonstrates
that a stale binding now stops at the deterministic gate instead of producing a
costly or ambiguous occupied rerun. It does not alter the one-request authority
or support any claim about DeepSeek quality.
