# Practitioner Directory Read-Shape Design

Date: 2026-07-08

Sprint: 214

## Purpose

This design packet follows
`docs/api-spine/external-router-read-model-gap-inventory.md` for the
`Query.practice.practitioners` gap.

It defines a future read-shape contract only. It does not add a REST route,
GraphQL resolver, GraphQL mutation, Pydantic schema, database query, provider
call, runtime FGA client, Access AI invocation, or write authority.

## Target Read Surface

| GraphQL read surface | Current gap posture | Future REST read shape | Runtime status |
|---|---|---|---|
| `Query.practice.practitioners(activeOnly: Boolean = true)` | `route_gap` | `GET /api/v1/practice/practitioners` or equivalent practice-scoped GET read | `not_implemented` |

## Display-Safe Field Mapping

| GraphQL field | Current source | Mapping posture | Notes |
|---|---|---|---|
| `Practitioner.id` | `app/models/tenancy.py::Practitioner.id` | `direct` | Must remain scoped to the authenticated user's practice before exposure. |
| `Practitioner.displayName` | `Practitioner.first_name`; `Practitioner.last_name` | `derive` | Derive by joining non-empty first and last name parts; do not expose provider, prescriber, AHPRA, HPI-I, email, phone, or address fields through this shape. |
| `Practitioner.roleLabel` | `Practitioner.specialty` | `optional_map` | Current model has `specialty`, while SDL reserves `roleLabel`; future implementation must decide whether specialty is the role label or whether a separate staff role vocabulary is needed. |
| `Practitioner.active` | `Practitioner.is_active` | `rename` | Default future read should apply `activeOnly=true`; explicit inactive review is a separate authorization decision. |
| `Practitioner.defaultLocation` | `Practitioner.default_location_id`; `PracticeLocation` | `linked_read_gap` | Future read must join only same-practice active locations and project the existing display-safe `PracticeLocation` shape. |

## Current Supporting Evidence

- `Practice.practitioners` relationship exists in `app/models/tenancy.py`.
- `User.practitioner_id` and `User.practitioner` exist, but viewer identity does
  not become a full practitioner directory.
- `GET /api/v1/diary/template` can resolve `practitioner_id` from
  `practitioner_ahpra` for diary template columns.
- `GET /api/v1/diary/roster` returns `practitioner_id`,
  `practitioner_ahpra`, and a roster label for room/date context.
- The above diary reads are context reads, not a practitioner-directory read
  model and not evidence that `Query.practice.practitioners` is implemented.

## Known Shape Gaps

- No current dedicated practitioner directory GET route exists.
- No current `PractitionerOut` or equivalent display-safe response schema exists
  in `app/schemas/diary.py`.
- `Practitioner.displayName` is derived, not stored.
- `Practitioner.roleLabel` is not a direct model field; current `specialty`
  may not be the same concept as a receptionist-facing role label.
- `defaultLocation` needs a safe linked object projection; `default_location_id`
  alone is not the GraphQL `PracticeLocation` object.
- Provider number, prescriber number, AHPRA number, HPI-I, user email, phone,
  address, and schedule/availability details are deliberately outside the
  future practitioner directory read shape.

## Future Route Requirements

Before any implementation sprint may add the practitioner directory read:

- the route must be a practice-scoped GET read under an explicit reviewed path;
- the route must depend on the authenticated user and filter by `current_user.practice_id`;
- the default response must filter `Practitioner.is_active == True` unless a
  reviewed inactive-inclusion parameter and role policy is added;
- the response shape must include only `id`, derived `displayName`, optional `roleLabel`, `active`, and optional display-safe `defaultLocation`;
- `defaultLocation` must be same-practice and display-safe, not a raw location
  model dump;
- ordering must be deterministic, preferably by display name or last/first name;
- pagination or bounded result-size policy must be documented before production
  rollout;
- the route must not expose provider identifiers, prescriber identifiers,
  AHPRA, HPI-I, user credentials, contact details, schedule internals, or
  appointment data;
- the route must not be used as provider, RAG, GraphRAG, Access AI, or external patient-client authority.

## Closed Gates

This design does not authorize:

- adding a REST practitioner directory route;
- adding GraphQL resolvers or GraphQL mutations;
- adding Pydantic runtime schemas;
- provider calls or live provider gates;
- provider dry-run wiring;
- runtime FGA clients;
- external patient clients;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- Access AI invocation wiring;
- practitioner create/update/onboarding commands;
- appointment, roster, schedule, or diary write authority;
- model-to-database writes outside REST command handlers;
- raw compatibility deprecation mode changes.

## Boundary

This is a static read-shape design packet. It does not prove runtime GraphQL
resolver implementation, REST route authorization, database query correctness,
location join correctness, pagination, inactive-practitioner policy,
performance, deployment readiness, or patient-facing client readiness.

`tests/test_api_spine_practitioner_directory_read_shape_design.py` validates
this packet by parsing only this markdown file, the GraphQL SDL, selected
model/router/schema source files, and the external read-model gap inventory.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_practitioner_directory_read_shape_design.py -q
```
