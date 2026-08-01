# Reception One Yuri-only internal walkthrough findings

Date: 2026-07-29

Result: `reception_one_yuri_internal_walkthrough_completed_promising_needs_revision`

Evidence class: `single_owner_internal_product_critique`

## Result

Yuri completed all eight authored-synthetic tasks in 28 minutes 35 seconds.
Five tasks worked and three partly worked; none failed or were skipped. Five
tasks rated Reception One better than the ordinary Diary and three were not
compared. This is encouraging internal product evidence, not representative
usability evidence.

The final disposition is:

- overall value: `promising_needs_revision`;
- design-partner readiness: `not_ready`;
- foreground projection: `concern`;
- date-first page movement: `concern`;
- Bureau workflow: `supports`; and
- text before push-to-talk: `not_assessed`.

## Preserve

The technical Bureau direction is the strongest part of the present product.
The combined availability flow successfully moved from relevant candidate
times to a visibly proposed slot in the ordinary Diary without claiming that a
booking had occurred. Yuri described that complete flow as impressive.

This supports retaining:

- natural-language intent as the entry point;
- a typed, bounded interpretation before product rendering;
- deterministic proofreader and proposal boundaries;
- fresh Diary-backed availability; and
- the proposal returning visibly to the authoritative Diary.

## Revise before a design partner

### Keep the Diary psychologically present

The current full-window Reception One projection replaces the Diary and breaks
the user's spatial connection to it. It also allocates a large maximised
surface to comparatively little information. The projection should become a
modeless, content-sized foreground window over the still-visible Diary, with
bounded adaptive sizing.

### Make return and closure obvious

`back_path_unclear` and `diary_context_lost` were each selected three times.
Escape and the custom return control worked but were not immediately
discoverable, while browser navigation was disabled and closing Reception One
appeared to require closing the whole browser. The foreground projection needs
an ordinary close control, an explicit readable return affordance and
deterministic focus restoration to the underlying Diary.

### Realise date-first choreography

The walkthrough opened the ordinary Diary on the actual calendar date,
Wednesday 29 July, with zero appointments even though the frozen reference day
was Monday 27 July. Yuri had to select the reference day manually. The launcher
and product transition must make the underlying Diary navigate to and verify
the intended date before the projection appears.

### Replace technical language with conversation

`wording_too_technical` was selected three times, including for the identity
ambiguity task. State and clarification language should sound like an
experienced receptionist colleague: brief, direct and conversational.
Technical provenance and policy terminology should remain in audit evidence,
not dominate the product surface.

### Add restrained visual character

The flow worked but felt bland. The next visual pass should strengthen spatial
hierarchy, transition, focus and Bureau character without increasing density
or decorative noise.

### Stop calling the Diary a grid

`Grid` may remain an internal architectural term where useful, but it should
not appear in the final receptionist-facing interface. User-facing language
should say `Diary`, `full Diary` or describe the relevant focused view.

## Product decision

Do not invite the design partner or broader representative receptionist cohort
yet. First implement and verify the provider-free integrated Bureau baseline:

1. open the authored-synthetic Diary on the correct reference day;
2. move to a requested day before projection;
3. render a content-sized modeless foreground projection over the Diary;
4. make close, return and focus restoration obvious;
5. replace technical/legalistic product language with conversational copy;
6. retain typed proofreader and proposal-only boundaries; and
7. improve visual character without sacrificing calmness.

Only after that baseline passes should Yuri decide whether to authorise one
bounded model-connected text lane and a design-partner session.

## Evidence limits

This result contains one informed owner's internal critique over
authored-synthetic fixtures. It proves neither representative receptionist
usability nor a threshold, voice quality, model interpretation, production
fitness or safety with real/product-derived data. No provider, appointment
write, credential, recording, deployment or release path was used. After Yuri
stopped the runner, an independent residue check confirmed that the owned
Python processes, loopback listeners and disposable database were absent; the
disconnected user browser tab was deliberately preserved.
