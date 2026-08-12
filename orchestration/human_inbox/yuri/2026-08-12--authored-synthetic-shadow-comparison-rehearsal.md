# Shadow-comparison rehearsal — lay and technical closeout

Date: 2026-08-12

Result: `passed`

## Lay summary

We have now rehearsed the proposed diagnostic “shadow” beside the old
appointment write routes without connecting it to the product. When switched
off—or when any required permission/configuration element is missing—it does
nothing. When admitted in the synthetic rehearsal, it correctly spots the three
controls the old routes currently lack, distinguishes unexpected and future
complete cases, and safely loses diagnostic evidence during timeout, overload
or sink failure.

Most importantly, the original route result was byte-for-byte identical before
and after every one of the eighteen cases. The shadow has no vote over success,
failure, response, audit or command behavior. This gives us evidence that the
comparison idea is useful without making correctness depend on the observer.

## Technical summary

- exact source: `47b5f09ecf35225da25812ba87bb656a1094fc7e`;
- evidence: provider-free, unmounted, authored-synthetic;
- 18 scenarios: 6 denied and 12 admitted;
- all four current raw adapters return the exact accepted three-gap set;
- unexpected gap/candidate plus semantic equivalent/divergent classifications
  pass, with the divergent mismatch limited to `command_digest`;
- observer failure emits one safe record; timeout/overflow emit zero; sink
  failure drops its one record candidate;
- 10 candidates, 9 emitted diagnostics, maximum 1 per scenario;
- 18/18 primary canonical byte comparisons match;
- 51/51 hostile mutations fail closed;
- 17 tranche, 209 focused and 191 canonical tests pass; and
- Continuity 250 / Compass 232 is current.

## Issue exposed and resolved

The first hostile-mutation run included a no-op test mutation. It was corrected
to attack the missing-generation denial case. This changed no product or
architecture behavior.

## Deliberately closed

No application route, observer runtime, queue, sink, persistence, database,
source, watcher, event, provider, product/patient data, kernel, command/write,
deployment, release, Pages or protected ref has opened. The existing untracked
files, including `docs/branding/`, remain preserved and excluded.

## Place in the Raisa direction and next tranche

This is the evidence bridge between the already accepted pure route adapters and
a possible default-off product instrumentation seam. The next tranche will
freeze that seam as architecture only: where a post-result projection could be
mounted, what dependencies must be impossible, and how default-off behavior is
proved before any application route is edited.

Yuri's attention is not required; the next architecture plan is dependency-
satisfied and proceeds under standing authority.
