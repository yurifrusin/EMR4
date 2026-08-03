#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

import {
  assertApplicationSessionPractitionerBootstrap,
  createApplicationSessionPractitionerDirectory,
  isApplicationSessionPractitionerDirectoryEnabled,
} from '../docs/diary/application-session-practitioner-directory.mjs';
import {
  createNativeDiaryClientReconciler,
} from '../docs/diary/application-session-practitioner-reconciler.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE_HEAD = 'e7d209e6652106c8f69036460223259a33af19c9';
const RESULT = 'provider_free_native_diary_application_session_ui_composition_pass';
const EVIDENCE_LABEL = 'provider_free_default_off_ui_composition_harness';
const CANONICAL_RECONCILER = path.join(
  ROOT,
  'orchestration',
  'continuity',
  'raisa-provider-free-native-diary-application-session-practitioner-reconciliation',
  'client-reconciler.mjs',
);
const PUBLISHED_RECONCILER = path.join(
  ROOT,
  'docs',
  'diary',
  'application-session-practitioner-reconciler.mjs',
);
const COMPOSITION_MODULE = path.join(
  ROOT,
  'docs',
  'diary',
  'application-session-practitioner-directory.mjs',
);
const DIARY_JS = path.join(ROOT, 'docs', 'diary', 'diary.js');

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
  if (!condition) throw new Error(reason);
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

