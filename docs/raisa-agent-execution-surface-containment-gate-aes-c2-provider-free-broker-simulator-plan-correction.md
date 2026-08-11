# AES-C2 broker-simulator plan correction

Date: 2026-08-11

Status: corrected before worker dispatch

The mandatory pre-dispatch plan challenge rejected one infeasible digest rule.
The accepted C1 manifest and current-generation fixture deliberately carry the
authored-synthetic adapter-artifact identity `sha256:` plus 64 `f` characters.
The first C2 wording incorrectly required a newly computed digest of the C2
adapter definition to equal that inherited value, which would impose an
unjustified preimage requirement.

The frozen plan now keeps two independent checks:

1. the C2 registry's inherited adapter-artifact identity must exactly equal the
   C1 manifest/current-generation identity; and
2. the C2 implementation-definition digest is recomputed over the closed C2
   declarative definition and compared only with its own registry field.

There is no equality or preimage claim between them. This correction narrows
ambiguity without changing the one-adapter, provider-free, authored-synthetic,
in-process, zero-external-effect boundary. No worker was dispatched and no C2
candidate existed under the rejected wording.
