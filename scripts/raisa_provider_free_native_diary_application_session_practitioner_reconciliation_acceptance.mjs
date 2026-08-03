#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  REJECTION_REASONS,
  admitFixedReadResult,
  createNativeDiaryClientReconciler,
} from '../orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/client-reconciler.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MODULE_PATH = path.join(
  ROOT,
  'orchestration',
  'continuity',
  'raisa-provider-free-native-diary-application-session-practitioner-reconciliation',
  'client-reconciler.mjs',
);
const RESULT = 'provider_free_native_diary_application_session_practitioner_reconciliation_pass';
const EVIDENCE_LABEL = 'provider_free_unmounted_client_state_machine';

function parseOutput(argv) {
  const index = argv.indexOf('--output');
  if (index === -1 || index + 1 >= argv.length || argv[index + 1].startsWith('--')) {
    throw new Error('explicit_output_path_required');
  }
  if (argv.length !== 2) {
    throw new Error('unexpected_arguments');
  }
  return path.resolve(argv[index + 1]);
}

function assert(condition, reason) {
  if (!condition) {
    throw new Error(reason);
  }
}

function expectThrow(fn, message) {
  let thrown = null;
  try {
    fn();
  } catch (error) {
    thrown = error;
  }
  assert(thrown instanceof Error, `expected_throw:${message}`);
  assert(thrown.message === message, `wrong_throw:${message}`);
}

function row(overrides = {}) {
  return {
    id: 'practitioner-authored-0001',
    displayName: 'Avery Authored Synthetic',
    roleLabel: 'GP',
    active: true,
    defaultLocation: {
      id: 'location-authored-0001',
      name: 'Synthetic Clinic',
    },
    ...overrides,
  };
}

function success(rows = [row()]) {
  return { status: 'success', rows };
}

function expectRejected(result, reason) {
  assert(result.ok === false, `expected_rejection:${reason}`);
  assert(result.reason === reason, `wrong_rejection:${reason}`);
}

