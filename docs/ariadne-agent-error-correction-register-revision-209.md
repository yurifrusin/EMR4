# Ariadne agent error and correction register — revision 209

Date: 2026-08-11

Revision 209 adds AER-0243 and brings the register to 243 bounded incidents.

## AER-0243 — inherited identity conflated with a new definition digest

The first frozen AES-C2 plan required the computed digest of the new C2
declarative adapter definition to equal the accepted C1 manifest's authored-
synthetic `adapter_artifact_digest` (`sha256:` plus 64 `f` characters). The
mandatory pre-dispatch plan challenge caught the infeasible preimage requirement
before any DeepSeek call or candidate source existed.

The corrected plan treats the values as independent semantic layers. The
registry must preserve exact equality with the inherited C1 adapter-artifact
identity, while a separate C2 implementation-definition digest is recomputed
against its own registry field. No equality or preimage claim connects them.

The prevention control is to name the semantic layer and preimage for every
descendant digest; an inherited declared identity is never equated with a new
content digest unless the accepted predecessor explicitly defines that
relationship.
