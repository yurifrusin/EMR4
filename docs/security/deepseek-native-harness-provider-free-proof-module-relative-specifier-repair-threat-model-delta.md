# Threat-model delta — native Harness proof-module relative-specifier repair

Date: 2026-08-21
Timestamp: 2026-08-21T13:41:11.0607422+10:00 (Australia/Brisbane)

## Scope

This delta covers only the provider-free replacement of two generated proof
module names with accepted profile-relative specifiers. It opens no Harness or
provider execution and changes no product surface.

## Threats and controls

- **Path widening or traversal:** only the two exact
  `../../../installation/proof/*.mjs` literals are admitted; variants,
  duplicates and additional module rows fail closed.
- **Unintended profile drift:** deterministic comparison permits the two output
  rows and dead `proof` local removal only; all other bounded-profile anchors
  remain required.
- **False readiness claim:** evidence labels the result static/provider-free
  and records zero execution counters. Native boot and worker readiness remain
  separate gates.
- **Historical evidence mutation:** attempts 001-004 and accepted predecessor
  evidence are read-only digest bindings.
- **Provider or credential escape:** the repair runner has no subprocess,
  socket, HTTP, Node, Harness, broker, model or provider entry point.
- **Product-authority escape:** no application, API, route, database, feature
  flag, client or patient/clinical surface is in the owned file set.

## Residual risk

A correctly formed relative specifier may still fail during a future rc7 boot
for a different reason. This tranche proves only the generated profile repair;
a native boot proof requires its own frozen authority and evidence.
