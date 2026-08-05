import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

import {
  admitRayleenWaitingRoomResponse,
  assertRayleenWaitingRoomBootstrap,
  createRayleenWaitingRoomProjection,
} from '../docs/diary/rayleen-waiting-room-projection.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MODULE_PATH = path.join(
  ROOT,
  'docs',
  'diary',
  'rayleen-waiting-room-projection.mjs',
);
const LOCATION_ID = '33333333-3333-4333-8333-333333333333';
const PRACTICE_ID = '11111111-1111-4111-8111-111111111111';
const APPOINTMENT_ID = '44444444-4444-4444-8444-444444444444';
const PRACTITIONER_ID = '55555555-5555-4555-8555-555555555555';

function label() {
  return {
    sourceIds: [`backend:appointment:${APPOINTMENT_ID}`],
    integrityPrincipals: ['backend_truth'],
    confidentialityReaders: ['authorized_reception_surface'],
    observedAt: '2099-08-05T02:00:00Z',
    expiresAt: '2099-08-05T02:02:00Z',
    freshnessState: 'fresh',
    authorityCeiling: 'data_only',
  };
}

function responseFixture(overrides = {}) {
  const frame = {
    schemaVersion: 'emr4.waiting_room_context_frame.v1',
    frameId: '22222222-2222-4222-8222-222222222222',
    practiceId: PRACTICE_ID,
    locationId: LOCATION_ID,
    contextRevision: 7,
    generatedAt: '2099-08-05T02:00:00Z',
    expiresAt: '2099-08-05T02:02:00Z',
    reader: 'authorized_reception_surface',
    excludedFieldClasses: [
      'contact_details',
      'national_identifiers',
      'clinical_text',
      'appointment_notes',
      'unrestricted_history',
      'credentials',
      'raw_provider_data',
    ],
    projection: {
      kind: 'FULL_QUEUE',
      selectedCount: 1,
      practitionerId: null,
      waitingAreaId: null,
      focusAppointmentId: null,
      selectorProvenance: 'deterministic_product_read',
      authorityCeiling: 'data_only',
      writesAuthorized: false,
    },
    backendFacts: [{
      appointmentId: APPOINTMENT_ID,
      patientDisplayToken: 'synthetic:patient-44a4c0de1234',
      practitionerId: PRACTITIONER_ID,
      status: 'arrived',
      scheduledAt: '2099-08-05T01:15:00Z',
      waitingAreaId: null,
      arrivedAt: '2099-08-05T01:20:00Z',
      label: label(),
    }],
    derivedSignals: [{
      kind: 'elapsed_wait_minutes',
      appointmentId: APPOINTMENT_ID,
      integerValue: 40,
      textValue: null,
      booleanValue: null,
      derivedBy: 'deterministic_projection_engine',
      label: label(),
    }],
    ...overrides,
  };
  return { data: { rayleenWaitingRoom: frame } };
}

