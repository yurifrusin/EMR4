# Threat-model delta: historical recovery validator source binding repair

Date: 2026-08-21

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-historical-recovery-validator-source-binding-repair`

## Protected assets

- the immutable accepted pre-HMR recovery evidence and consumed attempts;
- the exact seven source blobs at full Git commit
  `12d8758fee2504435ca2b4ccf6225b9d7a86a6a1`;
- the old validator's zero-subprocess guarantee;
- current product, configuration and protected refs; and
- the prohibition on any Harness, worker, model or provider execution.

## Delta threats and controls

| Threat | Fail-closed control |
|---|---|
| Mutable descendant files are mistaken for historical reviewed source. | The old validator projects the accepted historical map; the independent checker hashes exact blobs from the frozen Git object. |
| A seven-character abbreviation or ambiguous object is accepted. | The schema requires 40 lowercase hexadecimal characters, resolution must return the identical value and the object must be a commit. |
| A fabricated but valid-looking commit substitutes for the accepted source. | The contract fixes the exact commit and the checker requires exact equality plus ancestry to current `HEAD`. |
| A path is absent, renamed or traverses outside the frozen source set. | The contract fixes the exact seven-key map; `git show` receives only those keys and any read failure denies. |
| Historical evidence is silently regenerated to fit current source. | Eight accepted artifacts are hashed byte-for-byte; this tranche has no write authority over the historical Continuity directory. |
| Adding Git verification breaks the old zero-process predecessor test. | Git proof is isolated in the new checker; the old validator is retested with shared `subprocess.run` and `Popen` forbidden. |
| A validator repair weakens behavioral or immutable-attempt checks. | Only source-map construction changes; scenario, mutation, schema, ordering and attempt-integrity checks continue and the old evidence object must still compare exactly. |
| The repair becomes a pretext for another occupied attempt. | Contract and evidence require zero Harness/broker/worker/model/provider activity and forbid retry, resume, overwrite and reclassification. |
| Product or authority scope expands. | No product/config/API/database/route/adapter/flag/allowlist/grammar/client/waiting-area or protected-ref paths are owned. |

## Claim boundary

A pass proves only that the accepted recovery validator is stable against
legitimate descendant source evolution and remains independently bound to its
exact historical Git blobs. It does not prove DeepSeek quality, native Harness
reliability, production suitability or any ordinary-practice admission.
