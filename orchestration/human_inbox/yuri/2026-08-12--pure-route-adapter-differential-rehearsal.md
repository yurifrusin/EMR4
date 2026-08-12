# Pure route adapters: same referee, no hidden shortcuts

Date: 2026-08-12

## Lay summary

We have now proved that the newer confirmation routes and a properly equipped
future version of each old write route can hand the same meaning to one backend
referee. The routes may arrive through different doors, but the appointment,
authority context, freshness evidence, confirmation and retry identity are not
allowed to change in translation. The door itself remains recorded honestly.

The current old routes still do not qualify. Each is missing three distinct
things: evidence of what backend state the user acted on, separate confirmation
evidence, and a durable command retry identity. The adapter rejects all three
gaps together and produces no partial command. This is the practical version
of the principle we discussed: stale or incomplete context may prompt an
attempt, but it cannot award the ribbon.

Nothing in the product has been rewired. The useful gain is a small, testable
translation boundary that can later be observed safely before any route is
migrated.

## Technical summary

- Accepted result:
  `raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal_pass`.
- Exact source: `beb4e65cddf72437948d72e08dd18c2ea4f0c609`.
- Covered 9 adapters, 4 synthetic intents and 13 scenarios.
- Mapped 9 complete candidates; rejected all 4 current raw profiles with the
  exact three control-gap codes and no partial candidate.
- Proved 4 operation-family differentials equal across 17 semantic fields;
  only `route_adapter_id` differs as audit provenance.
- Preserved 4 route families, 8 outcomes, authority-first precedence and the
  canonical lock order.
- 45 hostile mutations, 119 focused tests and the canonical 191-test profile
  pass; lifecycle/Compass checks pass at Continuity 248 / Compass 230.
- No application route, database/source, event, watcher, provider, patient or
  product data, command, deployment, Pages or protected ref was opened.
- Next: provider-free unmounted default-off non-enforcing shadow-comparison
  architecture. Your attention is not required.
