# Ariadne / DeepSeek shadow clockwork gear architecture — lay and technical closeout

Date: 2026-08-19

Timestamp: 2026-08-19T06:08:13.6850292+10:00 (Australia/Brisbane)

Status: accepted architecture; continuing to provider-free shadow rehearsal

Exact reviewed source: `f6cbd33fd3322754e06ac6dafa1503f5200e0803`

## Lay summary

We now have a precise design for the clockwork you proposed. Ariadne is the
clock. When DeepSeek is selected, Ariadne hands its broker one uniquely shaped,
tamper-evident gear tooth. The broker can turn that tooth once and must return a
complete result before Ariadne can advance again. Neither side relies on wall-
clock timing or a remembered short Git identifier.

The Harness presets remain useful: read-only review, bounded worker and
provider-free profiles can package the right capabilities for recurring jobs.
But a preset cannot grant permission. The exact preset, package, profile and
tool set must all match the authority already recorded by Ariadne.

The architecture passed an independent Gemini review. It did not call DeepSeek
or replace anything live.

## Technical summary

- ten predecessor artifacts are bound by canonical-LF SHA-256;
- zero binding fields are caller-authored and fifteen field groups are engine-
  owned;
- a single-writer lease moves `Ariadne -> broker -> Ariadne` through exact
  WorkOrder, terminal-result and acknowledgement digests;
- unknown commit releases no success, permits no automatic retry and requires
  exact-identity readback;
- 48 scenarios, 256 hostile contract mutations and ten hostile causal traces
  pass with zero escapes;
- only read-only and private shadow-generation effects are admitted; and
- the exact Gemini 3.7 Flash/high review passed all ten read-only commands at
  unchanged clean source `f6cbd33fd3322754e06ac6dafa1503f5200e0803`.

## Efficacy and issues

We have deliberately not declared victory on efficiency yet. The old manual
workflow still caused fourteen failure-induced verification reruns through the
final post-compaction publication checkpoint. The failures included a
historical fixture reading the live latch, duplicated register literals,
uninventoried path operands and one receipt with an incomplete adapter
inventory and one latch test that retained its planning source after valid
completion. All were caught before publication; no escape or partial
publication occurred.

That is useful baseline evidence. The next rehearsal must show at least a 50%
reduction in failure-induced reruns, zero caller binding fields, no new mutable-
current fixture, no coverage loss and zero escape. It must also report shared-
engine growth and clean-run overhead honestly.

## Deliberately still closed

No live clock adoption, current-control retirement, DeepSeek/HMR call, ordinary
practice, product/API/database/client change, product or clinical data,
production runtime, deployment, release, Pages or protected-ref movement.
Yuri's prepaid provider balance remains the financial ceiling; no duplicate
Harness budget feature is required.

## Next tranche

Build the clock request/lease/result/acknowledgement engine only in a private
provider-free shadow and run it against frozen representative workflow
fixtures. If its measured bureaucracy is not materially lower, it will not be
proposed for live adoption.

The continuing non-PHI Pushover closeout request is
`0d55e84a-8c60-40b1-8260-5a1d467b205e`.
