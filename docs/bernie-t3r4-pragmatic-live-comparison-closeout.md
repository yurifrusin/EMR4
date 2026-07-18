# Bernie T3R4 Pragmatic Live Comparison Closeout

Date: 2026-07-18

Decision: `comparison_complete_with_hard_limit_stop`

## Outcome

The authorized synthetic-only comparison is complete. GPT/Codex and
Gemini/Antigravity were treated as practical subscription systems; DeepSeek was
a smaller auxiliary diversity lane and was excluded from production ranking.

The frozen maximum was 120 observations. Eighty-nine were consumed. Gemini
completed 48/48 and DeepSeek completed 24/24. GPT stopped at 17/48 because its
provider-reported input plus output usage reached 250,258 tokens, crossing the
frozen 250,000-token lane ceiling. The remaining 31 GPT observations were not
sent. No observation was retried.

No prompt, raw response, dialogue instruction, patient/practice information,
historical diary material, external corpus, or protected holdout content is in
the durable evidence. The ledger contains normalized decisions, hashes, safe
error codes, latency, and usage only.

## Primary systems

### GPT/Codex

The originally proposed `gpt-5.6-sol` alias was unavailable in the installed
Codex subscription catalog. Four observations were consumed as setup/model
errors before the lane was explicitly amended to the latest visible alias,
`gpt-5.5`. The first `gpt-5.5` observation also failed while the optional
provider-side output-schema flag was present; the same strict contract then
worked through the local schema parser without that flag.

Final GPT evidence:

- 17 consumed, 12 normalized successes, and five provider/setup errors;
- 12/12 successful observations safe and exact;
- correctness 72/72 with zero successful-response variance;
- five cases with two successful repeats and two cases with one success;
- 247,468 input plus 2,790 output tokens, total 250,258; and
- 31 unsent observations after the hard stop.

### Gemini/Antigravity

Final Gemini evidence:

- 48 consumed, 46 normalized successes, one provider error, and one parse
  error;
- all 46 successful observations safe;
- 43/46 successful observations exact;
- correctness 272/276 (98.55%);
- two entity failures and two date/time failures, concentrated in three status
  change observations;
- one variant case, the high-noise status-change ellipsis case; and
- 22 cases with two successful repeats and two cases with one success.

The only fully paired comparison contains five cases with two successful
repeats from each primary lane. GPT and Gemini are both 10/10 exact and 60/60
on that narrow slice. It is too small to rank the underlying models.

## DeepSeek auxiliary diversity

DeepSeek completed 24/24 scheduled observations: 23 normalized successes and
one provider error. All 23 successes were safe; 14 were exact, with correctness
127/138 (92.03%). Its eleven dimension failures were six entity, two intent,
one date/time, one clarification, and one tool-selection failure. Seven cases
varied across repeats.

This was useful evidence: the different model family surfaced substantially
more entity and repeat-stability weakness than GPT or Gemini. It validates the
reduced diversity role. It does not make DeepSeek eligible for deployment or
part of the production ranking. Claude Code reported an adapter estimate of
USD 1.071515; this is not an authoritative DeepSeek billing amount.

## Independent review

One fresh bundle-isolated Gemini review was attempted, then one mechanically
corrected fresh attempt. Both returned a proposed inspection plan instead of
the required bound decision. The correction loop is closed. The second
rejected output is preserved at
`orchestration/agent_inbox/antigravity/t3r4-pragmatic-live-independent-review-failed-decision.md`.
It is not acceptance evidence and reported no finding.

Sol therefore accepts the result as deterministic bounded experimental
evidence without an independent veto. This limitation blocks any use of T3R4
as a production-provider selection or promotion decision.

## Verification and bindings

- normalized observation count: 89;
- normalized observation file SHA-256:
  `6926da95c48b49d0f6c4b10269b5a3e2eac852840d785deead286b0efd25a0ea`;
- report file SHA-256:
  `e614d4ea92cad557f794ceb90430dc5da41b842f6d7923aebe1fc69720911b91`;
- internal report hash:
  `sha256:74490b72580db78fdd6ee6fcaeb07d8a05240c81a217e1da5b7fc4cbeeaaf650`;
- source result commit: `eb80c0c7`;
- focused and preservation gate: 105/105;
- Bandit: no new medium/high findings; and
- API-spine classification: developer-only synthetic Access AI evaluation.

The product T3 live gate, default provider, routes, runtime Access AI wiring,
database/audit writes, appointments, confirmation, deployment, release, and
write authority remain blocked.

## Recommendation

Gemini is the most useful current production-relevant lead because it completed
the broad sample with high accuracy and safety. GPT remains promising but the
subscription-agent transport overhead prevented a comparable broad result.
DeepSeek should remain a synthetic-only adversarial/diversity resource.

The next sensible track is a no-call Australian-region Gemini/Vertex
feasibility and entitlement design, followed by a separately approved
tool-free Vertex evaluation if its regional data-handling, audit, budget, and
exact-model controls pass. T3R4 itself does not authorize that work or select a
production provider.