function runAcceptance() {
  const cases = [];
  const record = (name, fn) => {
    fn();
    cases.push(name);
  };

  record('latest_read_wins_and_late_a_never_renders', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const a = reconciler.beginRead();
    const b = reconciler.beginRead();
    let renders = 0;
    const bResult = reconciler.reconcileAndRender(b, success(), () => { renders += 1; });
    assert(bResult.ok === true && bResult.reason === 'rendered', 'latest_not_rendered');
    expectRejected(
      reconciler.reconcileAndRender(a, success(), () => { renders += 1; }),
      'request_superseded',
    );
    assert(renders === 1, 'late_a_rendered');
    assert(reconciler.snapshot().outstandingTicketCount === 0, 'outstanding_after_latest');
  });

  record('generation_advance_rejects_already_returned_result', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 7 });
    const ticket = reconciler.beginRead();
    const returned = success();
    reconciler.advanceSessionGeneration(8);
    expectRejected(reconciler.reconcileAndRender(ticket, returned, () => {}), 'session_generation_stale');
  });

  record('newer_read_rejects_already_returned_result', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const oldTicket = reconciler.beginRead();
    const returned = success();
    reconciler.beginRead();
    expectRejected(reconciler.reconcileAndRender(oldTicket, returned, () => {}), 'request_superseded');
  });

  record('invalidation_rejects_before_render_and_blocks_new_read', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const ticket = reconciler.beginRead();
    reconciler.invalidateSession();
    let rendered = false;
    expectRejected(reconciler.reconcileAndRender(ticket, success(), () => { rendered = true; }), 'session_inactive');
    assert(rendered === false, 'invalidated_rendered');
    expectThrow(() => reconciler.beginRead(), 'session_inactive');
  });

  record('latest_current_renders_once_then_replay_rejected', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 2 });
    const ticket = reconciler.beginRead();
    let renders = 0;
    assert(reconciler.reconcileAndRender(ticket, success(), () => { renders += 1; }).ok, 'first_render_failed');
    expectRejected(reconciler.reconcileAndRender(ticket, success(), () => { renders += 1; }), 'ticket_replayed');
    assert(renders === 1, 'ticket_rendered_twice');
  });

  record('ticket_is_frozen_and_exact', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 3 });
    const ticket = reconciler.beginRead();
    assert(Object.isFrozen(ticket), 'ticket_not_frozen');
    assert(JSON.stringify(Object.keys(ticket).sort()) === JSON.stringify(['requestRevision', 'sessionGeneration']), 'ticket_shape');
  });

  record('forged_cross_instance_and_malformed_tickets_rejected', () => {
    const one = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const two = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const ticket = one.beginRead();
    const forged = Object.freeze({ sessionGeneration: 1, requestRevision: 1 });
    expectRejected(one.reconcileAndRender(forged, success(), () => {}), 'ticket_unknown');
    expectRejected(two.reconcileAndRender(ticket, success(), () => {}), 'ticket_unknown');
    expectRejected(one.reconcileAndRender(null, success(), () => {}), 'ticket_unknown');
    expectRejected(one.reconcileAndRender('ticket', success(), () => {}), 'ticket_unknown');
  });

  record('invalid_generation_values_fail_without_state_change', () => {
    const invalidValues = [1, 0, -1, 1.5, Number.NaN, Number.POSITIVE_INFINITY, '2', null];
    for (const value of invalidValues) {
      const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
      const ticket = reconciler.beginRead();
      expectThrow(() => reconciler.advanceSessionGeneration(value), 'invalid_generation_advance');
      assert(reconciler.snapshot().sessionGeneration === 1, 'invalid_generation_changed_state');
      assert(reconciler.reconcileAndRender(ticket, success(), () => {}).ok, 'invalid_generation_consumed_ticket');
    }
  });

  record('invalid_initial_generation_values_fail_closed', () => {
    for (const value of [undefined, 0, -1, 1.5, Number.NaN, '1']) {
      expectThrow(
        () => createNativeDiaryClientReconciler({ initialSessionGeneration: value }),
        'invalid_initial_session_generation',
      );
    }
  });

  record('strict_response_admission', () => {
    assert(admitFixedReadResult(success()).ok === true, 'valid_result_rejected');
    assert(admitFixedReadResult(success([row({ roleLabel: null, defaultLocation: null })])).ok === true, 'nullable_projection_rejected');
    const bad = [
      null,
      [],
      { status: 'failure', rows: [] },
      { status: 'success', rows: {}, },
      { status: 'success', rows: [], authority: true },
      success([row({ secret: 'forbidden' })]),
      success([row({ id: '' })]),
      success([row({ displayName: '' })]),
      success([row({ roleLabel: '' })]),
      success([row({ active: false })]),
      success([row({ defaultLocation: { id: 'x', name: 'y', authority: true } })]),
      success([row({ defaultLocation: { id: '', name: 'Synthetic Clinic' } })]),
    ];
    for (const value of bad) {
      assert(admitFixedReadResult(value).ok === false, 'malformed_result_admitted');
    }
  });

  record('inadmissible_result_consumes_ticket_without_render', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const ticket = reconciler.beginRead();
    let renders = 0;
    expectRejected(
      reconciler.reconcileAndRender(ticket, { status: 'success', rows: [], session: 'forbidden' }, () => { renders += 1; }),
      'response_not_admissible',
    );
    expectRejected(reconciler.reconcileAndRender(ticket, success(), () => { renders += 1; }), 'ticket_replayed');
    assert(renders === 0, 'inadmissible_rendered');
  });

  record('callback_exception_still_consumes_ticket', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const ticket = reconciler.beginRead();
    expectThrow(
      () => reconciler.reconcileAndRender(ticket, success(), () => { throw new Error('synthetic_render_failure'); }),
      'synthetic_render_failure',
    );
    expectRejected(reconciler.reconcileAndRender(ticket, success(), () => {}), 'ticket_replayed');
    const snapshot = reconciler.snapshot();
    assert(snapshot.renderCallbackExceptionCount === 1, 'callback_exception_not_counted');
    assert(snapshot.totalRenders === 1, 'render_attempt_not_counted');
  });

  record('snapshot_is_bounded_and_contains_no_rows_or_identity_values', () => {
    const reconciler = createNativeDiaryClientReconciler({ initialSessionGeneration: 9 });
    const ticket = reconciler.beginRead();
    reconciler.reconcileAndRender(ticket, success(), () => {});
    const snapshot = reconciler.snapshot();
    assert(Object.keys(snapshot).length === 9, 'snapshot_shape_drift');
    assert(Object.keys(snapshot.rejectionCounts).sort().join('|') === [...REJECTION_REASONS].sort().join('|'), 'rejection_reason_drift');
    const serialized = JSON.stringify(snapshot);
    for (const forbidden of ['Avery', 'Synthetic Clinic', 'practitioner-authored', 'location-authored', 'cookie', 'csrf', 'principal', 'practice']) {
      assert(!serialized.includes(forbidden), `snapshot_leak:${forbidden}`);
    }
  });

  record('module_has_no_product_or_external_effect_dependency', () => {
    const source = fs.readFileSync(MODULE_PATH, 'utf8');
    assert(!/^\s*import\s/m.test(source), 'module_import_present');
    for (const pattern of [
      /\bfetch\s*\(/,
      /XMLHttpRequest/,
      /\bdocument\s*\./,
      /\bwindow\s*\./,
      /\blocalStorage\b/,
      /\bsessionStorage\b/,
      /\bWebSocket\b/,
      /\bEventSource\b/,
      /\bindexedDB\b/,
    ]) {
      assert(!pattern.test(source), `forbidden_dependency:${pattern}`);
    }
  });

  return cases;
}

function main() {
  const outputPath = parseOutput(process.argv.slice(2));
  const cases = runAcceptance();
  const source = fs.readFileSync(MODULE_PATH);
  const evidence = {
    schema_version: 'emr4.native_diary_practitioner_reconciliation_evidence.v1',
    result: RESULT,
    evidence_label: EVIDENCE_LABEL,
    data_class: 'authored_synthetic',
    case_count: cases.length,
    passed_case_count: cases.length,
    failed_case_count: 0,
    rejection_reason_count: REJECTION_REASONS.length,
    properties: {
      latest_read_wins: true,
      stale_generation_rejected_before_render: true,
      superseded_request_rejected_before_render: true,
      invalidated_session_rejected_before_render: true,
      foreign_and_replayed_ticket_rejected: true,
      strict_fixed_read_shape: true,
      response_rows_retained: false,
      client_generation_is_server_bound_proof: false,
      provider_or_external_effect: false,
    },
    claims_not_made: [
      'live',
      'browser',
      'route_intercepted',
      'http',
      'backend',
      'postgresql',
      'mounted_runtime',
      'usability',
    ],
    client_reconciler_sha256: crypto
      .createHash('sha256')
      .update(source.toString('utf8').replace(/\r\n/g, '\n'), 'utf8')
      .digest('hex'),
  };
  const serialized = `${JSON.stringify(evidence, null, 2)}\n`;
  for (const forbidden of ['Avery', 'Synthetic Clinic', 'practitioner-authored', 'location-authored']) {
    assert(!serialized.includes(forbidden), `evidence_leak:${forbidden}`);
  }
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, serialized, { encoding: 'utf8', flag: 'w' });
  process.stdout.write(`${JSON.stringify(evidence)}\n`);
}

main();
