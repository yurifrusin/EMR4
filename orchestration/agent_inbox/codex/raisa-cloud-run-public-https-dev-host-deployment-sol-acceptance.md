# Sol acceptance — Raisa Cloud Run public-HTTPS development host deployment

Date: 2026-07-31

Disposition: `accepted_blocked_closeout_pending_user_access_control_decision`

The repository, immutable image and private Sydney service satisfy the frozen
build, identity and runtime controls. The exact runtime identity remains
zero-role and keyless, and no secret, volume, VPC, backend or provider surface
was added.

Acceptance cannot pass because effective Domain Restricted Sharing rejected
the frozen `allUsers` / `roles/run.invoker` binding. No binding was created,
the service remains private, and public route/browser/Word Online evidence
does not exist.

Google's documented alternative is to disable the Cloud Run Invoker IAM check
on the exact service. That is a material access-control choice and requires
Yuri's explicit authority before execution.

Continuity graph revision 178 and Compass map revision 159 validate together.
The focused deployment/Compass suite passes 20 tests and the broader inherited
Word, Reception One and API Spine gate passes 137 tests. Final read-only cloud
observation confirms that the service remains exact and private.
