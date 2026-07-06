# Ariadne/Fable 100+ Sprint Strategy Map

| Item | Value |
|---|---|
| Status | Ariadne synthesis after Fable strategy review |
| Date | 2026-07-06 |
| Fable input | `orchestration/agent_inbox/codex/review-claude-fable-100-sprint-strategy-map.md` |
| Mode | Strategy only; no production runtime/provider/trove gate opened |

## Executive Decision

Fable's central critique is accepted: EMR4 has enough provider-free Bernie
Interpretation Harness guardrails for now. The next strategic arc should close
the "consumer gap" by building the runtime surfaces those guardrails were meant
to protect, while keeping historical diary, runtime-provider, memory/RAG, and
database-write boundaries closed until explicit reviewed gates open them.

The first durable arc is:

1. Clean orchestration signal just enough to trust worker output.
2. Stabilise the visible Bernie booking loop and its release gates.
3. Land the API spine decision and non-invasive schema artifacts.
4. Put Access AI behind one invocation/audit/cost boundary.
5. Route Bernie interpretation through that boundary in fake/default-disabled
   mode before any live provider opening.

This is a pivot from more harness-hardening to spine-building. It is not a
pivot into broad trove mining, autonomous Bernie writes, live providers, or
runtime memory.

## Map Shape

This map is a horizon, not a promise. Ariadne should revisit it at least every
10 sprints, at each band boundary, and whenever a gate fails or Yuri makes a
material priority/safety decision.

### Band 1: Booking Loop And API Spine

Goal: make one staff-confirmed Bernie booking flow real enough to review, and
document the API spine it should live on.

Candidate sprints:

1. Time-boxed inbox and Claude residue cleanup.
2. Sprint 98 Bernie booking-loop integrity.
3. API root-to-branch plan review.
4. API Spine ADR.
5. Non-invasive schema prototype.
6. API steward skill.
7. Margaret Thompson / Dr Shera release-gate hardening.
8. Route-intercepted UI release evidence for candidate choice and confirm errors.
9. Backend typed confirm-failure envelope hardening.
10. Band checkpoint: decide whether the booking loop is strong enough to host
    Access AI wiring.

### Band 2: Access AI Runtime Spine

Goal: make Access AI the only model path, fake-provider first.

Candidate sprints:

11. Access AI invocation service, fake provider only.
12. Invocation audit and cost envelope.
13. Enterprise auth seam and role mapping.
14. Bernie interpreter migration behind Access AI, default-disabled.
15. Scribe/extraction/letter migration behind Access AI with no visible change.
16. Dev-only non-PHI live-smoke gate proposal.
17. Live-provider gate review with Yuri approval required.
18. Budget, quota, and audit review for first live capability.
19. First narrow live capability if approved; otherwise strengthen fake harness.
20. Band checkpoint: re-plan after any provider boundary change.

### Band 3: Safe Appointment Mutation Workbench

Goal: all high-risk receptionist writes use proposal, confirmation, and audit.

Candidate sprints:

21. Drag/reschedule design contract.
22. Drag/reschedule backend proposal route.
23. Drag/reschedule diary UI proposal preview.
24. Cancel/no-show/DNA confirmation semantics.
25. Recurrence and reason-note policy.
26. Patient-search alert hardening.
27. Caller-context identity source.
28. Pending Bernie proposal object.
29. Diary pending-proposal highlight UI.
30. Confirm-to-appointment bridge checkpoint.

### Band 4: Bernie Internal Copilot

Goal: Bernie becomes useful to reception without becoming autonomous.

Candidate sprints:

31. Tool-schema audit-log foundation.
32. Staff message-taking model.
33. Slot-search proposal contract.
34. Non-autonomous Bernie command preview.
35. Promote one action grammar verb through H39 gates.
36. Promote second action grammar verb through H39 gates.
37. Waiting-area/check-in promotion review.
38. Link-patient promotion review.
39. Staff-facing recovery and clarification flows.
40. Band checkpoint: decide whether Bernie is internally pilotable.

### Band 5: Practice Operations And Davida

Goal: build daily admin surfaces and setup workflows that make EMR4 operable.

Candidate sprints:

41. Internal message model/API.
42. Diary message panel.
43. Billing review queue.
44. Operational notification semantics.
45. Davida setup-path CSV validation.
46. Davida dry-run/execute/verify/rollback maturity.
47. GCP pitfall helper metadata.
48. Keyless production posture review.
49. Practice onboarding manifest schema.
50. Band checkpoint: confirm admin surfaces are not obscuring core diary flow.

### Band 6: Evidence And Consultant Foundations

Goal: add cited clinical evidence support without autonomous clinical decisions.

Candidate sprints:

