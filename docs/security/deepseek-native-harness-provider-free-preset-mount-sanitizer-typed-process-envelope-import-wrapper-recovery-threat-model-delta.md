# Threat-model delta: preset-mount sanitizer typed-process-envelope recovery

Date: 2026-08-22

Timestamp: 2026-08-22T05:21:00.2786709+10:00 (Australia/Brisbane)

Status: **frozen recovery before implementation**

## Scope delta

Two consumed local processes produced only outer safe terminals. The final
recovery adds a content-free process envelope and one repository-local dynamic
import inside a closed diagnostic wrapper.

## Controls

| Threat | Fail-closed control |
|---|---|
| Nonzero exit remains untraceable | Persist numeric exit, stream byte counts and SHA-256 before semantic admission; never persist content. |
| Dynamic import widens module authority | Admit exactly one literal relative specifier whose target path and bytes are contract-bound; reject every other import token. |
| Import/evaluation error leaks a path or stack | Wrapper catches without interpolation and emits one closed stage/code/null-detail terminal. |
| A malformed stream is mistaken for safe evidence | Python accepts only the exact success bytes or exact closed wrapper terminal; all other outputs stop. |
| Recovery becomes repeated probing | Attempt 003 is final; no fourth process is authorised by this plan. |
| Diagnostic success becomes native retry authority | Runner integration, repair selection, native Harness and worker/model/provider authority remain false. |

## Security acceptance

Accept only immutable attempts 001/002, one content-free attempt-003 envelope,
an exact closed output and unchanged no-Harness/no-provider/no-product gates.
