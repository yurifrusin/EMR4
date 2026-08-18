# Ariadne agent error and correction register — revision 423

Date: 2026-08-18

Status: superseded correction update

Reasoning level: high

Revision 423 preserved accepted revision 422 and added AER-0493. The pinned
Linux rc.7 package and native modules loaded, but a provider-free root-package
import probe inferred an `index.js` entry that the CLI-only package does not
declare. Exact package metadata instead names `lib/bin.js` and provides no root
`exports` or `main` entry.

The correction requires entrypoint discovery from package metadata before any
probe. No Harness session, broker container or provider call had started.

This revision was superseded before acceptance by revision 424, which records
a later command-scope incident from the same pre-dispatch correction cycle.
