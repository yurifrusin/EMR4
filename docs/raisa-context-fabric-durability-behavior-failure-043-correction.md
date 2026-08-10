# Context Fabric durability behavior failure 043 — correction descendant

Date: 2026-08-08

This provider-free descendant corrects the behavior expectation exposed by
immutable attempt 043 without changing the accepted database body or SQL.

`BTR-E06` still submits the same valid generation and missing outbox position,
with the same readbacks, forbidden effects, principal, transaction shape,
population and order. Its expected failure now matches the accepted exact-row
semantics: `F_CARDINALITY` / `CF004`. `F_ADMISSION_SOURCE` / `CF201` retains its
distinct meaning of a packet-to-present-source membership-digest mismatch.

The parent receipt-lock contract and its scenario seal remain immutable history:

- parent canonical contract SHA-256:
  `ee44dbf39c2458fdabc94768e3c3e8cdcc0372c10ae7f0a35709b55301c5d596`;
- parent scenario-set SHA-256:
  `d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`.

The corrected current seals are:

- canonical contract SHA-256:
  `897e07895116eecedaf8a2506ad10f9f5e5207b7e78e68ab79afb09347018a57`;
- scenario-set SHA-256:
  `e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb`.

Future SQLSTATE mismatch evidence now carries only bounded typed fields:
scenario ID, expected SQLSTATE, observed SQLSTATE set, optional single observed
SQLSTATE and process exit. It still persists no raw PostgreSQL message or
caller-selected value.

The body contract and schema, builder, validator, inert SQL, render manifest,
parse/catalogue evidence, roles, grants and authority ceilings remain
byte-identical. A new database characterization is closed until this exact
candidate passes deterministic validation and a fresh independent veto.
