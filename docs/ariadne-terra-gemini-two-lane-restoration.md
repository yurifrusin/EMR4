# Ariadne Terra/Gemini Two-Lane Restoration

Date: 2026-07-24
Authority: Yuri's instruction to “go back to running both models”
Status: active before either lane was consumed

Yuri restored the original sequential comparative plan after adding
`GEMINI_API_KEY` to the system environment. The intervening Terra-only
amendment is superseded before any work-cell start, prompt transmission,
provider call, cost, or ledger consumption.

The active order is again:

1. Terra: at most one `gpt-5.6-terra` Responses API call;
2. exact Terra teardown and absence verification;
3. Gemini: at most one `gemini-3.5-flash` `generateContent` call.

Both lanes receive byte-identical provider-neutral authored-synthetic task and
schema projections. No retry, fallback, tool, cross-model input, vote, product
access, database, event feed, mailbox, command, PII, protected evidence, or
raw-content persistence is authorised.

Both machine-level credential presence gates must pass before Terra authority
is consumed. Values must not be printed, hashed, persisted, or placed in a
command line or container environment.
