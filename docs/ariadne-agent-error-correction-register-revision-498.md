# Ariadne agent error and correction register — revision 498

Date: 2026-08-19

Timestamp: 2026-08-19T02:10:11.1536438+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0575 records the recurring omitted UTF-8 decoding. AER-0576 corrects its
initial non-schema stage. AER-0577 removes its one-way conceptual peer link and
uses the existing recurrence signature as the single grouping source. All three
candidates failed before publication and canonical state was unchanged.

Revision 498 contains 577 bounded incidents. All are corrected or contained;
none is open.

## Prevention

The typed clockwork must centralize UTF-8 loading, source enums directly from
schema and derive recurrence groups from one event field. Peer links remain a
separate validated symmetric relationship, eliminating manual back-link work.
