# Native-analysis disposition and Sol source reconciliation

Date: 2026-08-14

Timestamp: 2026-08-14T20:37:05+10:00 (Australia/Brisbane)

Status: `native_outputs_rejected_sol_exact_source_reconciliation_complete`

## Native disposition

Two read-only native packages were dispatched only after a passing five-source
pre-dispatch receipt. Both were stopped and their complete findings are
inadmissible:

- AER-0306 records directory-root filename discovery outside the exact file
  allowlist. No protected path or content appeared in the reported output.
- AER-0307 records a distinct directory-root content search that emitted
  protected-fixture content locally. The complete output is quarantined and no
  substantive conclusion is used.

Neither attempt changed a file, Git ref, runtime, database, provider, external
system or product datum. The sanitized receipts and register revision 268
preserve the incidents without repeating protected content.

## Sol exact-source reconciliation

Sol reconstructed the contract using only exact literal reads of the already-
named non-protected appointment schemas, router, OpenAPI command contract,
focused update/status tests, Diary bridges, API Spine ADR and interaction model.

The exact result is:

1. The existing update family is structurally multi-field and constructs one
   full command from a closed optional patch.
2. Its confirm route locks the appointment, rechecks signed current evidence,
   re-proposes and exact-matches the full command, then applies one update and
   audit within the command transaction.
3. Date, time and duration are directly proven together through successful
   confirmation. Changed practitioner plus time plus duration is structurally
   carried but not directly proven as a successful combined confirmation.
4. Status is a distinct proposal/confirm family, so status plus any update
   field has no current all-or-nothing command.
5. The visible buttons are human presentation controls. Provider and channel
   output may eventually become typed inert candidates only; it may not click,
   confirm, call a route or write.

The actual native lane therefore had negative leverage. Sol owns the durable
architecture and Gemini remains reserved for a fresh exact-candidate veto.
