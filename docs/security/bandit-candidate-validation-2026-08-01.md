# Bandit candidate validation — 2026-08-01

Target: working tree rooted at `2ae8f2173276147e59be361e0182f6cb4b7453fa`
Input: 14 unexpected medium/high candidates from
`scripts/security_bandit_gate.py`
Method: instance-preserving static source/control/sink trace plus exact gate
rerun

## Outcome

None of the 14 candidates survives as a reportable product security finding.
Eleven B108 instances are Docker `--tmpfs` mount destinations or exact Docker
policy expectations; no host temporary file is created at the flagged line.
The container relay B104 listener has no published port and is restricted to
the exact internal Docker work-cell network. The two host-broker B104 listeners
are transient local evaluation infrastructure rather than product services;
their reachable action requires a generated 48-byte bearer, constant-time
comparison, an exact path and request packet, bounded request size, one-use
state and a 90-second deadline.

The host listeners retain a defence-in-depth limitation: the OS firewall and
Docker Desktop host-interface behavior are not repository-enforced, so local
network traffic could add availability noise during the short rehearsal. That
does not grant the provider call or protected value because the bearer and
exact packet checks remain before execution. This residual is documented, not
silently treated as proof of loopback binding.

Each reviewed site now carries an exact, local `# nosec B104` or
`# nosec B108` annotation with its boundary rationale. The central baseline
remains limited to the two existing reviewed Git-identity B324 instances.
`scripts/security_bandit_gate.py` then passes with exactly those two baseline
findings and no unexpected medium/high result.

## Validation rubric

- [x] Identify the exact scanner source, affected operation and claimed sink.
- [x] Classify whether the line is a host product surface, host evaluation
  helper, container listener or inert Docker policy string.
- [x] Trace the nearest reachability, authentication, isolation, size, lifetime
  and cleanup controls.
- [x] Identify a concrete confidentiality, integrity, authority or availability
  impact that remains after those controls.
- [x] Preserve every candidate instance and rerun the exact blocking gate after
  the local disposition annotations.

## Closure table

| Row | Instance | Source | Sink/control | Disposition | Counterevidence or proof gap | Survives |
|---|---|---|---|---|---|---|
| BV-001 | `scripts/ariadne_vertex_sydney_gemini_25_broker.py:449:B104` | local/Docker-host network traffic during an occupied rehearsal | transient all-interface host HTTP broker | suppressed | 48-byte ephemeral bearer, constant-time check, exact packet/size, one use, 90s deadline; OS firewall not repository-proved | no |
| BV-002 | `scripts/ariadne_vertex_sydney_gemini_25_launcher.py:156:B108` | trusted launcher constant | Docker `--tmpfs /tmp` argument | not_applicable | literal configures a bounded noexec/nosuid container mount; no host temp file operation | no |
| BV-003 | `scripts/ariadne_vertex_sydney_gemini_25_launcher.py:200:B108` | trusted launcher constant | Docker `--tmpfs /tmp` argument | not_applicable | same exact container-mount boundary | no |
| BV-004 | `scripts/ariadne_vertex_sydney_gemini_25_rehearsal.py:342:B108` | Docker inspect output | expected cell tmpfs policy | not_applicable | comparison-only expected dictionary; no filesystem creation | no |
| BV-005 | `scripts/ariadne_vertex_sydney_gemini_25_rehearsal.py:404:B108` | Docker inspect output | expected relay tmpfs policy | not_applicable | comparison-only expected dictionary; no filesystem creation | no |
| BV-006 | `scripts/ariadne_vertex_sydney_gemini_25_relay.py:84:B104` | exact work-cell internal-network request | container all-interface relay listener | not_applicable | no port publication, exact internal network, read-only/unprivileged container, bounded request | no |
| BV-007 | `scripts/reception_one_bureau_model_text_lane_broker.py:1693:B104` | local/Docker-host network traffic during an occupied rehearsal | transient all-interface host HTTP broker | suppressed | ephemeral bearer, constant-time check, exact packet/size, one use, 90s deadline; OS firewall not repository-proved | no |
| BV-008 | `scripts/reception_one_bureau_model_text_lane_isolation.py:214:B108` | trusted isolation constant | Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-009 | `scripts/reception_one_bureau_model_text_lane_live.py:948:B108` | trusted live-lane constant | relay Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-010 | `scripts/reception_one_bureau_model_text_lane_live.py:1003:B108` | trusted live-lane constant | cell Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-011 | `scripts/reception_one_preprinted_form_v5_isolation.py:201:B108` | trusted isolation constant | Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-012 | `scripts/reception_one_proofreader_dialogue_v4_isolation.py:201:B108` | trusted isolation constant | Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-013 | `scripts/reception_one_shared_typed_plan_isolation.py:203:B108` | trusted isolation constant | Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |
| BV-014 | `scripts/reception_one_structured_source_plan_isolation.py:205:B108` | trusted isolation constant | Docker `--tmpfs /tmp` argument | not_applicable | bounded container mount, not host temp-file creation | no |

## Confidence and remaining uncertainty

Confidence is high for every B108 row and the container-relay B104 row because
the scanner category is defeated by the exact Docker argument/inspect context.
Confidence is medium-high for the two host broker rows: static tracing proves
the authority checks, while a hostile local-network availability exercise was
not run and would be disproportionate for closed one-shot evaluation tooling.

No provider call, external system, cloud resource, protected evidence or
production surface was exercised during this validation.