function requestFixture() {
  return {
    locationId: LOCATION_ID,
    projectionKind: 'FULL_QUEUE',
    practitionerId: null,
    waitingAreaId: null,
    focusAppointmentId: null,
  };
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function check(name, condition) {
  if (!condition) throw new Error(`case_failed:${name}`);
  return { name, passed: true };
}

async function run() {
  const cases = [];
  const admission = admitRayleenWaitingRoomResponse(responseFixture(), {
    expectedLocationId: LOCATION_ID,
    expectedPracticeId: PRACTICE_ID,
    now: Date.parse('2099-08-05T02:01:00Z'),
  });
  cases.push(check('closed_response_admitted', admission.ok === true));
  cases.push(check('released_frame_frozen', Object.isFrozen(admission.frame)));

  const extra = responseFixture({ unexpectedAuthority: true });
  cases.push(check(
    'unknown_field_rejected',
    admitRayleenWaitingRoomResponse(extra, {
      expectedLocationId: LOCATION_ID,
      expectedPracticeId: PRACTICE_ID,
      now: Date.parse('2099-08-05T02:01:00Z'),
    }).ok === false,
  ));
  cases.push(check(
    'expired_frame_rejected',
    admitRayleenWaitingRoomResponse(responseFixture(), {
      expectedLocationId: LOCATION_ID,
      expectedPracticeId: PRACTICE_ID,
      now: Date.parse('2099-08-05T02:03:00Z'),
    }).ok === false,
  ));
  cases.push(check(
    'foreign_location_rejected',
    admitRayleenWaitingRoomResponse(responseFixture(), {
      expectedLocationId: '66666666-6666-4666-8666-666666666666',
      expectedPracticeId: PRACTICE_ID,
      now: Date.parse('2099-08-05T02:01:00Z'),
    }).ok === false,
  ));

  let invalidBootstrapRejected = false;
  try {
    assertRayleenWaitingRoomBootstrap({
      enabled: true,
      practiceId: PRACTICE_ID,
      readFixedWaitingRoom: async () => responseFixture(),
      sessionGeneration: 1,
      authority: true,
    });
  } catch (error) {
    invalidBootstrapRejected = error.message === 'rayleen_waiting_room_bootstrap_invalid';
  }
  cases.push(check('authority_bearing_bootstrap_rejected', invalidBootstrapRejected));

  const reads = [deferred(), deferred()];
  let readIndex = 0;
  const projection = createRayleenWaitingRoomProjection({
    enabled: true,
    practiceId: PRACTICE_ID,
    sessionGeneration: 1,
    readFixedWaitingRoom: async () => reads[readIndex++].promise,
  });
  const rendered = [];
  const first = projection.readAndRender(
    requestFixture(),
    (frame) => rendered.push(frame),
    () => {},
    () => {},
  );
  const second = projection.readAndRender(
    requestFixture(),
    (frame) => rendered.push(frame),
    () => {},
    () => {},
  );
  reads[1].resolve(responseFixture());
  const secondResult = await second;
  reads[0].resolve(responseFixture());
  const firstResult = await first;
  cases.push(check(
    'latest_read_wins',
    secondResult.ok === true
      && firstResult.ok === false
      && ['request_interrupted', 'request_superseded'].includes(firstResult.reason)
      && rendered.length === 1,
  ));

  const pending = deferred();
  const interruptedProjection = createRayleenWaitingRoomProjection({
    enabled: true,
    practiceId: PRACTICE_ID,
    sessionGeneration: 4,
    readFixedWaitingRoom: async () => pending.promise,
  });
  let interruptedRender = false;
  const interrupted = interruptedProjection.readAndRender(
    requestFixture(),
    () => { interruptedRender = true; },
    () => {},
    () => {},
  );
  interruptedProjection.invalidateSession();
  pending.resolve(responseFixture());
  const interruptedResult = await interrupted;
  cases.push(check(
    'invalidation_suppresses_release',
    interruptedResult.ok === false && interruptedRender === false,
  ));

  const expiryProjection = createRayleenWaitingRoomProjection({
    enabled: true,
    practiceId: PRACTICE_ID,
    sessionGeneration: 8,
    readFixedWaitingRoom: async () => responseFixture({
      generatedAt: new Date(Date.now() - 1000).toISOString(),
      expiresAt: new Date(Date.now() + 25).toISOString(),
    }),
  });
  let expiryCleared = false;
  let expiryWarningShown = false;
  const expiryResult = await expiryProjection.readAndRender(
    requestFixture(),
    () => {},
    () => { expiryCleared = true; },
    () => { expiryWarningShown = true; },
  );
  await new Promise((resolve) => setTimeout(resolve, 40));
  cases.push(check(
    'rendered_frame_expires_and_clears',
    expiryResult.ok === true && expiryCleared === true,
  ));
  cases.push(check(
    'pre_expiry_warning_is_emitted',
    expiryWarningShown === true,
  ));
  expiryProjection.invalidateSession();

  const source = fs.readFileSync(MODULE_PATH, 'utf8');
  const forbidden = [
    /\bfetch\s*\(/,
    /XMLHttpRequest/,
    /\bdocument\s*\./,
    /\bwindow\s*\./,
    /\blocalStorage\b/,
    /\bsessionStorage\b/,
    /\bWebSocket\b/,
    /\bEventSource\b/,
    /\bindexedDB\b/,
  ];
  cases.push(check(
    'module_has_no_direct_effectful_surface',
    forbidden.every((pattern) => !pattern.test(source)),
  ));

  return {
    schema_version: 'emr4.model_required_bureau_a4.ui_acceptance.v1',
    result: 'provider_free_rayleen_a4_ui_state_machine_pass',
    evidence_label: 'provider_free_default_off_product_read_ui_state_machine',
    data_class: 'authored_synthetic',
    case_count: cases.length,
    passed_case_count: cases.filter((item) => item.passed).length,
    failed_case_count: cases.filter((item) => !item.passed).length,
    cases,
    properties: {
      strict_true_default_off: true,
      latest_read_wins: true,
      interruption_suppresses_release: true,
      response_schema_closed: true,
      provider_or_external_effect: false,
      command_or_write_authority: false,
      browser_or_backend_claim: false,
    },
    module_sha256: crypto.createHash('sha256').update(source).digest('hex'),
  };
}

const outputIndex = process.argv.indexOf('--output');
if (outputIndex === -1 || !process.argv[outputIndex + 1]) {
  throw new Error('explicit_output_path_required');
}
const output = path.resolve(process.argv[outputIndex + 1]);
const evidence = await run();
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
process.stdout.write(`${JSON.stringify(evidence)}\n`);
