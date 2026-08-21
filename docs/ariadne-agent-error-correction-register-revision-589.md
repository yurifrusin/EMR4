# Ariadne agent error and correction register — revision 589

<!-- ariadne-agent-error-register-reading
revision: 589
incident_count: 790
new_incident_ids: AER-0788,AER-0789,AER-0790
open_incident_count: 0
-->

This revision note binds three contained observations to the clockwork-projected register. The canonical JSON register and pattern report remain clockwork-owned.

## AER-0788

The repaired sentinel author used an ordinary Python bytes literal for JavaScript containing single-escaped carriage-return and newline spellings. Python translated them into raw line terminators, making the generated module lexically invalid before activation. The provider-free AST/lexical diagnosis identifies and contains the coordinate; a separately frozen source-only repair is required.

## AER-0789

The first diagnosis acceptance predicate counted the three deliberately scrubbed credential-environment names as prohibited provider activity. The focused test rejected the evidence, and the predicate now checks an explicit allowlist of fields that must be zero while preserving the scrub count as positive safety evidence.

## AER-0790

An unvalidated pre-verifier draft expanded the visible abbreviated candidate ID with guessed suffix characters. Before preflight or publication, Git resolved the exact 40-character commit, the guessed value was discarded, and the final Git-evidence narrative was made object-ID-free so the machine snapshot remained the sole binding.
