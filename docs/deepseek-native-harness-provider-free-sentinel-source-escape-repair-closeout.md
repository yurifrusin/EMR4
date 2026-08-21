# DeepSeek native Harness provider-free sentinel source escape repair closeout

Date: 2026-08-21
Timestamp: 2026-08-21T15:53:26.2180712+10:00 (Australia/Brisbane)

## Outcome

Accepted at exact reviewed source `eb8913aacb19d823e251731f9393cc54fe71524c`.

The repair changes exactly one pre-existing source byte: `sentinel_source()` now returns a raw Python bytes literal (`br'''`) rather than an ordinary bytes literal (`b'''`). Python therefore preserves the JavaScript `\r`, `\n` and `"\n"` spellings that the generated module needs.

## Evidence

- The whole controller equals its planning-source Git preimage plus that one inserted `r`; every request, profile, tool, guard and lifecycle byte outside the literal prefix is unchanged.
- The generated sentinel is exactly 1,157 bytes with SHA-256 `8b53bc7fb781d29d87310ee2d3425ca159a62fed4893a3e4db94069d63cd60bd`.
- Raw line terminators inside JavaScript regex or quoted literals fell from three to zero.
- All 133 tracked files under the consumed bounded-worker attempts, repaired-sentinel boot proof and accepted diagnosis roots remain byte-identical to the planning Git object.
- The pre-repair diagnosis baseline passed 8/8. The published clean candidate passed 99/99 applicable tests, plus Ruff and bytecode compilation.
- The fresh pre-verifier receipt passed with all five rehydration sources, exact protected refs and zero caller-supplied Git object IDs.
- No Node, Harness, broker, worker, model, provider or network process/request ran.

Three frozen historical-state selectors were retained but excluded because they deliberately require the consumed pre-repair controller digest or attempt-004 latch. One real-Node broker fixture was also excluded by the zero-Node contract. The exact selection is recorded without changing historical artifacts.

## Efficacy and contained issues

The one-byte contract was effective: it prevented repair broadening and converted an opaque preactivation failure into a mechanically checkable source property. The validator's first direct invocation exposed a missing repository-import bootstrap, which was corrected before evidence generation. The first surrounding packet also included three known historical-state checks; the corrected packet records their exact exclusion and passes every remaining selector.

Clockwork revision 590 records four contained procedure observations with none open. The register-closeout observation required three dry-run-only rejections across decision-source, incident-evidence and revision-reading surfaces; a later patch then omitted one JSON comma and was rejected during parsing. The final typed shape binds existing evidence, pre-authors the exact revision reading, validates after every patch and leaves canonical projection to clockwork.

## Claim boundary and successor

This result proves lexical validity of the generated sentinel and preservation of the frozen boundaries. It is not a Node/Harness boot result and says nothing yet about DeepSeek worker/model/provider performance.

Proceed under standing authority with `deepseek-native-harness-provider-free-source-repaired-sentinel-native-boot-proof`: one fresh provider-free rc7 Node/native-Harness process, sentinel-only initial profile, no broker/worker/model/provider/network activity, no retry, and a structured pass or fail-closed terminal with complete cleanup.
