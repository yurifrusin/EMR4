# Ariadne agent-error register revision 34

Date: 2026-08-06

Status: protected-path enumeration attempt rejected and contained

## AER-0041 contained

A fresh native independent reviewer used a broad read-only filename discovery
command before source review. Its output included path names beneath protected
holdout directories. The reviewer immediately self-reported the breach. No
protected file content was opened or read, no protected hash or fixture
metadata was queried, no patient or product data was accessed, and no network,
cloud or candidate-runtime provider operation occurred.

Sol stopped the review and rejected the entire attempt. Exact Git readback
confirmed the candidate remained at
`12fbab157551954018e781810e4b100f05698dfb` with a tracked-clean review
worktree. The corrected review must use a genuinely fresh context and an exact
allowlist of named plan, design, threat, source, schema, fixture, evidence and
test paths. Repository-wide filename discovery is forbidden.

Revision 34 contains 41 bounded incidents: 29 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
No incident remains open. Counts remain workflow-improvement signals only and
do not establish model, provider, transport or role causation.
