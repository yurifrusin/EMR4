Date: 2026-09-09
Timestamp: 2026-09-09T09:52:00+10:00 (Australia/Brisbane)

# EMR4 status and bounded controller maintenance

EMR4 remains in recovery. The accepted G1B.1 state/event kernel and published
G1B.2 readiness are intact. The two-file journal implementation is locally
tested and preserved, but is not accepted or published. The cumulative admission
policy omitted two legitimate transition records; its corrected exact package
now has an independent review PASS.

The maintenance candidate supplies a way to publish that correction through an
authenticated executable source and a complete staged-tree comparison. It also
gives the journal's manifest and scope checks one explicitly accepted base.
Yuri approved the bounded index processing, activation and recovery-branch
publication in advance. Actual completion requires the separate external
operation receipts; this pre-publication letter does not claim it has happened.

## Review reconciliation

[Governance stop analysis](https://chatgpt.com/c/6a9e7016-8a8c-83ec-8888-3310aa914f86)
provided diagnosis. [Review Admission Failure](https://chatgpt.com/c/6a9e7150-8f58-83ec-9089-8d46e396464a)
identified the cumulative-policy omission and mixed full-suite result.
[Governance review](https://chatgpt.com/c/6a9f5629-2080-83ec-bc1f-a5ecdb06806e)
rejected the first correction, then returned `POLICY_REPAIR_REVIEW_PASS` for
the corrected exact two-file package. Its later maintenance architecture advice
was conditional on the index-access decision, which Yuri subsequently approved.
Architectural advice, code-review PASS, publication and activation remain
separate evidence; none is inferred from another.

## Technical position and remaining work

The maintenance generation is a direct child of governing transition
`f726021a71e08f81529d3eecd807a695f7ba7e3a`. It uses a separately authenticated
29-file source capsule, exact changed/frozen file manifest, detached-HEAD CAS,
lease-protected exact-SHA task-branch publication and external exclusive
activation evidence. It does not execute candidate source or use the old
complete-tree loader. The [maintenance contract](../../../docs/architecture/ariadne-g1b2-controller-maintenance-contract.md)
defines the exact source, effects, uncertainty rules and journal successor.

There are 307 distinct focused passing maintenance cases. The historical full
suite remains 430 passed, 33 failed, 1 skipped. Earlier complete-tree fixture
drafts were preserved and excluded; no full-suite or historical-equivalence
PASS is claimed. The first zero-enumeration claim was withdrawn after discovering
old-loader metadata traversal. New index processing uses Yuri's explicit bounded
approval and exposes no individual sealed paths or hashes.

Smaller models remain in use where useful: Luna for bounded helpers/tests and
Terra for independent review. Root checks their work, corrects errors and owns
acceptance/integration. A faulty Luna inventory was rejected and replaced using
literal source lists and exact byte verification. No billed saving is asserted.

After maintenance publication and activation, the next work is exact journal
admission/review using the externally authenticated activation base, plus the
separately unresolved historical fixture work. The broader Raisa goal remains
one safe command/event truth across Word and the Diary. Product changes,
provider calls, real-data use, G1C, deployment, Pages and protected integration
remain closed. No additional owner decision is pending for this maintenance.
