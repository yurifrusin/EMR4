# Native Harness preset-mount sanitizer runner-bridge report

Date: 2026-08-22

Timestamp: 2026-08-22T06:34:51.627220+10:00 (Australia/Brisbane)

Result: **passed**

- Candidate source: `993a3b383aa79afba857bb53af29177bffacd566`
- Pure Node fixture processes: `1`
- Native Harness processes / DSH imports: `0 / 0`
- Closed fixture results: `8`
- Sanitizer admitted: `true`
- Runner bridge deterministically admitted: `true`
- Runner executed: `false`
- Worker/model/provider requests: `0 / 0 / 0`
- Stream content or environment values retained: `false / false`

The exact accepted runner and guard generators now have a deterministic source
descendant that places the admitted stage/code/null-detail sanitizer ahead of
the broader composition fallback at the exact mount boundary. This is source
and pure-fixture evidence only. It does not start DSH or the native Harness and
does not admit a worker, model/provider request, target or product authority.
