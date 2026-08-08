# Threat-model delta: Raisa Agent Execution Surface and Containment Gate

Date: 2026-08-08

Status: accepted future security boundary; no runtime opened

## Scope change

The existing Bureau architecture controls context admission, model candidate
shape, deterministic proofreading, human authority and backend commands. This
future gate adds the missing execution-containment boundary beneath an occupied
work cell before it receives real product context or any executable tool,
credential, network, filesystem, database or command-adjacent capability.

## Assets

- human, practice, purpose and atomic capability authority;
- ContextFrameSet confidentiality, provenance, freshness and expiry;
- provider, database, cloud, tool, command and deployment credentials;
- application, clinical, financial and Diary truth;
- generation manifests, leases, budgets and revocation state;
- provider/tool adapters and supply-chain identity; and
- minimized audit and incident evidence.

## Trust boundaries

1. user/product surface to backend authorization;
2. backend Context Fabric assembler to occupied Bureau work cell;
3. work cell candidate to deterministic proofreader;
4. proofreader output to the external capability broker;
5. broker to an exact provider/read/tool adapter;
6. adapter to product or external infrastructure;
7. command proposal to the separately authorised REST/OpenAPI command; and
8. runtime telemetry to audit, stop, revocation and incident response.

## Threats and required controls

| Threat | Required control | Required evidence |
|---|---|---|
| Prompt rules are treated as containment | Enforcement outside the model process | Model output cannot alter manifest, broker or kill switch |
| Allowed proxy becomes a general bridge | Exact destination/method/media/byte/count/time egress | Arbitrary URLs, redirects, DNS, package registries and public relays fail |
| Ambient cloud or application credential is stolen | Work cell has no credential; broker uses short-lived audience-bound lease | Environment, metadata and token-enumeration probes reveal no credential |
| Local-file or template feature executes content | Closed inert frame/output schemas; no path, template or executable deserialisation | File, HDF5-external-storage, template and pickle-shaped attacks fail |
| Encoded or exception-channel exfiltration bypasses content filters | Destination-independent byte/count budgets and normalized telemetry | Clear, encoded, chunked, compressed and exception attempts share one ceiling |
| Thousands of failed probes eventually find a path | Cumulative denial/action/time/destination budget and external stop | Threshold crossing revokes the generation before another operation |
| Agent reconstructs authority after restart | New generation identity; old leases, aliases and caches invalid | Cross-generation and cross-Bureau replay fail |
| Model selects executable, SQL, route or cleanup target | Closed trusted mapping in the broker/adapter | Hostile candidate mutations cannot change operation identity |
| Context or memory carries executable instructions or secrets | Typed minimized frames and lossy Memory Bank projection | Forbidden fields and executable references are schema-rejected |
| Supply-chain write or artifact substitution persists | Digest/version binding and no CI/repository credential in runtime | Image, adapter, manifest and model/provider contract identity readback |
| Event or context frame becomes command evidence | REST/OpenAPI command reauthorization, confirmation, idempotency and readback | Command-shaped candidate remains inert until separate command gate |
| Detection sees signals but fails to stop activity | Cross-layer correlation plus externally owned automatic stop/revoke | Boundary-probe scenario produces one terminal incident disposition |

## Residual risks

- vulnerabilities in the broker, container runtime, host kernel or provider;
- side channels not represented in the finite hostile set;
- compromised pinned artifacts or signing infrastructure;
- operational failure to rotate a genuinely exposed external credential; and
- future high-risk code-execution cells that may require VM/tenant isolation in
  addition to the broker.

## Stop conditions

No occupied or product-runtime descendant may proceed if a work cell can reach
cloud metadata, obtain a reusable credential, choose a destination or
executable, exceed cumulative budgets, reuse a stale lease, execute context
content, bypass the proofreader, invoke a command, suppress the kill switch or
emit unminimized evidence.

The present plan grants no provider call, product/patient data, credential/IAM
change, runtime wiring, deployment, production, release, Pages or protected-ref
authority.
