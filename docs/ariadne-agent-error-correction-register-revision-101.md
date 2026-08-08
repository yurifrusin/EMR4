# Ariadne agent error and correction register revision 101

Date: 2026-08-08

Status: accepted register correction

Revision 101 adds AER-0123 and brings the register to 123 bounded incidents.

## AER-0123 — digest domain contradicted nullable checkpoint semantics

Failure evidence 007 proved that the remaining `23502` was not a missing table
column. The accepted inert artifact declared the digest domain globally
`NOT NULL`, yet its checkpoint invariant and registration function both require
a typed null digest at stream position zero.

Renderer `2.0.4` adds one fragment-sealed recovery that removes only the domain
presence constraint. Digest syntax remains enforced by the domain, mandatory
columns retain their own `NOT NULL`, and positive checkpoint positions still
require a digest. The revised artifact receives no runtime acceptance until a
fresh independent veto and both disposable PostgreSQL rehearsals pass.
