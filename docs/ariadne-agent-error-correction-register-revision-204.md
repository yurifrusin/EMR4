# Ariadne agent error and correction register — revision 204

Date: 2026-08-08

Revision 204 adds AER-0238 and brings the register to 238 bounded incidents.

## AER-0238 — emitted stderr digest and evidence schema disagreed

The first whole-document validation of the immutable attempt-048 pass exposed a
repository schema defect. The harness consistently emits bounded digests in the
repository-standard `sha256:<64 lowercase hexadecimal characters>` form, but
the nested `stderrDigest.sha256` schema field still required the older bare
64-character form. Synthetic passing evidence had mirrored the stale schema,
so earlier tests did not expose the disagreement.

The immutable pass evidence remains untouched. The schema now reuses the
existing prefixed digest definition, the synthetic fixture matches the real
emitter, a hostile bare digest is rejected, and the exact sealed attempt-048
document validates as a whole. This changes evidence admission only; it does
not change the durability SQL, behavior contract, database result or runtime
authority.
