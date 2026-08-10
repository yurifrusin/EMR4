# Context Fabric durability behavior failure 044 — telemetry correction

Date: 2026-08-08

This correction is diagnostic containment only. It does not repair or alter the
database behavior responsible for SQLSTATE `23502`.

The behavior harness now projects a not-null coordinate for an unexpected
scenario rejection only when both the relation and column are present in the
closed admission-table allowlist. It otherwise emits only
`unlisted_relation`, `unlisted_column`, `missing` or `ambiguous`. Raw PostgreSQL
messages never enter durable evidence.

Fresh tests prove the allowlisted path, the hostile unlisted-column path and
the existing evidence schema. A fresh exact-head independent veto is required
before one new owned disposable attempt. That new attempt may identify the
responsible column; it grants no authority to guess at or change the accepted
database body beforehand.
