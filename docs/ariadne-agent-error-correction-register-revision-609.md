# Ariadne agent error and correction register — revision 609

Date: 2026-08-22

Status: **three corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 609
incident_count: 910
new_incident_ids: AER-0908,AER-0909,AER-0910
open_incident_count: 0
-->

## AER-0908

The first source-reconciliation contract manually expanded the planning
commit instead of copying the full object ID from the machine resolver. The
deterministic contract check rejected the invented 40-character value before
commit or evidence generation. The accepted contract uses the exact
machine-resolved object. Future contract construction must obtain Git object
identities through the repository resolver rather than caller-authored text.

## AER-0909

The first direct controller invocation could import its own module under
pytest but could not import the repository `scripts` package when executed by
path. The direct check failed before evidence generation. The controller now
binds the repository root before package imports, and the direct CLI path is
covered by verification.

## AER-0910

Two first-draft plan assertions normalized line wrapping by joining tokens in
a way that also removed source-owned compound hyphens. The focused suite
rejected only those assertions before evidence generation. The accepted tests
normalize Markdown whitespace while preserving compound terms.

## Control reading

All three incidents were caught by deterministic local gates before evidence
acceptance and without starting Node, the native Harness, a worker, a model or
a provider. The material lesson is AER-0908: a 40-character field is not made
reliable merely by validation after authorship. The next clockwork-connected
correction must make the repository resolver the only producer of that
binding.
