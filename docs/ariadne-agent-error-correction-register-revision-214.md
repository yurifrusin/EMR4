# Ariadne agent error and correction register — revision 214

Date: 2026-08-11

Revision 214 adds AER-0249 and brings the register to 249 bounded incidents.

## AER-0249 — unavailable PowerShell/.NET hash-format API

The first read-only untracked-baseline probe collected the exact 494 preserved
paths but attempted `Convert.ToHexString`, which is unavailable in this Windows
PowerShell/.NET runtime. The hash field was therefore null and no evidence was
accepted from that probe. It changed no file, ref, process or worker state.

The corrected fresh probe formats the same SHA-256 bytes through
`System.BitConverter.ToString`, removes hyphens and lowercases the result. It
returned the historical
`f9381b3e31389b512ed04a2eb2c9eec4c5a0a77bf6a673613a746bbc5dd99162`
digest over all 494 original paths, including five `docs/branding/` paths. The
runtime-compatible BitConverter form is frozen for remaining AES-C2 checks.
