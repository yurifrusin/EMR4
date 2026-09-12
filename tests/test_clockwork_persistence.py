"""Focused adapter tests, executable directly without repository collection.

The direct runner loads exactly the adapter and its two pinned kernel inputs.
Child processes use that same capsule. All databases and synchronization files
are newly authored under TemporaryDirectory; the live repository is denied.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

if __name__ != "__main__":
    from orchestration_harness import clockwork_persistence as p
    from orchestration_harness.clockwork_state import ClockworkCommand as Command
    from orchestration_harness.clockwork_state import ClockworkEvent as Event
    from orchestration_harness.clockwork_state import ClockworkState as State

_SOURCE_SHA = (hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest()
               if __name__ != "__main__" else None)
_VIOLATIONS = []
_KILLED = []
_EXPECTED_CHILD_COMMAND = None


def _capsule(source_sha):
    global p, Command, Event, State, _SOURCE_SHA
    _SOURCE_SHA = source_sha
    root = Path(__file__).absolute().parents[1]
    pins = {
        "clockwork_state": "6e54a4414c3fb22a46caa6b471749d31a4e9fcc356f90f011e9fd8d17a31d052",
        "clockwork_journal": "98686ae95c8477511e0ebee0170e0232ee39c5270b14d1cdcba74def11791b6c",
        "clockwork_persistence": source_sha,
    }
    if any(n == "orchestration_harness" or n.startswith("orchestration_harness.") for n in sys.modules):
        raise RuntimeError("ambient repository import")
    package = types.ModuleType("orchestration_harness")
    package.__path__ = []
    sys.modules[package.__name__] = package
    for name, digest in pins.items():
        path = root / "orchestration_harness" / (name + ".py")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise RuntimeError("source changed")
        module = types.ModuleType("orchestration_harness." + name)
        module.__file__ = str(path)
        sys.modules[module.__name__] = module
        setattr(package, name, module)
        exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    p = package.clockwork_persistence
    Command = package.clockwork_state.ClockworkCommand
    Event = package.clockwork_state.ClockworkEvent
    State = package.clockwork_state.ClockworkState


def _guard(event, args):
    blocked = False
    if event in {"open", "os.listdir", "os.scandir", "sqlite3.connect"} and args and isinstance(args[0], (str, bytes)):
        value = os.fsdecode(args[0]).replace(chr(92), "/").casefold()
        roots = ("c:/users/there/emr4", "c:/users/sarashera/emr4", "c:/users/sarashera/emr4-worktrees")
        blocked = any(value == root or value.startswith(root + "/") or
                      value.startswith("file:///" + root + "/") for root in roots)
    if event.startswith("socket.") or event == "os.system":
        blocked = True
    if event == "subprocess.Popen":
        expected = _EXPECTED_CHILD_COMMAND
        argument_match = False
        if expected is not None and len(args) > 1:
            if isinstance(args[1], (list, tuple)):
                argument_match = list(args[1]) == expected
            elif type(args[1]) is str:
                argument_match = args[1] == subprocess.list2cmdline(expected)
        blocked = not (argument_match and args[0] in (None, sys.executable))
    if blocked:
        _VIOLATIONS.append(event)
        raise RuntimeError("observation outside synthetic capsule")


def _write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())


def _await_file(path):
    deadline = time.monotonic() + 15
    while not Path(path).exists():
        if time.monotonic() >= deadline:
            raise RuntimeError("synthetic rendezvous timed out")
        time.sleep(0.01)


def _child(job_path):
    job = json.loads(job_path.read_bytes())
    store = p.ClockworkStore(Path(job["database"]))
    mode = job["mode"]
    if mode in {"before_commit", "after_commit", "lost_response"}:
        original = p.ClockworkStore._connect

        class CommitBoundary:
            def __init__(self, db):
                self.db = db
                self.appended = False

            def __getattr__(self, name):
                return getattr(self.db, name)

            def execute(self, sql, *args):
                if sql.startswith("INSERT INTO entries"):
                    self.appended = True
                boundary = self.appended and sql == "COMMIT"
                if boundary and mode == "before_commit":
                    self.pause()
                result = self.db.execute(sql, *args)
                if boundary and mode == "after_commit":
                    self.pause()
                if boundary and mode == "lost_response":
                    raise OSError("simulated response loss after real commit")
                return result

            def pause(self):
                journal = store.path.with_name(store.path.name + "-journal")
                _write_json(job["ready"], {"mode": mode, "pid": os.getpid(), "rollback_journal_present": journal.exists()})
                while True:
                    time.sleep(1)

        p.ClockworkStore._connect = lambda self: CommitBoundary(original(self))
    else:
        _write_json(job["ready"], {"pid": os.getpid()})
        _await_file(job["go"])
    try:
        if mode == "acquire":
            lease = store.acquire_lease(job["owner"], 60_000_000_000)
            result = {"status": "lease_acquired", "fence": lease.fence}
        else:
            outcome = store.append(p.Lease(**job["lease"]), p.JournalHead(**job["head"]),
                                   job["request_id"], Event.START, Command.ADVANCE)
            result = {"status": "committed", "accepted": outcome.accepted, "sequence": outcome.entry.sequence}
    except p.PersistenceError as error:
        result = {"status": error.code}
    _write_json(job["result"], result)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="clockwork-persistence-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).absolute()
        self.store = p.ClockworkStore.create(self.root / "clockwork #1.sqlite")

    def error(self, code, function, *args):
        with self.assertRaises(p.PersistenceError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)

    def lease(self):
        return self.store.acquire_lease("coordinator", 60_000_000_000)

    def append(self, lease, request="request-1", event=None, command=None):
        return self.store.append(lease, self.store.recover().head, request,
                                 event or Event.START, command or Command.ADVANCE)

    def test_recovery_replays_committed_state_and_derives_narrative(self):
        empty = self.store.recover()
        self.assertEqual(empty.state, State.IDLE)
        self.assertEqual(empty.head, p.JournalHead(0, p.GENESIS_PREVIOUS_DIGEST))
        self.assertEqual(empty.narrative, "Clockwork state: idle. Journal entries: 0.")
        result = self.append(self.lease())
        self.assertTrue(result.accepted)
        recovered = p.ClockworkStore(self.store.path).recover()
        self.assertEqual(recovered.state, State.ACTIVE)
        self.assertEqual(recovered.replayed.validated_journal, (result.entry,))
        self.assertEqual(recovered.narrative, "Clockwork state: active. Journal entries: 1. Last attempt: start/advance, accepted.")
        forged = p.Snapshot(replace(recovered.replayed, state=State.IDLE))
        self.error("store_corrupt", lambda: forged.narrative)

    def test_invalid_transition_is_audited_without_state_advance(self):
        lease = self.lease()
        invalid = self.append(lease, event=Event.STOP, command=Command.HOLD)
        self.assertFalse(invalid.accepted)
        self.assertEqual(invalid.entry.stored_result.invalid.code, "invalid_transition")
        self.assertEqual(self.store.recover().state, State.IDLE)
        self.assertIn("rejected: invalid_transition", self.store.recover().narrative)
        valid = self.append(lease, "request-2")
        self.assertTrue(valid.accepted)
        self.assertEqual(valid.entry.previous_digest, invalid.entry.digest)
        repeated = self.append(lease, "request-3")
        self.assertFalse(repeated.accepted)
        self.assertEqual(self.store.recover().state, State.ACTIVE)

    def test_input_types_and_forged_leases_fail_before_append(self):
        lease = self.lease()
        head = self.store.recover().head
        for changed in (replace(head, sequence=True), replace(head, digest="sha256:" + "f" * 63)):
            self.error("invalid_argument", self.store.append, lease, changed, "x", Event.START, Command.ADVANCE)
        for event, command in (("start", Command.ADVANCE), (Event.START, True)):
            self.error("invalid_argument", self.store.append, lease, head, "x", event, command)
        self.error("stale_lease", self.store.append, replace(lease, fence=True), head, "x", Event.START, Command.ADVANCE)
        self.assertEqual(self.store.recover().head, head)

    def test_head_compare_and_swap_and_idempotent_request_binding(self):
        lease = self.lease()
        before = self.store.recover().head
        first = self.append(lease)
        self.error("head_conflict", self.store.append, lease, before, "different-request", Event.START, Command.ADVANCE)
        retry = self.store.append(lease, before, "request-1", Event.START, Command.ADVANCE)
        self.assertTrue(retry.already_committed)
        self.assertEqual(retry.entry, first.entry)
        self.error("request_conflict", self.store.append, lease, before, "request-1", Event.STOP, Command.ADVANCE)
        self.error("request_conflict", self.store.append, lease, self.store.recover().head, "request-1", Event.START, Command.ADVANCE)
        self.assertEqual(self.store.lookup("request-1"), retry)
        self.assertIsNone(self.store.lookup("unknown"))
        self.assertEqual(self.store.recover().head.sequence, 1)

    def test_lease_busy_release_and_fencing_across_reopen(self):
        old = self.lease()
        self.error("lease_busy", self.store.acquire_lease, "coordinator", 60_000_000_000)
        self.store.release_lease(old)
        fresh = p.ClockworkStore(self.store.path).acquire_lease("coordinator", 60_000_000_000)
        self.assertEqual(fresh.fence, old.fence + 1)
        self.error("stale_lease", self.append, old)
        self.assertTrue(self.append(fresh).accepted)
        other = p.ClockworkStore.create(self.root / "other.sqlite")
        self.error("stale_lease", other.append, fresh, other.recover().head, "x", Event.START, Command.ADVANCE)

    def test_expiry_renewal_and_clock_regression(self):
        with mock.patch.object(p, "_now_ns", return_value=100):
            store = p.ClockworkStore.create(self.root / "clock.sqlite")
            old = store.acquire_lease("worker", 100)
        with mock.patch.object(p, "_now_ns", return_value=150):
            renewed = store.renew_lease(old, 100)
            self.error("stale_lease", store.append, old, store.recover().head, "x", Event.START, Command.ADVANCE)
        with mock.patch.object(p, "_now_ns", return_value=149):
            self.error("clock_regressed", store.append, renewed, store.recover().head, "x", Event.START, Command.ADVANCE)
        with mock.patch.object(p, "_now_ns", return_value=250):
            self.error("stale_lease", store.append, renewed, store.recover().head, "x", Event.START, Command.ADVANCE)
            fresh = store.acquire_lease("new-worker", 100)
            self.assertGreater(fresh.fence, renewed.fence)
            self.error("stale_lease", store.release_lease, renewed)
            self.assertTrue(store.append(fresh, store.recover().head, "x", Event.START, Command.ADVANCE).accepted)

    def test_lease_expiring_during_append_rolls_back_both_head_and_entry(self):
        with mock.patch.object(p, "_now_ns", return_value=100):
            store = p.ClockworkStore.create(self.root / "expires.sqlite")
            lease = store.acquire_lease("worker", 200)
        before = store.recover()
        with mock.patch.object(p, "_now_ns", side_effect=(200, 300)):
            self.error("stale_lease", store.append, lease, before.head, "expires", Event.START, Command.ADVANCE)
        self.assertEqual(store.recover(), before)
        self.assertIsNone(store.lookup("expires"))

    def test_append_only_sql_guards(self):
        self.append(self.lease())
        before = self.store.recover()
        with closing(sqlite3.connect(self.store.path)) as db, db:
            for statement in ("UPDATE entries SET request_id='changed'", "DELETE FROM entries"):
                with self.assertRaisesRegex(sqlite3.IntegrityError, "append_only_journal"):
                    db.execute(statement)
        self.assertEqual(self.store.recover(), before)

    def test_corrupt_envelopes_and_truncated_tail_fail_closed(self):
        self.append(self.lease())
        original = self.store.path.read_bytes()
        with closing(sqlite3.connect(self.store.path)) as db:
            payload = db.execute("SELECT payload FROM entries").fetchone()[0]
        altered = json.loads(payload)
        altered["stored_result"]["state_schema_version"] = "unknown"
        cases = [
            ("UPDATE entries SET payload=?", (payload + b" ",)),
            ("UPDATE entries SET payload=?", (json.dumps(altered, sort_keys=True, separators=(",", ":")).encode(),)),
            ("UPDATE entries SET digest=?", ("sha256:" + "f" * 64,)),
            ("DELETE FROM entries", ()),
            ("UPDATE metadata SET head_sequence=0", ()),
            ("CREATE TABLE unrelated (value TEXT)", ()),
            ("CREATE TABLE sqlitex_extra (value TEXT)", ()),
        ]
        for i, (statement, args) in enumerate(cases):
            with self.subTest(case=i):
                path = self.root / f"corrupt-{i}.sqlite"
                path.write_bytes(original)
                with closing(sqlite3.connect(path)) as db, db:
                    triggers = db.execute("SELECT sql FROM sqlite_schema WHERE type='trigger'").fetchall()
                    db.execute("DROP TRIGGER entries_no_update")
                    db.execute("DROP TRIGGER entries_no_delete")
                    db.execute(statement, args)
                    for (sql,) in triggers:
                        db.execute(sql)
                before = path.read_bytes()
                self.error("store_corrupt", p.ClockworkStore(path).recover)
                self.assertEqual(path.read_bytes(), before)

    def test_missing_and_existing_stores_are_not_silently_initialized(self):
        before = self.store.path.read_bytes()
        self.error("store_exists", p.ClockworkStore.create, self.store.path)
        self.assertEqual(self.store.path.read_bytes(), before)
        missing = self.root / "missing.sqlite"
        self.error("missing_store", p.ClockworkStore(missing).recover)
        self.assertFalse(missing.exists())
        incomplete = self.root / "incomplete.sqlite"
        incomplete.write_bytes(b"")
        self.error("store_corrupt", p.ClockworkStore(incomplete).recover)
        self.assertEqual(incomplete.read_bytes(), b"")
        self.error("unsafe_path", p.ClockworkStore, Path("relative.sqlite"))
        orphan = self.root / "orphan.sqlite"
        journal = orphan.with_name(orphan.name + "-journal")
        journal.write_bytes(b"unresolved orphan journal")
        self.error("unsafe_path", p.ClockworkStore.create, orphan)
        self.assertFalse(orphan.exists())
        self.assertEqual(journal.read_bytes(), b"unresolved orphan journal")

    def job(self, name, mode, lease=None, head=None, **extra):
        global _EXPECTED_CHILD_COMMAND
        job = {"database": str(self.store.path), "mode": mode, "ready": str(self.root / (name + ".ready")),
               "result": str(self.root / (name + ".result")), "request_id": name, **extra}
        if lease is not None:
            job.update(lease=asdict(lease), head=asdict(head))
        path = self.root / (name + ".job")
        _write_json(path, job)
        command = [sys.executable, "-I", "-B", "-S", str(Path(__file__).absolute()),
                   "--source-sha256", _SOURCE_SHA, "--child", str(path)]
        _EXPECTED_CHILD_COMMAND = command
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        finally:
            _EXPECTED_CHILD_COMMAND = None
        self.addCleanup(self.stop, process)
        return process, job

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=15)

    def completed(self, process, job):
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stdout + stderr)
        return json.loads(Path(job["result"]).read_bytes())

    def test_real_process_death_before_commit_recovers_previous_state(self):
        self.crash("before_commit")

    def test_real_process_death_after_commit_recovers_once(self):
        self.crash("after_commit")

    def crash(self, mode):
        lease = self.lease()
        self.append(lease, "baseline", Event.STOP)
        before = self.store.recover()
        process, job = self.job("crash", mode, lease, before.head)
        _await_file(job["ready"])
        marker = json.loads(Path(job["ready"]).read_bytes())
        self.assertEqual(marker["mode"], mode)
        self.assertEqual(marker["pid"], process.pid)
        self.assertEqual(marker["rollback_journal_present"], mode == "before_commit")
        process.kill()
        process.communicate(timeout=15)
        self.assertNotEqual(process.returncode, 0)
        _KILLED.append(mode)
        recovered = p.ClockworkStore(self.store.path).recover()
        if mode == "before_commit":
            self.assertEqual(recovered, before)
            self.assertIsNone(self.store.lookup("crash"))
        else:
            self.assertEqual(recovered.state, State.ACTIVE)
            self.assertEqual(recovered.head.sequence, before.head.sequence + 1)
            self.assertTrue(self.store.lookup("crash").accepted)
            duplicate = self.store.append(lease, before.head, "crash", Event.START, Command.ADVANCE)
            self.assertTrue(duplicate.already_committed)
            self.assertEqual(self.store.recover(), recovered)

    def test_lost_response_is_explicit_and_readback_finds_the_commit(self):
        lease = self.lease()
        before = self.store.recover().head
        process, job = self.job("lost-response", "lost_response", lease, before)
        self.assertEqual(self.completed(process, job), {"status": "commit_outcome_unknown"})
        self.assertTrue(self.store.lookup("lost-response").accepted)
        self.assertEqual(self.store.recover().head.sequence, 1)

    def test_two_processes_cannot_commit_the_same_head(self):
        lease, head = self.lease(), self.store.recover().head
        gate = str(self.root / "go")
        children = [self.job(f"race-{i}", "append", lease, head, go=gate) for i in range(2)]
        for _, job in children:
            _await_file(job["ready"])
        Path(gate).write_bytes(b"go")
        outcomes = [self.completed(process, job)["status"] for process, job in children]
        self.assertCountEqual(outcomes, ["committed", "head_conflict"])
        self.assertEqual(self.store.recover().head.sequence, 1)

    def test_two_processes_cannot_both_acquire_an_active_lease(self):
        gate = str(self.root / "go")
        children = [self.job(f"lease-{i}", "acquire", owner=f"owner-{i}", go=gate) for i in range(2)]
        for _, job in children:
            _await_file(job["ready"])
        Path(gate).write_bytes(b"go")
        outcomes = [self.completed(process, job) for process, job in children]
        self.assertCountEqual([r["status"] for r in outcomes], ["lease_acquired", "lease_busy"])
        self.assertEqual(next(r["fence"] for r in outcomes if r["status"] == "lease_acquired"), 1)
        self.assertEqual(self.store.recover().head.sequence, 0)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--child", type=Path)
    args = parser.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode and not sys.flags.optimize):
        raise RuntimeError("isolated interpreter required")
    _capsule(args.source_sha256)
    sys.addaudithook(_guard)
    if args.child:
        _child(args.child)
        return 0
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PersistenceTests))
    modules = sorted(n for n in sys.modules if n.startswith("orchestration_harness."))
    expected = ["orchestration_harness.clockwork_journal", "orchestration_harness.clockwork_persistence",
                "orchestration_harness.clockwork_state"]
    passed = result.wasSuccessful() and not _VIOLATIONS and modules == expected
    print(json.dumps({"status": "pass" if passed else "fail", "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped),
        "guard_violations": _VIOLATIONS, "native_process_death_boundaries": sorted(_KILLED),
        "source_sha256": args.source_sha256, "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": sys.version.split()[0], "sqlite_version": sqlite3.sqlite_version,
        "source_modules": modules, "live_repository_tested": False, "full_suite": False}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(_main())
