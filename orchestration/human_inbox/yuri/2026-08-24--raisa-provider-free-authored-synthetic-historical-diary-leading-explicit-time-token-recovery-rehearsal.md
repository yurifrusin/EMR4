# Raisa leading Diary time-token recovery — lay and technical closeout

Date: 2026-08-24

Timestamp: 2026-08-24T07:59:22.5874518+10:00 (Australia/Brisbane)

Attention required: **no**

## Lay summary

The new clock reader works. It can recognize a time written at the beginning of
one Diary cell line, attach that time only to the rest of that line, and refuse
lookalikes such as dates, phone numbers, email addresses, invalid times or a
time buried later in the text. It removes the clock label before making the
private fingerprint used to follow the line through later snapshots.

This makes one fresh local measurement worthwhile. No historical file was read
for this parser work, and the first-use gate remains closed because no reusable
historical-derived scenario exists yet.

## Technical summary

Exact reviewed source is `5a3c589873a104e948e65eaadacd2397f0621a3b`.
The strict anchored parser, same-segment direct mapping, no-forward-fill rule,
contact/date denials and token-free HMAC equivalence pass 29 focused controls.
All 219 controls across 23 historical-Diary files pass with Ruff, compileall,
filesystem/source boundaries and diff checks.

Pre-closeout review corrected one stale integration assumption: aggregate
admission had still demanded main-story anchors. It now recognizes story
anchors and leading tokens as the only two explicit source forms while retaining
all separate utility and privacy gates. This was corrected before historical
access and caused no private-data rerun.

Deliberately closed: first use, reusable historical derivatives, product,
database, client, ordinary-practice, provider/model, production, deployment,
release, Pages, protected evidence and protected refs.

Next: freeze and run exactly one fresh 80-snapshot local leading-token
measurement at a new ignored root, with one metadata bind, one content run, no
retry, exact Word cleanup and generic aggregate retention only.

Pushover delivery succeeded under request
`6a8016db-19aa-4a12-aa28-b65e725c2afb`.
