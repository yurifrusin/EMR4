# Gate -1 source-evidence context

Collection ID: `model-required-bureau-gate-minus-one-2026-08-04`

Collection SHA-256: `e3b6721331853ee41598c226139dc09820e308413322abc72b7a0762baa6fc70`

Target Git revision: `b09739183ddbe1a102086460749a84741a23b11b`

Source drift: none observed during collection

## Scope

Gate -1 is an architecture-only adversarial review of the model-required
Bureau design. It assumes that any provider model may follow direct or indirect
prompt injection and that the local cognitive wrapper may be compromised. It
asks whether deterministic controls still prevent authority gain, illicit
information flow and host compromise.

The review does not run a model, open product or patient data, wire a provider,
add an actuator, change deployment, or implement the proposed hardening.

## Repository evidence

| ID | Artifact | Evidence identity |
|---|---|---|
| E001 | Model-required deterministic-authority Bureau architecture | `sha256:86d43800661ce70a1884a60b0deb62482b3d348427e19de6d39cc82eeacc7271` |
| E002 | Rayleen, Davida and controlled-recovery development plan | `sha256:8dab2510b9109dc9ce9778cb3d7798d6a992ed8d8deadd9ee38c5ec48c5ea8f7` |
| E003 | Model-required Bureaus threat-model delta | `sha256:9db185ab4606cab7d1e82181c356728fcf08daf4726f77245580f6817d5e95c4` |
| E004 | Bounded Cognitive Work Cell protocol design | `sha256:8c259345cc6334928b342356ecfd66aa9e4c391d2c4bc209509a17a0fb2be278` |
| E005 | Bounded Cognitive Work Cell threat-model delta | `sha256:0ed2cfe9cdf42656fe418a1775e816d13343303b51b9fcc6303adfe04eba5940` |
| E006 | Sandbox-DAG protocol design | `sha256:489220d618a1e62cc4f911579158db823c403e5038151a488b5eac0841ae001d` |
| E007 | Bernie-Davida shared-agent boundary | `sha256:ada91c7338fa46745d7a2a62e98431a61af52088cef76ecee9b09ca1ab195081` |
| E008 | Bernie-Davida seam threat-model delta | `sha256:46e9daccd521dd292ffdff860c8faf4178d4fd5abbcda0bed4b7cb1c57dcda09` |
| E009 | Real-isolation rehearsal design | `sha256:e8d8d7d1683637ff18028ddfe574c9a2802b64dac19cf8dba96795f0f4d1b354` |
| E010 | Real-isolation rehearsal threat-model delta | `sha256:93eb569d570dfd2fd80046be98e8b77061c8180022261ab07e7c5cc8b0754f61` |
| E011 | Bounded agent-admission design | `sha256:14db6322cfbaed1c2dd823d1c3d393414644253343100c90830bdb6bb3169cec` |
| E012 | Bounded agent-admission threat-model delta | `sha256:103c141488d951c6e9800b273e08d5a9d0d38c74063b55ac3b5854b52d2e429f` |
| E013 | Access AI API design | `sha256:6befbd638f486291008d972f44c0fc42879aef0c2f4e4c1b4725f9244243a421` |
| E014 | API Spine blueprint-first/model-second boundary | `sha256:f76b81b7d86f6e1085dca2dfa672a1caa1f322211a64ed01b86a199f354b29d7` |

## Primary external evidence

| ID | Artifact | Primary source |
|---|---|---|
| E015 | NIST CAISI large-scale AI-agent red teaming | <https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition> |
| E016 | Microsoft prompt-to-RCE and host-bridge research | <https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/> |
| E017 | CaMeL: Defeating Prompt Injections by Design | <https://arxiv.org/abs/2503.18813> |
| E018 | FIDES: Securing AI Agents with Information-Flow Control | <https://arxiv.org/abs/2505.23643> |
| E019 | Design Patterns for Securing LLM Agents against Prompt Injections | <https://arxiv.org/abs/2506.08837> |
| E020 | NCSC: Prompt injection is not SQL injection | <https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection> |
| E021 | NCSC: Thinking carefully before adopting agentic AI | <https://www.ncsc.gov.uk/blogs/thinking-carefully-before-adopting-agentic-ai> |

The collection hash is SHA-256 over the sorted
`ID|artifact|identity` lines recorded in `evidence-index.json`, with LF endings
and one final LF. The collection contains 21 artifacts. External sources are
linked rather than copied. No runtime, provider or production telemetry was
used.

## Evidence synthesis

### Observed

- EMR4 already separates cognition, proofreading, authority and execution,
  prohibits model-to-database or model-to-actuator access, uses closed typed
  candidates and requires deterministic readback (E001-E014).
- Existing isolation evidence proves a bounded container configuration, not
  safety of the host kernel, daemon, bridge code, future provider runtime or
  model behavior (E009-E012).
- The current Bureau contract records provenance and freshness, but it does not
  yet specify end-to-end confidentiality and integrity labels, label joins, or
  sink policies for every value that can influence a command (E001-E003,
  E007-E008, E013-E014).
- Recent research demonstrates successful attacks across frontier models and
  concrete prompt-to-code-execution and arbitrary host-file-write paths when
  model-influenced values reach unsafe framework or tool bridges (E015-E016).
- The current research consensus does not treat model alignment, delimiters,
  blocklists or injection detectors as a complete security boundary. Structural
  patterns instead isolate untrusted data, constrain actions and enforce
  deterministic data-flow and capability policy (E017-E021).

### Inferred

- A syntactically valid, grounded candidate can still be attacker-directed if
  low-integrity text influenced the choice of action or a security-relevant
  argument. Schema validation alone cannot reveal that influence.
- If any future wrapper exposes evaluation, file, URL, callback, telemetry,
  metadata, shell or generic tool bridges, compromise of the cognitive cell can
  become host compromise or data exfiltration even though the proofreader
  rejects ordinary free-form commands.
- Human confirmation does not repair hidden provenance or covert data-flow
  defects and can add confirmation-fatigue risk.

### Proposed

Admit Gate zero only after it incorporates both selected Gate -1 controls:

1. an end-to-end deterministic label and capability envelope; and
2. a one-attempt, broker-mediated, deny-by-default cognitive-cell contract.

The model remains mandatory for intelligent dialogue, but is treated as an
untrusted candidate generator. Detection, model safeguards and adversarial
evaluation remain useful defense in depth; none may grant authority or remove
the deterministic controls.
