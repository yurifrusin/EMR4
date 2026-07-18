# Bernie T3R3 Provider Retention Review

Date: 2026-07-18

Decision: `policy_review_complete_account_acceptance_blocked`

## Scope

This is a source-backed privacy and retention review for the proposed
synthetic-only GPT, Gemini, and DeepSeek evaluation lanes. It does not approve a
provider call. The exact 24 prompts contain only committed synthetic Silver v2
dialogue; patient, practice, historical diary, external-corpus, and protected
holdout material remains prohibited.

## OpenAI Codex subscription lane

OpenAI states that content from individual services such as ChatGPT and Codex
may be used to improve models unless the user opts out. Codex has additional
controls for full-environment training, and ChatGPT training controls apply to
Codex content. Deleting a retained Codex chat schedules deletion within 30 days,
subject to legal, security, or previously de-identified-data exceptions.

Sources:

- https://help.openai.com/en/articles/5722486-api-data-usage-policies
- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- https://help.openai.com/en/articles/20001333-how-to-archive-and-delete-codex-chats-in-the-chatgpt-app

The proposed `codex exec --ephemeral` control prevents local session-file
persistence. It does not prove the account-level training setting, provider
retention, or deletion state. Those account controls have not been inspected or
accepted for this run, so the lane remains blocked.

## Google Gemini subscription lane

Google's Gemini Apps guidance says that when Keep Activity is off, conversations
may still be retained with the account for up to 72 hours to provide and protect
the service. With activity enabled, the default auto-delete period is 18 months;
reviewed feedback and associated content can be retained for up to three years.

Sources:

- https://support.google.com/gemini/answer/13278892
- https://support.google.com/gemini/answer/13594961

No accessible official source found in this review establishes that
Antigravity's new-project/print mode inherits exactly those Gemini Apps controls.
The installed `agy` CLI also exposes no no-session-persistence flag. The
Antigravity-specific retention mapping therefore remains unresolved and the lane
remains blocked.

## DeepSeek API lane

DeepSeek's official API documentation confirms `deepseek-v4-flash` as an API
model and records token-based billing. Its privacy policy says collected
information is generally stored on servers in mainland China and retained for
the minimum necessary period, while cited cybersecurity requirements include
security/network logs retained for at least six months. DeepSeek's context-cache
documentation says request-derived disk-cache entries are enabled by default and
are usually cleared within hours to days.

Sources:

- https://api-docs.deepseek.com/
- https://api-docs.deepseek.com/quick_start/pricing
- https://api-docs.deepseek.com/guides/kv_cache
- https://platform.deepseek.com/downloads/DeepSeek%20Privacy%20Policy.pdf

Claude Code's `--no-session-persistence` disables local Claude session storage;
it does not override DeepSeek's server-side policy or caching. Those terms may be
acceptable for deliberately synthetic, non-PHI prompts, but that is a material
data-residency/retention acceptance for Yuri. It has not been granted, so the
lane remains blocked.

## Conclusion

None of the three lanes is execution-ready. DeepSeek has the strongest local
tool-free adapter contract but still needs explicit acceptance of its provider
retention/data-residency posture and exact observed model identity. GPT still
needs account-control verification and a tool-free transport. Gemini additionally
needs Antigravity-specific retention evidence, structured-output enforcement,
no-session-persistence, tool-disable, and no-fallback controls.

No exact marginal-dollar budget is required. The packet instead caps each lane
at 48 samples and 250,000 provider-reported tokens when available, with 144
samples and 750,000 tokens across the entire run, one attempt per sample, no
automatic retries, and fixed character/time ceilings.