51. Multi-provider knowledge-base adapter.
52. Wiley/Cochrane licensing and privacy spike.
53. Clinical evidence citation envelope.
54. Consultant capability charter.
55. Patient-context frame minimisation.
56. Evidence audit model.
57. Clinician-facing evidence-response prototype.
58. Clinical safety review.
59. Knowledge-base provider decision.
60. Band checkpoint: decide whether clinical evidence can enter runtime.

### Band 7: Security And Deployment Maturity

Goal: make EMR4 safer to ship and easier to review.

Candidate sprints:

61. Preview deployment harness.
62. Browser smoke automation.
63. Broad pytest timeout segmentation.
64. GitHub security alert automation.
65. Threat model refresh.
66. PostgreSQL RLS tenant isolation plan.
67. RLS implementation slice.
68. Append-only audit_log foundation.
69. JWT/localStorage hardening plan.
70. Band checkpoint: security gate before external clients or broader AI.

### Band 8: Historical Diary Trove Utilisation

Goal: use the 58k-file trove only after a runtime consumer exists.

Candidate sprints:

71. H22 gate-review refresh.
72. Readiness/proposal guard rerun for trove surfaces.
73. Full-trove mining design with checkpointing and `-AllowLargeRun` rationale.
74. Validator-safe aggregate refresh plan.
75. One-time full-trove local mining run, if approved.
76. Neutral transition graph refresh.
77. Derived GraphRAG design over neutral state only.
78. De-identified synthetic fixture family expansion.
79. Runtime-consumer fit review.
80. Band checkpoint: decide whether any memory/RAG path is justified.

### Band 9: External Patient And Kiosk Clients

Goal: reuse the internal spine for public/patient-facing surfaces.

Candidate sprints:

81. Online booking portal API contract.
82. Online booking portal prototype.
83. SMS confirmation integration gate.
84. Patient PWA booking surface.
85. Patient PWA queue-position surface.
86. Kiosk identity-proofing design.
87. Rayleen check-in prototype.
88. Waiting-room display privacy review.
89. External-client security review.
90. Band checkpoint: decide whether external beta is safe.

### Band 10+: Clinical, Billing, Integrations, Launch

Goal: expand toward the master implementation plan once the core spine is real.

Candidate sprint areas:

91. Results relay/parser foundations.
92. Referral/document management.
93. VOIP caller-ID integration.
94. ePrescribing research and gateway spike.
95. Medicare/billing gateway plan.
96. ADHA/PRODA architecture plan.
97. Enhanced ambient scribe with patient context.
98. DDx decision-support prototype.
99. Launch-readiness documentation and accreditation.
100. Open-source preparation and contributor workflow.

Beyond sprint 100, continue with the same checkpoint rule rather than treating
this map as fixed.

## First Tactical Band

The next 5-10 sprints Ariadne should consider, in order:

1. Bounded inbox/Claude residue cleanup.
2. Sprint 98 Bernie booking-loop integrity.
3. API root-to-branch plan review.
4. API Spine ADR.
5. Schema prototype.
6. Access AI invocation service, fake provider only.
7. Invocation audit and cost envelope.
8. API steward skill.
9. Bernie interpreter migration behind Access AI, default-disabled.
10. Live-provider gate proposal only if the prior audit and fake-provider path
    are healthy.

## Standing Gates

These remain blocked unless Yuri explicitly approves a dedicated reviewed sprint:

- broad historical diary trove mining;
- H15/H-series runtime imports;
- provider calls outside Access AI gate review;
- memory/RAG/GraphRAG runtime wiring;
- database writes from model output;
- interpretation-harness runtime wiring outside promotion gates.

Before any proposal touches these surfaces, Ariadne must run and record:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

Expected current values remain:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`

Any drift pauses the sprint engine.

## Adaptation Checkpoints

Re-plan after every 10 sprints and immediately after:

- a Bernie happy-path release gate fails;
- Yuri approves or denies a live provider, H15, trove, security, or phase
  priority decision;
- a provider/runtime boundary opens;
- a P0/P1 security issue appears;
- the API/schema prototype disproves the ADR;
- historical diary readiness values drift;
- worker orchestration stops producing trustworthy poll/review signal.

## Ariadne Notes

The key trap is comfortable meta-work: cleanup, harness-hardening, and protocol
polish are useful only when they protect or unblock a real product surface.
The next arc should keep safety discipline, but it should spend that discipline
on getting the Bernie booking consumer and Access AI spine into shape.

Fable should be reserved for band-boundary architecture gates while access is
available: API Spine synthesis, first live-provider gate, and pre-trove review.
Routine implementation should use Claude, Antigravity/Gemini, DeepSeek Flash,
and Codex workers according to risk and file ownership.
