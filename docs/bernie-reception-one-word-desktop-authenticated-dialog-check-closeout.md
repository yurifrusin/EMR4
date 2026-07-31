# Reception One supervised Word desktop dialog check closeout

Status: **accepted provider-free desktop-host result**
Closed: 2026-07-31
Result: `reception_one_word_desktop_supervised_dialog_check_pass`

## Outcome

The accepted compact companion now passes one real installed-Word desktop
exercise through a disposable HTTPS-loopback sideload.

One task-created blank document loaded the Reception One taskpane. A single
authored-synthetic receptionist request opened the native Diary in the Office
dialog, the Diary retained three detailed synthetic appointment results, and
the deterministic proofreader returned only the generic sentence:
`3 results are ready in the Diary.`

The Office dialog then closed and focus returned to Word. No existing document
was opened or inspected, and the blank document body was neither read nor
written.

## Repository-local repair

The first desktop observation exposed an initialization-order defect rather
than an Office trust or credential problem. The default-off companion mode
configured correctly, but the later `Office.onReady` authentication branch
overwrote it with the ordinary login view when no application token existed.

The repair checks the exact loopback companion capability before the normal
token/login branch, shows only the local app view needed for the companion and
does not call `initApp`. A focused regression test freezes this ordering in
both the source and published taskpane copies.

## Evidence and boundary

Durable evidence records:

- one disposable product identifier distinct from the canonical add-in;
- a schema-valid manifest and `127.0.0.1`-only listener;
- one task-created Word desktop window;
- one authored-synthetic closed request;
- date verification before projection;
- three detailed results retained in the native Diary;
- one exact generic proofreader-admitted Word summary;
- zero provider, credential, backend, database, confirmation, command or
  appointment-write activity; and
- complete sideload, Word-process, listener, development-server and temporary
  file cleanup.

No raw request, screenshot, Office account identifier, credential, document
identifier or appointment detail is retained in the desktop evidence.

## Word Online disposition

This does not revise the preceding Word Online observation. The authenticated
Word Online attempt remains platform-blocked before taskpane execution because
the Microsoft-owned cross-origin editor frame could not navigate to the local
loopback development host under Chromium Local Network Access policy. The
desktop pass is a new descendant, not a reinterpretation of that failed gate.

## Candid limit

This proves one provider-free authored-synthetic exchange in the installed
Word desktop host using a disposable local sideload. It does not prove Office
tenant identity, authenticated Word Online interoperability, live backend
authorization, provider interpretation, representative usability, production
deployment or safety for real, product-derived, patient, health, clinical or
historical data.

Provider use, live product context, voice, appointment writes, production,
deployment and release remain separately gated.
