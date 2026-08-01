# Threat model delta: authenticated Word desktop dialog check

Date: 2026-07-31

Status: `active`

Parent boundaries:

- Reception One Word compact companion shell;
- Word Hybrid contextual launch;
- the platform-blocked Word Online dialog check; and
- EMR4 API Spine read/context and command separation.

## Assets

- the existing installed Word desktop host;
- one new blank document;
- the disposable task-specific manifest;
- the HTTPS loopback taskpane and Diary;
- one authored-synthetic request; and
- the existing closed request and summary envelopes.

## New trust edge

Word desktop hosts the taskpane and Office dialog directly from the trusted
HTTPS loopback origin. This replaces the blocked public-page-to-loopback
Word Online subframe edge and grants no document-content, Office-token,
backend, provider or command authority.

## Threats and controls

### Existing document or account context is exposed

Controls:

- create one new blank document;
- never invoke document-body read or write APIs;
- never inspect account, licence, tenant or Office credential state; and
- retain no filename, document identifier or account identifier.

### Disposable sideload becomes persistent deployment

Controls:

- use the task-specific manifest with a disposable development product id;
- leave the canonical manifest unchanged;
- make no catalogue, tenant or central deployment change; and
- remove the sideload when the check ends.

### Loopback service becomes network-visible

Controls:

- bind only to `127.0.0.1`;
- verify no LAN listener or advertisement;
- use the existing trusted HTTPS certificate; and
- stop the task-owned listener and process tree at cleanup.

### Companion escapes authored-synthetic smoke mode

Controls:

- require both companion and smoke URL flags;
- require `authored_synthetic_client_fixture`;
- reject unexpected backend/provider hosts; and
- retain false patient, appointment, provider, command and write authority.

### Desktop host evidence overclaims online or production readiness

Controls:

- label the Office host as Word desktop and the Diary as local
  authored-synthetic;
- exclude raw request, appointment detail and Office identifiers from durable
  evidence; and
- state explicitly that Word Online remains platform-blocked.

## Closed boundaries

Protected holdouts, historical Diary material, real/product-derived
patient/health/clinical data, Office credentials, provider material, backend
or database access, appointment commands, voice, production, deployment and
release remain excluded.
