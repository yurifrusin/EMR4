# Bernie T3R2 Three-Lane Amendment

Date: 2026-07-18

Decision: `deepseek_lane_added_calls_remain_blocked`

Yuri explicitly added DeepSeek to the proposed synthetic comparison before any
provider call. The frozen 24-case population and selection hash are unchanged.
The candidate set is now:

- OpenAI `gpt-5.6-sol` through subscription-backed Codex;
- Google `Gemini 3.5 Flash (Medium)` through subscription-backed Antigravity;
  and
- DeepSeek `deepseek-v4-flash` at high reasoning through Claude Code `--bare`,
  using the existing metered API transport.

Two observations per model and case raise the hard ceiling from 96 to 144
scheduled samples. The provider-reported token ceiling rises from 500,000 to
750,000 and the wall-clock ceiling from 120 to 180 minutes. One attempt per
sample, no automatic retry, prompt/response character limits, provider errors
consuming a scheduled sample, and every privacy, evidence, runtime, tool, and
write boundary are unchanged.

The original T3R2 closeout and acceptance remain the historical record of the
initial two-lane packet. This amendment and the current JSON packet supersede
their lane and usage counts only. No model prompt was sent by this amendment.
