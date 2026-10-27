"""Pure synthetic receipt/commit regression; not SQLAlchemy, PostgreSQL or RLS proof.

The exact service functions execute via AST extraction. A strict row double models
expiration and loss of transaction-local tenant context at successful commit.
Run this same file in separately admitted old/fixed source capsules for RED/GREEN.
No product modules, model registry, repository conftest or providers are imported.
"""
import ast
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import uuid
from zoneinfo import ZoneInfo


class PostCommitMappedRead(RuntimeError):
    """A modeled expired refresh after SET LOCAL context ended."""


class CommitFailure(RuntimeError):
    pass


class HttpFailure(Exception):
    def __init__(self, *, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(status_code)


class Rejected(Exception):
    pass


class ExpiringRow:
    def __init__(self, values):
        object.__setattr__(self, '_values', copy.deepcopy(values))
        object.__setattr__(self, '_expired', False)
        object.__setattr__(self, '_postcommit_reads', [])

    def __getattr__(self, name):
        values = object.__getattribute__(self, '_values')
        if name not in values:
            raise AttributeError(name)
        if object.__getattribute__(self, '_expired'):
            object.__getattribute__(self, '_postcommit_reads').append(name)
            raise PostCommitMappedRead('expired row refresh requires a new tenant-scoped transaction')
        return values[name]

    def __setattr__(self, name, value):
        object.__getattribute__(self, '_values')[name] = value


class ExpiringSession:
    expire_on_commit = True

    def __init__(self, row, *, fail=False):
        self.row, self.fail = row, fail
        self.commits = 0
        self.tenant_context = 'synthetic-practice'
        self.persisted = None

    def commit(self):
        if self.fail:
            raise CommitFailure('synthetic commit failure')
        self.commits += 1
        self.persisted = copy.deepcopy(object.__getattribute__(self.row, '_values'))
        self.tenant_context = None
        object.__setattr__(self.row, '_expired', True)


def service_functions():
    path = Path(__file__).resolve().parents[1] / 'app/services/patient_request_service.py'
    tree = ast.parse(path.read_bytes(), filename=str(path))
    names = {'_utc_text', 'allowed_dates', 'submit_request'}
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if len(selected) != len(names) or {n.name for n in selected} != names:
        raise AssertionError('exact service function selection')
    # Existing profile/capability/validator code is outside this synthetic boundary.
    # Native regression must retain the actual mounted route and all those guards.
    namespace = {'datetime': datetime, 'timedelta': timedelta, 'timezone': timezone,
                 'hashlib': hashlib, 'hmac': hmac, 'json': json, 'ZoneInfo': ZoneInfo,
                 'Session': ExpiringSession, 'PatientBookingRequest': ExpiringRow,
                 'HTTPException': HttpFailure, 'RequestRejected': Rejected,
                 '_profile_ids': lambda: (None, None, b'synthetic-only-secret-material-32bytes'),
                 'validate_submission': lambda raw, context: SimpleNamespace(**raw)}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['submit_request']


def draft():
    now = datetime.now(timezone.utc)
    return ExpiringRow({'id': uuid.UUID('70000000-0000-4000-8000-000000000001'),
        'practice_timezone': 'Australia/Brisbane', 'request_version': 7,
        'state': 'draft', 'capability_expires_at': now + timedelta(hours=1),
        'submission_key_digest': None, 'submission_body_digest': None,
        'submission_receipt': None})


def body():
    tomorrow = datetime.now(timezone.utc).astimezone(ZoneInfo('Australia/Brisbane')).date() + timedelta(days=1)
    return {'schema_version': 'patient.request_submission.v1',
            'request_id': '70000000-0000-4000-8000-000000000001',
            'request_version': 7, 'date': tomorrow.isoformat(), 'earliest_local': '14:00',
            'latest_local': '16:00', 'reason_code': 'follow_up', 'authority': 'request_only'}


class SubmissionReceiptCommitRegression(unittest.TestCase):
    def test_successful_commit_returns_receipt_without_expired_row_read(self):
        row = draft()
        db = ExpiringSession(row)
        receipt = service_functions()(db, row, body(), 'first-submit')
        self.assertEqual(receipt, {'request_id': '70000000-0000-4000-8000-000000000001',
            'state': 'submitted', 'request_version': 8,
            'message': 'Request received for staff review.'})
        self.assertEqual(db.commits, 1)
        self.assertEqual(db.persisted['submission_receipt'], receipt)
        self.assertEqual(db.persisted['state'], 'submitted')
        self.assertEqual(db.persisted['request_version'], 8)
        self.assertIsNone(db.tenant_context)
        self.assertTrue(db.expire_on_commit)
        self.assertEqual(object.__getattribute__(row, '_postcommit_reads'), [])
        with self.assertRaises(PostCommitMappedRead):
            _ = row.submission_receipt

    def test_same_key_replay_returns_stored_receipt_without_second_commit(self):
        row = draft()
        db = ExpiringSession(row)
        raw = body()
        receipt = service_functions()(db, row, raw, 'same-key')
        fresh_row = ExpiringRow(db.persisted)
        fresh_db = ExpiringSession(fresh_row)
        replay = service_functions()(fresh_db, fresh_row, raw, 'same-key')
        self.assertEqual(replay, receipt)
        self.assertEqual(fresh_row.request_version, 8)
        self.assertEqual(fresh_db.commits, 0)

    def test_changed_body_same_key_keeps_conflict(self):
        row = draft()
        db = ExpiringSession(row)
        raw = body()
        service_functions()(db, row, raw, 'same-key')
        fresh_row = ExpiringRow(db.persisted)
        fresh_db = ExpiringSession(fresh_row)
        with self.assertRaises(HttpFailure) as caught:
            service_functions()(fresh_db, fresh_row, dict(raw, reason_code='other'), 'same-key')
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(caught.exception.detail, {'code': 'REQUEST_KEY_CONFLICT'})
        self.assertEqual(fresh_db.commits, 0)
        self.assertEqual(fresh_row.request_version, 8)

    def test_commit_failure_propagates_without_success_result(self):
        row = draft()
        db = ExpiringSession(row, fail=True)
        with self.assertRaises(CommitFailure):
            service_functions()(db, row, body(), 'failed-commit')
        self.assertEqual(db.commits, 0)
        self.assertIsNone(db.persisted)


if __name__ == '__main__':
    unittest.main()
