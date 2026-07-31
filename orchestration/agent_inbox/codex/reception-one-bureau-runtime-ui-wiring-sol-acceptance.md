# Sol acceptance: Reception One Bureau runtime UI wiring

Decision: **accept**

The implementation satisfies the frozen provider-free plan:

- the control is absent outside the explicit authored-synthetic development
  gate;
- deterministic planning remains the visible and transmitted default;
- the browser can select only `deterministic` or `isolated_vertex`;
- provider identity, credentials, project, region, endpoint, cost and fallback
  remain backend-owned;
- only proofreader-admitted typed proposal data and bounded non-secret
  provenance reach the projection;
- failed or gate-closed work clears provenance and does not fall back;
- the isolated backend gate rejects before context and provider use;
- no confirmation, write, credential read or provider call occurred; and
- the real browser/FastAPI/PostgreSQL evidence records unchanged database
  truth and complete owned cleanup.

The combined regression matrix passed 136 tests. JavaScript syntax, Python
compilation, JSON/YAML validation, Compass validation/rendering, diff and
residue checks are required to remain green at final binding.

Acceptance is limited to a provider-free, development-only,
authored-synthetic UI result. It is not authority for another occupied call,
real or patient data, confirmation, mutation, participant use, Word, voice,
production, deployment or release.
