# AES-C5 local-fake source-head misbind analysis

Date: 2026-08-11

Before generating the local-fake preexecution receipt, Sol placed a fabricated
forty-character expansion of the displayed short commit `e3ebc119` into the
runtime state instead of mechanically capturing the object ID. The error was
noticed before preflight and before any database, product-route, credential,
cloud or provider operation. The invalid state supplies no authority.

The exact commit was then captured with `git rev-parse HEAD` and verified with
`git cat-file -e` as `e3ebc119f81909555faa0147dfa428c0d6a78097`. The
corrected v2 runtime state repeats all five rehydration sources using only that
captured value.
