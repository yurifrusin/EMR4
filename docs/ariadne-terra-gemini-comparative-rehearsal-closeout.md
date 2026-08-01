# Ariadne Terra/Gemini Comparative Rehearsal — Closeout

Date: 2026-07-24
Owner: GPT Sol High
Result: `ariadne_terra_gemini_comparative_rehearsal_revision_required`

## Outcome

The comparative rehearsal failed closed before either cloud provider received
a request. Terra's provider-neutral work cell started, so its one-shot process
authority is consumed. Its one-use broker rejected the internal request at the
sealed-input gate. Gemini was then suppressed by the frozen boundary-stop rule;
its ledger remains available.

There was no OpenAI or Google model inference, provider usage or cost,
externally transmitted prompt, generated draft, schema candidate, proofreader
input, comparison, downstream delivery, or human-gate action.

## Exact failure

Four sealed values matched exactly:

- shared authored-synthetic task;
- common provider output schema;
- system prompt; and
- compiled task prompt.

The derived full-schema file did not. The host computed the expected hash over
explicit UTF-8/LF bytes, but the Windows build-context preparation used a text
write. Windows translated LF to CRLF after the expected hash was computed:

- expected:
  `sha256:7efd3644329807462b3efcd3b16552d923a9262b43876432c21698656cde8a6e`;
- executed file:
  `sha256:036e54c1d708255ba6ab68be858074025b71b9a467d9da9540698ac11cbaa5da`.

The broker returned `sealed-request-mismatch` and recorded no
`provider-call-started` event. This is a local byte-preparation defect, not a
Terra model failure, OpenAI service failure, schema-quality result, or
proofreader result.

## Isolation and authority

The inspected Terra cell and broker retained the frozen policy:

- non-root `node` user;
- read-only root filesystems;
- all capabilities dropped and `no-new-privileges`;
- no published ports;
- one internal-only cell network;
- provider credential mounted only into the broker;
- no repository, Docker socket, product, database, event-feed, mailbox, PII,
  protected evidence, historical material, command, or human-action surface.

Terra's ledger is `consumed` because the work cell started. Gemini's ledger is
`available` because its broker and cell were never started. No retry,
single-lane continuation, or Gemini-only continuation is granted by this
closeout.

## Cleanup

Terra's cell, broker, internal network, and Terra image tags were removed by
the runner. The unused Gemini image tags were then removed without starting
them. Final residue is zero comparison containers, zero comparison networks,
and zero comparison image tags. Credential values were never printed, hashed,
persisted, placed in a command line, or exposed to either work cell.

## Post-failure source correction

After the attempt closed, the build-context preparation was changed from a
platform text write to an explicit UTF-8 byte write. A focused regression now
constructs the allowlisted context in a temporary directory and proves all
five expected sealed hashes byte-for-byte, including absence of CRLF in the
derived schema.

This correction is repository-local and provider-free. It was not used by the
consumed Terra attempt and does not authorise or imply a retry.

## Verification

- focused comparative population: 16 passed;
- Python compilation, Node syntax, Ruff, and whitespace: passed;
- deterministic local failure reproduction: exactly one mismatching hash,
  caused by CRLF translation;
- post-correction five-hash regression: passed;
- runtime evidence hash:
  `sha256:7f879a5e5aca0acd2690652cc70f0351c3b4f83bf2462620be3cd8d8bea8cea4`;
- reconstructed executed-runner hash:
  `sha256:fb3c3703fa2f84f9f117fcc1bb39b975f6f52ac4fe2b4f169cccfbd1e3b3b9f5`.

The selected broader Ariadne population retains one pre-existing failure:
the checked-in DeepSeek historical runtime evidence no longer matches three
already-tracked source hashes. This tranche does not alter those historical
files.

## API Spine result

Boundary classification:
`occupied_model_transport_attempt_rejected_before_provider`.

Only authored-synthetic opaque context entered the isolated work cell. Nothing
reached the OpenAI or Google provider boundary. GraphQL, REST/OpenAPI,
PostgreSQL, event, command, product, and human-authority planes remained
unused.

## Next decision

The smallest next candidate is a fresh two-lane attempt using the corrected
byte-stable build context. Because Terra's occupied-process authority is
consumed, that candidate requires a new explicit Yuri decision even though no
provider call occurred. A Gemini-only attempt also requires a fresh decision:
the current Gemini ledger is available, but the frozen plan suppressed it
after the Terra boundary failure.

No retry, Gemini continuation, provider call, prompt transmission, container,
image build, or broader authority is granted by this closeout.
