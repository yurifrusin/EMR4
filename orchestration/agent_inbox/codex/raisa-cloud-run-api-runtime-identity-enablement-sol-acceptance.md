# Sol acceptance — Raisa Cloud Run API and runtime identity

Date: 2026-07-31

Disposition: `accepted`

The exact authorised control-plane tranche passes:

- only `run.googleapis.com` and `artifactregistry.googleapis.com` were enabled;
- only the exact dedicated Raisa runtime service account was created;
- that identity is active, has zero project roles and has no user-managed key;
- the repeated read-only checks now establish that both the frozen Sydney
  Artifact Registry repository and Cloud Run service are absent; and
- no repository, service, image, deployment, public invocation, billing,
  provider, backend, patient-data, production or release action occurred.

The next creation/deployment boundary remains closed pending Yuri's separate
authority.

Continuity graph revision 177 and Compass map revision 158 bind the accepted
result.
