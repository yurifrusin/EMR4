# Reception One Bureau Model Text Lane — Threat-Model Delta

## Scope

This delta covers the provider-blocked, authored-synthetic model text lane. It
adds an untrusted candidate adapter and a disposable fixture cell. It opens no
provider, credential, product, database or command connection.

## New trust boundary

The model-shaped output is hostile input. It is not an intent decision,
proposal, command or evidence merely because it conforms to JSON.

| Threat | Required control | Failure disposition |
|---|---|---|
| Model forges practice, request or context scope | Candidate schema excludes the envelope; trusted host attaches frozen values | reject |
| Model invents a patient, time or literal | Arguments accept only allowlisted source handles or prior typed outputs | reject |
| Model invents an operator or signature | Exact closed catalogue and deterministic signature check | reject |
| Model reorders a dependency after its consumer | Deterministic topological and typed-output check | reject |
| Model escalates from proposal to booking/write | Fixed `proposal_only` ceiling; no confirm/write operator; backend command path absent | edge abort |
| Prompt injection asks for credentials, network or tools | Cell receives none; request contains no tool surface; proofreader rejects foreign fields | reject |
| Revision loop leaks a draft or expands authority | One bounded revision; feedback is path/code-only | edge abort on exhaustion |
| Stale output races a committed Diary event | Exact context revision and expiry are rechecked immediately before admission | reject |
| Container reaches host/provider or reads credentials | `--network none`, no mounts, no forwarded environment, non-root, read-only root, dropped capabilities | edge abort |
| Fixture is mistaken for model-quality evidence | Evidence labels it provider-free and fixture-generated; provider call count remains zero | closeout limitation |

## Preserved properties

- FastAPI/PostgreSQL remains the owner of Diary truth and any future mutation.
- The candidate cannot call GraphQL, REST, a database, a provider or a shell.
- Raw historical Diary states and holdouts remain sealed.
- No API key or ADC path is read, inspected, copied or passed to the cell.
- A later occupied call is a separate authority decision and security review.
