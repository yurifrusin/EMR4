# Source-evidence context

Collection ID: `raisa-two-component-oidc-verifier-2026-08-02`
Collection SHA-256: `be59a6c7d6b6d9c5a60cda59311b4f524913bddb104ae8e72225c524e636960b`
Target Git revision: `805b32ef616daf3c904b8de698856ec211b17bec`
Source drift: none observed during collection

We reviewed the following ten artifacts. Repository sources were read from the stated target or, for the diagnostic, from the exact untracked authored artifact. Distribution hashes are the reviewed PyPI files. External documentation is cited by canonical primary-source URL and was not copied into the repository.

| ID | Artifact | Evidence identity |
|---|---|---|
| E001 | Parent architecture plan | `sha256:636fdc9002dc0805ba0bc89f0cf445162afeea9ea2821b57de0011913fb916cc` |
| E002 | Parent architecture design | `sha256:62cdce0695c7e793b224913c64a4ec9ff82388b0d1771c1a2b0525a6c2df8cb7` |
| E003 | Parent threat-model delta | `sha256:6e90f782a116db10f07403c04755d8b0600568f5603611f8b05402eb9cba7272` |
| E004 | MSAL admission diagnostic | `sha256:bf72319f7de8ed6d32f56bead6a45092cf9089514f5a7927634485d8a9457bf0` |
| E005 | `msal-1.37.0` wheel | `sha256:dd17e95a7c71bce75e8108113438ba7c4a086b3bcad4f57a8c09b7af3d753c2d` |
| E006 | `Authlib-1.7.2` wheel | `sha256:3e1faedc9d87e7d56a164eca3ccb6ace0d61b94abe83e92242f8dc8bba9b4a9f` |
| E007 | `joserfc-1.7.4` wheel | `sha256:32d46c2cd5e3203c13e87a6c61333cab310b1ba80cd54b4c4f386a848a122463` |
| E008 | Microsoft OIDC protocol guide | `https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc` |
| E009 | Microsoft token validation and key rollover | `https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens` |
| E010 | Authlib 1.7.2 OIDC verifier source | `https://github.com/authlib/authlib/blob/v1.7.2/authlib/integrations/base_client/sync_openid.py` |

The collection hash is SHA-256 over the sorted `ID|artifact|identity` lines with LF endings. The collection contains ten artifacts. No runtime, provider or production telemetry was used.
