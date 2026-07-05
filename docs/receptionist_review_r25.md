# Sprint R25 Receptionist & Product Review

Sprint R25 adds a **default-disabled, no-write provider sampling scaffold** for
feeding static provider-style outputs through the R24 manifest safety gate. It
does **not** make live Gemini/Vertex calls, wire production prompts, mutate the
database, or change the Diary UI.

The scaffold is a safe stepping stone toward a later opt-in shadow/live-provider
pilot. That later pilot must be separately designed, reviewed, and approved.

## Product Boundary

- R25 evaluates static Gemini-style, Vertex-style, and adversarial sample frames.
- R25 proves the harness is disabled by default and returns no samples unless
  explicitly enabled in test code.
- R25 routes samples only through `app/services/ai/evals/manifest_eval.py`.
- R25 does not create background jobs, telemetry tables, production logs, admin
  panels, live provider clients, credentials, prompt dispatch, or frontend copy.
- R25 hardens the R24 gate so `allow_write=True` is treated as a write-authority
  claim while `allow_write=False` remains safe provider-style metadata.

## Receptionist-Facing Rule

There is no receptionist-facing UI in R25. Staff should not see a badge, warning,
or workflow change from this sprint.

If a future sprint introduces live shadow sampling, staff/admin copy must make
the boundary explicit:

- Badge: `AI Engine: Shadow Mode Active`
- Tooltip: `EMR4 is testing an AI model in background shadow mode. It can analyse
  instructions, but it cannot make diary changes. Staff confirmation and backend
  evidence remain required for every write.`
- Log prefix: `[SIMULATED - NO WRITE]`
- Allowed verbs: `staged`, `proposed`, `analysed`, `requires backend check`
- Forbidden verbs unless a staff-confirmed backend write really occurred:
  `booked`, `cancelled`, `updated`, `completed`, `written`

## Safety Acceptance Criteria

R25 is acceptable only if all of these remain true:

1. The harness is disabled by default.
2. Importing the harness does not import Gemini, Vertex, Google Cloud clients,
   routes, database models, SQLAlchemy, Alembic, or diary mutation services.
3. Disabled harness calls return empty tuples and perform no evaluation work.
4. Enabled harness calls evaluate static in-repo samples only.
5. Every sample evaluation goes through `evaluate_manifest_response()`.
6. Safe Gemini-style and Vertex-style samples pass.
7. Adversarial samples fail with typed R24 violation kinds.
8. `writes_authorized=True`, `allow_write=True`, and suspicious write-authority
   synonyms are blocked.
9. PHI-indicative keys remain blocked.
10. The scaffold cannot be mistaken for evidence that live-provider readiness is
    proven.

## Future Live-Provider Pilot Gates

A later live shadow-sampling sprint should remain blocked until it defines:

- Practice opt-in and privacy basis.
- Prompt redaction and PHI minimisation rules.
- Sampling rate, latency timeout, cost ceiling, and auto-disable policy.
- Telemetry schema with `run_mode="sampling"` and `writes_blocked=true`.
- Clear separation between active-path staff workflow and background sampling.
- A kill switch that cannot be overridden by model output.
- Evidence labels that distinguish static fixtures, fake-provider dry runs, and
  genuine live provider responses.

Readiness for write-authorised use remains **unproven** if any sampled output:

- claims write authority;
- emits PHI-bearing fields or copy;
- invents diary status or reason-code taxonomies;
- asserts live availability instead of requesting a backend check;
- bypasses required staff confirmation;
- returns malformed frames above the agreed threshold;
- exceeds latency or cost budgets; or
- fails prompt-injection refusal tests.

## References

- `app/services/ai/evals/manifest_eval.py`
- `app/services/ai/evals/provider_sampling_harness.py`
- `tests/test_provider_sampling_harness.py`
- `tests/test_sampling_harness_adversarial_review.py`
- `docs/receptionist_review_r24.md`
