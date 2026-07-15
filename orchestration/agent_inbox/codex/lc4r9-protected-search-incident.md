# LC4R9 Protected Search Incident

Date: 2026-07-15

During Sol's source-generator orientation, a repository search intended to
exclude generated development fixtures used a scope covering `tests/` and a
glob that did not exclude the protected holdout directory. The command printed
protected fixture path names and generic matching lines containing audit
`change_type` vocabulary.

Exposure was initially limited to path names, line numbers, and generic audit
`change_type` lines. A later source-location search attempted to exclude the
protected fixture directories but did not exclude the protected LC4 support
module. It printed source-location matches from that module, including generic
semantic-field and coverage helper lines. Sol did not inspect protected
utterances, entities, generated scenario IDs, complete records, aggregate
results, seals, receipts, or reports, and did not run, import, evaluate,
regenerate, or hash the holdout. Nevertheless, both search outputs are content
exposure and are not classified as metadata-only.

Containment:

- the output is quarantined from LC4R9 reasoning and must not be copied into a
  worker packet, test, report, or implementation;
- no remaining LC4R9 command may search the broad `tests/` tree; every read,
  test invocation, and search must name a known development-only file or
  directory explicitly;
- LC4R9 remains limited to the 11-case selection and repair authorization
  frozen before the incident in accepted LC4R8 development-only evidence;
- the implementation worker must use only explicitly named development files,
  the ordinary source generator, and the LC4R8 redacted audit;
- independent review must verify the resulting delta from development evidence
  without protected access;
- protected holdout v1 must not be rerun or used for certification without the
  already-required future explicit reuse policy; a fresh holdout version remains
  the preferable later certification surface.

This incident does not itself authorize holdout reuse, replacement, provider
execution, or any product/runtime change. It must be carried into LC4R9
acceptance and the next user decision surface concerning certification data.