async function expectAsyncThrow(fn, message) {
  let thrown = null;
  try {
    await fn();
  } catch (error) {
    thrown = error;
  }
  assert(thrown instanceof Error, `expected_async_throw:${message}`);
  assert(thrown.message === message, `wrong_async_throw:${message}`);
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

function row(overrides = {}) {
  return {
    id: 'practitioner-authored-0001',
    displayName: 'Avery Authored Synthetic',
    roleLabel: 'GP',
    active: true,
    defaultLocation: { id: 'location-authored-0001', name: 'Synthetic Clinic' },
    ...overrides,
  };
}

function success(rows = [row()]) {
  return { status: 'success', rows };
}

function bootstrap(reader, generation = 1, overrides = {}) {
  return {
    enabled: true,
    readFixedPractitionerDirectory: reader,
    sessionGeneration: generation,
    ...overrides,
  };
}

function canonicalLf(buffer) {
  return buffer.toString('utf8').replace(/\r\n/g, '\n');
}

function extractFunction(source, name) {
  const functionStart = source.indexOf(`function ${name}(`);
  assert(functionStart >= 0, `missing_function:${name}`);
  const start = source.slice(Math.max(0, functionStart - 6), functionStart) === 'async '
    ? functionStart - 6
    : functionStart;
  const open = source.indexOf('{', start);
  let depth = 0;
  for (let index = open; index < source.length; index += 1) {
    if (source[index] === '{') depth += 1;
    if (source[index] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`unterminated_function:${name}`);
}

async function runAcceptance() {
  const cases = [];
  const record = async (name, fn) => {
    await fn();
    cases.push(name);
  };

  await record('published_reconciler_matches_canonical_lf_bytes', () => {
    const canonical = canonicalLf(fs.readFileSync(CANONICAL_RECONCILER));
    const published = canonicalLf(fs.readFileSync(PUBLISHED_RECONCILER));
    assert(published === canonical, 'published_reconciler_drift');
  });

  await record('only_exact_boolean_true_enables', () => {
    for (const value of [undefined, null, false, true, 'true', 1, [], {}, { enabled: false }, { enabled: 'true' }]) {
      assert(isApplicationSessionPractitionerDirectoryEnabled(value) === false, 'non_strict_enablement');
    }
    assert(isApplicationSessionPractitionerDirectoryEnabled({ enabled: true }) === true, 'strict_true_not_enabled');
  });

  await record('enabled_incomplete_and_authority_bearing_bootstrap_fail_before_read', () => {
    let reads = 0;
    const reader = () => { reads += 1; return success(); };
    for (const value of [
      { enabled: true },
      { enabled: true, readFixedPractitionerDirectory: reader },
      { enabled: true, readFixedPractitionerDirectory: 'reader', sessionGeneration: 1 },
      { enabled: true, readFixedPractitionerDirectory: reader, sessionGeneration: 0 },
      bootstrap(reader, 1, { token: 'forbidden' }),
      bootstrap(reader, 1, { practice: 'forbidden' }),
      bootstrap(reader, 1, { query: 'forbidden' }),
    ]) {
      expectThrow(
        () => assertApplicationSessionPractitionerBootstrap(value),
        'application_session_practitioner_directory_bootstrap_invalid',
      );
    }
    assert(reads === 0, 'invalid_bootstrap_invoked_reader');
  });

  await record('exact_reader_receives_no_argument_and_only_reconciled_rows_render', async () => {
    let argumentCount = -1;
    const composition = createApplicationSessionPractitionerDirectory(
      bootstrap(function reader() {
        argumentCount = arguments.length;
        return success();
      }),
    );
    let rendered = null;
    const result = await composition.readAndRender((rows) => { rendered = rows; });
    assert(result.ok === true && result.reason === 'rendered', 'exact_read_not_rendered');
    assert(argumentCount === 0, 'reader_received_argument');
    assert(Array.isArray(rendered) && rendered.length === 1, 'rows_not_egressed');
  });

  await record('latest_read_wins', async () => {
    const first = deferred();
    const second = deferred();
    let reads = 0;
    const composition = createApplicationSessionPractitionerDirectory(
      bootstrap(() => {
        reads += 1;
        return reads === 1 ? first.promise : second.promise;
      }),
    );
    let renders = 0;
    const a = composition.readAndRender(() => { renders += 1; });
    const b = composition.readAndRender(() => { renders += 1; });
    second.resolve(success());
    const bResult = await b;
    first.resolve(success());
    const aResult = await a;
    assert(bResult.ok === true, 'latest_read_rejected');
    assert(aResult.ok === false && aResult.reason === 'request_superseded', 'older_read_admitted');
    assert(renders === 1, 'superseded_rendered');
  });

  await record('generation_advance_suppresses_outstanding_and_is_strict', async () => {
    const pending = deferred();
    const composition = createApplicationSessionPractitionerDirectory(
      bootstrap(() => pending.promise, 4),
    );
    const read = composition.readAndRender(() => { throw new Error('stale_rendered'); });
    assert(composition.advanceSessionGeneration(5) === true, 'advance_failed');
    expectThrow(() => composition.advanceSessionGeneration(5), 'invalid_generation_advance');
    expectThrow(() => composition.advanceSessionGeneration(3), 'invalid_generation_advance');
    pending.resolve(success());
    const result = await read;
    assert(result.ok === false && result.reason === 'session_generation_stale', 'stale_generation_admitted');
  });

  await record('invalidation_suppresses_outstanding_and_new_reads', async () => {
    const pending = deferred();
    const composition = createApplicationSessionPractitionerDirectory(
      bootstrap(() => pending.promise),
    );
    const read = composition.readAndRender(() => { throw new Error('invalidated_rendered'); });
    composition.invalidateSession();
    pending.resolve(success());
    const result = await read;
    assert(result.ok === false && result.reason === 'session_inactive', 'invalidated_admitted');
    await expectAsyncThrow(
      () => composition.readAndRender(() => {}),
      'session_inactive',
    );
  });

  await record('reader_failure_is_consumed_and_sanitized', async () => {
    const composition = createApplicationSessionPractitionerDirectory(
      bootstrap(() => { throw new Error('secret_transport_detail'); }),
    );
    const result = await composition.readAndRender(() => { throw new Error('failed_read_rendered'); });
    assert(result.ok === false && result.reason === 'fixed_read_failed', 'reader_failure_not_sanitized');
    const snapshot = composition.snapshot();
    assert(snapshot.outstandingTicketCount === 0, 'reader_failure_ticket_pending');
    assert(JSON.stringify(snapshot).includes('secret_transport_detail') === false, 'reader_error_leaked');
  });

  await record('malformed_and_authority_bearing_results_are_suppressed', async () => {
    for (const returned of [
      null,
      { status: 'success', rows: [], session: 'forbidden' },
      success([row({ authority: true })]),
      success([row({ active: false })]),
    ]) {
      const composition = createApplicationSessionPractitionerDirectory(
        bootstrap(() => returned),
      );
      let rendered = false;
      const result = await composition.readAndRender(() => { rendered = true; });
      assert(result.ok === false && result.reason === 'response_not_admissible', 'bad_result_admitted');
      assert(rendered === false, 'bad_result_rendered');
    }
  });

  await record('replay_and_foreign_ticket_are_suppressed_by_published_reconciler', () => {
    const one = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const two = createNativeDiaryClientReconciler({ initialSessionGeneration: 1 });
    const ticket = one.beginRead();
    assert(one.reconcileAndRender(ticket, success(), () => {}).ok === true, 'first_render_failed');
    assert(one.reconcileAndRender(ticket, success(), () => {}).reason === 'ticket_replayed', 'replay_admitted');
    assert(two.reconcileAndRender(ticket, success(), () => {}).reason === 'ticket_unknown', 'foreign_ticket_admitted');
  });

  await record('callback_failure_consumes_ticket', async () => {
    const composition = createApplicationSessionPractitionerDirectory(bootstrap(() => success()));
    await expectAsyncThrow(
      () => composition.readAndRender(() => { throw new Error('synthetic_render_failure'); }),
      'synthetic_render_failure',
    );
    const snapshot = composition.snapshot();
    assert(snapshot.outstandingTicketCount === 0, 'callback_failure_ticket_pending');
    assert(snapshot.renderCallbackExceptionCount === 1, 'callback_failure_not_counted');
  });

  await record('snapshot_is_sanitized_and_immutable', async () => {
    const reader = () => success();
    const composition = createApplicationSessionPractitionerDirectory(bootstrap(reader, 9));
    await composition.readAndRender(() => {});
    const snapshot = composition.snapshot();
    assert(Object.isFrozen(snapshot) && Object.isFrozen(snapshot.rejectionCounts), 'snapshot_mutable');
    const serialized = JSON.stringify(snapshot);
    for (const forbidden of ['Avery', 'Synthetic Clinic', 'practitioner-authored', 'reader', 'cookie', 'csrf', 'token', 'principal', 'practice', 'authority']) {
      assert(!serialized.toLowerCase().includes(forbidden.toLowerCase()), `snapshot_leak:${forbidden}`);
    }
  });

  await record('cached_composition_reset_suppresses_invalid_transitions', async () => {
    const diarySource = fs.readFileSync(DIARY_JS, 'utf8').replace(/\r\n/g, '\n');
    const getBootstrap = extractFunction(
      diarySource,
      'getApplicationSessionPractitionerBootstrap',
    );
    const isEnabled = extractFunction(
      diarySource,
      'isApplicationSessionPractitionerBootstrapEnabled',
    );
    const resetHelper = extractFunction(
      diarySource,
      'invalidateAndResetApplicationSessionPractitionerDirectory',
    );
    const createFailure = extractFunction(
      diarySource,
      'createApplicationSessionPractitionerFailure',
    );
    const loadDirectory = extractFunction(diarySource, 'loadPractitionerDirectory');
    const originalReader = () => {};
    const transitions = [
      { name: 'disabled', bootstrapValue: { enabled: false }, rejects: false },
      { name: 'malformed', bootstrapValue: { enabled: true }, rejects: true },
      {
        name: 'reader_changed',
        bootstrapValue: bootstrap(() => success()),
        rejects: true,
      },
    ];
    for (const transition of transitions) {
      const pending = deferred();
      const composition = createApplicationSessionPractitionerDirectory(
        bootstrap(() => pending.promise),
      );
      const outstanding = composition.readAndRender(() => {
        throw new Error(`rendered_after_${transition}`);
      });
      const context = {
        injectedComposition: composition,
        injectedReader: originalReader,
        injectedBootstrap: transition.bootstrapValue,
        APPLICATION_SESSION_PRACTITIONER_BOOTSTRAP_GLOBAL:
          '__EMR4_NATIVE_DIARY_APPLICATION_SESSION_PRACTITIONERS__',
        APPLICATION_SESSION_PRACTITIONER_FAILURE:
          'application_session_practitioner_directory_failure',
        ENABLE_GRAPHQL_PRACTITIONERS: false,
        window: {
          __EMR4_NATIVE_DIARY_APPLICATION_SESSION_PRACTITIONERS__:
            transition.bootstrapValue,
        },
        fetchPractitionerDirectoryRest: async () => [],
        fetchPractitionerDirectoryGraphql: async () => ({
          rows: [], attempted: true, fallback: false,
        }),
        loadApplicationSessionPractitionerDirectory: async (candidate) => {
          assertApplicationSessionPractitionerBootstrap(candidate);
          if (candidate.readFixedPractitionerDirectory !== originalReader) {
            throw new Error('application_session_practitioner_reader_changed');
          }
          return [];
        },
        resetState: null,
        transitionResult: null,
        transitionError: null,
      };
      await vm.runInNewContext(`(async () => {
        let applicationSessionPractitionerDirectory = injectedComposition;
        let applicationSessionPractitionerReader = injectedReader;
        ${getBootstrap}
        ${isEnabled}
        ${resetHelper}
        ${createFailure}
        ${loadDirectory}
        try {
          transitionResult = await loadPractitionerDirectory();
        } catch (error) {
          transitionError = error;
        }
        resetState = {
          composition: applicationSessionPractitionerDirectory,
          reader: applicationSessionPractitionerReader,
        };
      })()`, context, { filename: `diary-transition-${transition.name}.mjs` });
      assert(context.resetState.composition === null, `composition_not_reset:${transition.name}`);
      assert(context.resetState.reader === null, `reader_not_reset:${transition.name}`);
      if (transition.rejects) {
        assert(
          context.transitionError?.message === 'application_session_practitioner_directory_failure',
          `transition_not_marked:${transition.name}`,
        );
      } else {
        assert(context.transitionError === null, `feature_off_rejected:${transition.name}`);
        assert(Array.isArray(context.transitionResult), `feature_off_legacy_not_used:${transition.name}`);
      }
      pending.resolve(success());
      const result = await outstanding;
      assert(
        result.ok === false && result.reason === 'session_inactive',
        `outstanding_not_suppressed:${transition.name}`,
      );
    }
  });

  await record('new_modules_have_no_direct_effect_implementation', () => {
    const source = `${fs.readFileSync(COMPOSITION_MODULE, 'utf8')}\n${fs.readFileSync(PUBLISHED_RECONCILER, 'utf8')}`;
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
      assert(!pattern.test(source), `forbidden_effect:${pattern}`);
    }
  });

  await record('legacy_graphql_and_rest_functions_are_source_exact', () => {
    const current = fs.readFileSync(DIARY_JS, 'utf8').replace(/\r\n/g, '\n');
    const original = execFileSync(
      'git',
      ['show', `${SOURCE_HEAD}:docs/diary/diary.js`],
      { cwd: ROOT, encoding: 'utf8' },
    ).replace(/\r\n/g, '\n');
    for (const name of ['fetchPractitionerDirectoryRest', 'fetchPractitionerDirectoryGraphql']) {
      assert(extractFunction(current, name) === extractFunction(original, name), `legacy_function_drift:${name}`);
    }
  });

  await record('enabled_branch_precedes_and_cannot_enter_legacy_fallback', () => {
    const source = fs.readFileSync(DIARY_JS, 'utf8').replace(/\r\n/g, '\n');
    const load = extractFunction(source, 'loadPractitionerDirectory');
    const branch = load.indexOf('isApplicationSessionPractitionerBootstrapEnabled');
    const enabledReturn = load.indexOf('return await loadApplicationSessionPractitionerDirectory');
    const legacyGate = load.indexOf('if (!ENABLE_GRAPHQL_PRACTITIONERS)');
    assert(branch >= 0 && enabledReturn > branch && legacyGate > enabledReturn, 'branch_order');
    const helper = extractFunction(source, 'loadApplicationSessionPractitionerDirectory');
    assert(!helper.includes('fetchPractitionerDirectoryGraphql'), 'enabled_graphql_fallback');
    assert(!helper.includes('fetchPractitionerDirectoryRest'), 'enabled_rest_fallback');
    assert(!helper.includes('apiFetch('), 'enabled_bearer_transport');
  });

  await record('invalid_transitions_reset_and_enabled_failure_rethrows_at_call_site', () => {
    const source = fs.readFileSync(DIARY_JS, 'utf8').replace(/\r\n/g, '\n');
    const load = extractFunction(source, 'loadPractitionerDirectory');
    const resetCalls = load.match(
      /invalidateAndResetApplicationSessionPractitionerDirectory\(\)/g,
    ) || [];
    assert(resetCalls.length === 2, 'transition_reset_call_count');
    assert(load.includes('return await loadApplicationSessionPractitionerDirectory'), 'enabled_not_awaited');
    assert(load.includes('throw createApplicationSessionPractitionerFailure()'), 'enabled_not_marked');
    assert(
      source.includes('loadPractitionerDirectory().catch(handlePractitionerDirectoryLoadFailure)'),
      'practitioner_call_site_handler_missing',
    );

    const isFailure = extractFunction(source, 'isApplicationSessionPractitionerFailure');
    const createFailure = extractFunction(source, 'createApplicationSessionPractitionerFailure');
    const handler = extractFunction(source, 'handlePractitionerDirectoryLoadFailure');
    const context = { rethrownMessage: null, legacyResult: null, console: { warn: () => {} } };
    vm.runInNewContext(`
      const APPLICATION_SESSION_PRACTITIONER_FAILURE =
        'application_session_practitioner_directory_failure';
      ${isFailure}
      ${createFailure}
      ${handler}
      try {
        handlePractitionerDirectoryLoadFailure(
          createApplicationSessionPractitionerFailure(),
        );
      } catch (error) {
        rethrownMessage = error.message;
      }
      legacyResult = handlePractitionerDirectoryLoadFailure(
        new Error('legacy_directory_failure'),
      );
    `, context);
    assert(
      context.rethrownMessage === 'application_session_practitioner_directory_failure',
      'enabled_failure_not_rethrown',
    );
    assert(Array.isArray(context.legacyResult) && context.legacyResult.length === 0, 'legacy_swallow_not_preserved');
  });

  return cases;
}

async function main() {
  const outputPath = parseOutput(process.argv.slice(2));
  const cases = await runAcceptance();
  const evidence = {
    schema_version: 'emr4.native_diary_ui_composition_evidence.v1',
    result: RESULT,
    evidence_label: EVIDENCE_LABEL,
    data_class: 'authored_synthetic',
    case_count: cases.length,
    passed_case_count: cases.length,
    failed_case_count: 0,
    properties: {
      strict_true_default_off: true,
      enabled_path_has_no_legacy_fallback: true,
      enabled_failure_rethrown_by_enclosing_load: true,
      invalid_transition_resets_cached_reconciler: true,
      canonical_reconciler_lf_parity: true,
      latest_read_wins: true,
      stale_generation_and_invalidation_suppressed: true,
      strict_response_admission: true,
      sanitized_snapshot: true,
      provider_or_external_effect: false
    },
    claims_not_made: [
      'browser',
      'route_intercepted',
      'http',
      'backend',
      'postgresql',
      'usability',
      'production',
      'release'
    ],
    hashes: {
      published_reconciler_sha256: crypto.createHash('sha256')
        .update(canonicalLf(fs.readFileSync(PUBLISHED_RECONCILER)), 'utf8').digest('hex'),
      composition_module_sha256: crypto.createHash('sha256')
        .update(canonicalLf(fs.readFileSync(COMPOSITION_MODULE)), 'utf8').digest('hex')
    }
  };
  const serialized = `${JSON.stringify(evidence, null, 2)}\n`;
  for (const forbidden of ['Avery', 'Synthetic Clinic', 'practitioner-authored', 'location-authored']) {
    assert(!serialized.includes(forbidden), `evidence_leak:${forbidden}`);
  }
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, serialized, { encoding: 'utf8', flag: 'w' });
  process.stdout.write(`${JSON.stringify(evidence)}\n`);
}

main().catch((error) => {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
});
