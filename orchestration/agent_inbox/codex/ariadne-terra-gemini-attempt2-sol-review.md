# Ariadne Terra/Gemini Comparative Rehearsal — Attempt 002 Sol Review

Date: 2026-07-24
Reviewer: GPT Sol High
Decision: `revision_required`
Result:
`ariadne_terra_gemini_comparative_rehearsal_attempt2_revision_required`

## Finding

I reject generated-draft, proofreader and comparative-model claims because
neither provider presented a draft. Terra returned HTTP 500 on its one request;
Gemini returned HTTP 400 on its independent one request. Both fresh process
authorities are consumed and no retry is authorised.

## Evidence accepted

I accept the narrower transport and isolation evidence:

- the five-source receipt, credentials, focused tests, corrected five-hash
  regression and real-isolation preflight passed;
- both lanes used the same sealed prompt and schemas;
- the attempt 001 CRLF defect did not recur;
- each broker made exactly one call to the frozen host, path and model;
- Terra cleaned up completely before Gemini began;
- the provider secrets remained broker-only;
- neither lane recorded raw content or reached schema/proofreader release; and
- final comparison container, network and image-tag residue is zero.

Focused verification passes 20/20. The broader serial population passes
261/261 with only the documented immutable DeepSeek runtime-source-hash node
deselected after separate reproduction. Graph/Compass validation, deterministic
Compass rendering, Ruff, compilation, Node syntax, exact reviewed Bandit, JSON
and whitespace checks pass.

## Diagnostic finding

The evidence safely proves HTTP status, byte count and response hash, but it
does not retain a provider error type/code/parameter or request identifier.
Accordingly:

- Terra's HTTP 500 is an unresolved provider non-success, not a model-quality
  result or a proven request-contract defect.
- Gemini's HTTP 400 is an unresolved request rejection. Current official
  references support the selected model and endpoint capabilities, while also
  permitting schema-complexity rejection; the exact cause is not proved.

No response-body reconstruction, provider replay or new call is permitted.

## Authority finding

Both attempt 002 ledgers are consumed. The comparative branch is paused behind
a fresh decision. A future diagnostic should first improve allowlisted
non-content error metadata and provider-contract validation without a provider
call. A later occupied attempt would require separate fresh authority.

PII, protected/historical evidence, product APIs, databases, events, mailboxes,
human actions, commands, production, deployment, release and autonomous action
remain closed.
