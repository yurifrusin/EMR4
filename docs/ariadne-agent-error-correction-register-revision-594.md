# Ariadne agent error and correction register — revision 594

<!-- ariadne-agent-error-register-reading
revision: 594
incident_count: 814
new_incident_ids: AER-0810,AER-0811,AER-0812,AER-0813,AER-0814
open_incident_count: 0
-->

This revision note binds five contained readiness-workflow observations to the
prospective clockwork-projected register. The canonical JSON register and
pattern report remain clockwork-owned.

## AER-0810

Two read-only PowerShell inventory commands placed a pipe immediately after a
`foreach` expression's closing brace. PowerShell rejected each as an empty
pipeline element before producing output or changing state. The corrected form
assigns the expression to a rows variable and pipes that variable separately.

## AER-0811

The first process-free source audit embedded the exact forbidden strings it was
searching for, so the focused packet failed on its own guard. The first
correction fragmented the launcher/provider strings but missed the equivalent
`subprocess.run` count token, causing one further fail-closed focused run. All
scanned tokens are now constructed from fragments and the final 9-test packet
passes with zero process or provider activity.

## AER-0812

The first widened startup-lineage packet included two immutable
controller-convergence equality selectors that bind the controller before the
accepted relative-specifier and sentinel-source repairs. Those two selectors
failed on only that expected old digest. The exact applicability boundary is
now frozen; the repaired current gate directly binds the new controller and all
repair artifacts, and the other 75 tests pass.

## AER-0813

The first read-only clockwork closeout check represented the exact successor
authority opening as a free string. The continuity graph requires a typed
boundary-and-source object. The check rejected at `tick_transaction_prepare`
with zero publication and no canonical change. The rejected receipt is
preserved and the corrected intent uses the schema's boundary, repository
source and exact one-attempt scope fields.

## AER-0814

The second read-only clockwork check accepted the typed object shape but
rejected the newly coined boundary identifier because authority openings use
the live graph's closed vocabulary. Again, publication remained zero. The
corrected intent binds the exact successor to the established `model-runtime`
and `provider-call` boundaries with one-attempt/no-retry scopes, and both
rejected checks remain preserved.
