# Governance clockwork ergonomics and efficacy review — lay and technical summary

Date: 2026-08-23

Timestamp: 2026-08-23T15:59:03.2163529+10:00 (Australia/Brisbane)

## Lay summary

The clockwork is safely doing its job, but its controls make the orchestrator
fill in far too much information the repository already knows. The last two
closeout forms run to 1,173 lines, and the latest closeout took about as long as
the product work it recorded.

The DeepSeek-Harness period was still useful: it taught us that only three
cross-harness readings are needed—prepared, terminal, and accepted or
recovered—and it made failures attributable. It did not prove reliable useful
completion, so the specific native profile remains paused.

The recommended first repair is to make the existing tick inspect the whole
prospective record before publication and generate its own transaction counts.
That would have removed all three latest rollback sequences without weakening
a safety gate or adding another form.

## Technical summary

The exact review covers 99 live-clockwork nodes, the accepted 70-node native
synthesis, four efficacy readings with 31 disclosed procedural lapses, and two
closeout intents containing 73,459 bytes and 785 scalar leaves. Four sampled
lapses required byte-exact rollback; none caused a provider or product rerun.

The next tranche changes only the existing governance tick and focused tests.
It opens no Harness/provider, check-in operational, product, runtime,
deployment, Pages or protected-ref surface. Yuri's attention is not required.
