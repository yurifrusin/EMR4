# DeepSeek preset-mount sanitizer — paired negative closeout

Date: 2026-08-22

Timestamp: 2026-08-22T05:40:14.8644397+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The translator itself is built, but its tiny Node test did not yet reach a
translation result. Three processes stopped before producing the closed list.
The important improvement is that the third stop is no longer opaque: we have
a clock reading—exit 134, no ordinary output, and 715 bytes of discarded error
output—without storing the path-bearing error text.

All three tests were started with an entirely empty Windows environment. That
is unlike the repository's earlier successful Node fixtures, which inherit the
host environment. We have not declared this the cause; it is the narrowest
remaining launch difference. The next tranche supplies only five mundane
Windows runtime keys and no secrets, then runs the unchanged translator once.

## Technical summary

- Three consumed candidates: `475a5b6c210a1bc98f75234f544b5c619a94b704`,
  `50a17beba7ea3a461cc2dd2154f747b307119f20` and
  `03a53c5b6f5e487b991e465a73c6368aa9759d74`.
- Attempt 003: exit 134; stdout 0 bytes; stderr 715 bytes; content absent;
  hashes retained.
- Sanitizer result: not admitted.
- DeepSeek Harness, DSH, worker/model/provider and product effects: zero.
- Verification: 15 implementation plus 7 negative-evidence tests, Ruff,
  compilation, schemas, hashes and whitespace pass.
- AER-0881 through AER-0889 contain the workflow incidents, including two
  clockwork pre-publication rejections of descriptive/derived form drafts.

## Place in Raisa and deliberately closed

This is a useful if awkward control-plane result: process failure has become a
safe gauge reading rather than an untraceable stderr event. It still does not
make DeepSeek ready for Raisa work. Runner connection, worker/model use,
product/data, ordinary-practice, production, deployment, release, Pages and
protected refs remain closed.

## Next tranche

Proceed under standing authority with the five-key Windows minimum-environment
recovery. Yuri's attention is not required.
