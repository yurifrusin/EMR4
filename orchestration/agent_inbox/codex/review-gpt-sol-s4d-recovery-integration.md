# GPT Sol S4d Recovery Integration Review

Date: 2026-07-11
Risk class: low
Settings fingerprint: `sha256:14b8ae3439d6ce03bb1c4405dd42694acc62ca1fd4278f0812c480b57e7e775c`

## Provenance

- D2's corrected authority document and worker artifact were accepted after
  content review and integrated unchanged.
- D1's adapter-settings test was imported as untrusted candidate source. Its
  contradictory first closeout was rejected and two closeout retries timed out.
  GPT Sol owns acceptance and verification of the source; no replacement D1
  worker attestation is claimed.
- D3's mailbox-settings test was imported as untrusted candidate source. Its
  false test-run claim and later ownership breach were rejected. The unowned
  `tests/test_ariadne_deepcode_pty.py` edit was not integrated. GPT Sol replaced
  the generated 623-line candidate with a focused 105-line contract suite and
  owns that amendment.
- The recovery verifier produced its artifact after the adapter deadline, so
  its transport contract failed and it was not used as authority.

## Orchestrator Identity Correction

The active protected orchestrator is GPT Sol, not GPT Terra. The stable pool
resource is now `openai-primary-orchestrator`, with current default model
`gpt-sol`. Historical Terra-labelled artifacts remain unchanged as historical
evidence. The model/resource correction was explicitly supplied by Yuri.
S4d's actual Conductor calls used Claude Opus at medium reasoning. Future
allocation now defaults to Fable, falls back to Opus only for usage/availability
problems, then to a distinct spawned GPT Sol conductor subagent.

## Verification

GPT Sol ran 70 focused tests covering D1, D3, PTY lifecycle, mailbox, allocation
schemas/replay/CLI, orchestrator preflight, and complete-settings fingerprinting.
All passed. The allocator selected Claude Fable conductor, DeepSeek Flash
verifier, and `openai-primary-orchestrator`. No EMR4 runtime code changed.

Antigravity/Gemini Flash 3.5 did not return a decision artifact and was stood
down. The bounded Ariadne-local fallback review passed with reduced independence
recorded at
`orchestration/agent_inbox/codex/review-ariadne-local-s4d-veto-fallback.md`.
