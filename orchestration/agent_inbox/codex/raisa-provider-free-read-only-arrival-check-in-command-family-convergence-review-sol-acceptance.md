# Sol acceptance — arrival/check-in command-family convergence review

Date: 2026-08-18

Timestamp: 2026-08-18T07:20:15+10:00 (Australia/Brisbane)

Decision: accept

Accepted reviewed source: `3bed3eb32dd1b8723bf5aa6218963b757ebc0e3d`

Result:
`raisa_provider_free_read_only_arrival_check_in_command_family_convergence_review_pass`

The exact candidate proves that dedicated check-in carries materially stronger
domain meaning than bare general-status assignment of `Arrived`. Dedicated
check-in is therefore the future canonical product-facing ordinary arrival
command; general status remains for other transitions, and waiting-area
movement/removal remains separate.

The later first-party cutover must be atomic: both clients move to dedicated
check-in while ordinary product-facing `Arrived` closes in general status. The
present tranche admits none of that runtime work. A5.1 remains default-off,
uncalled and unmodified, with its Rayleen/authored-synthetic gate explicitly
separated from the reusable deterministic kernel.

The deterministic packets and one fresh exact-candidate Gemini 3.7 Flash/high
veto pass. DeepSeek was correctly declined for the coupled review and must be
reassessed for the separable successor extraction. Native subagents remained
declined by developer policy. GPT Sol alone accepts the result and owns
continuity and Git.

The narrowest safe successor is
`raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal`.
It opens no route, practice, provider, product data, UI, deployment or
production authority.
