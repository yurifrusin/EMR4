"""Direct, isolated v2 integration tests; no repository discovery or providers."""
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
    from orchestration_harness import clockwork_governor as g, clockwork_persistence as p

S = 1_000_000_000
EVIDENCE = "sha256:" + "a" * 64
_PINS = {}
_CHILD = None
_VIOLATIONS = []
_KILLS = []
if __name__ != "__main__":
    _PINS = {"clockwork_persistence": hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest(),
             "clockwork_governor": hashlib.sha256(Path(g.__file__).read_bytes()).hexdigest()}


def policy(now, **changes):
    value = dict(envelope_id="recovery-test", owner="owner", scope_digest=EVIDENCE,
        account="account-1", quota_pool="shared-pool", window_id="window-1", units="usage_units",
        window_start_ns=now-S, window_end_ns=now+600*S, deadline_ns=now+300*S,
        max_operation_ns=120*S, max_no_progress_ns=90*S, max_usage_age_ns=300*S,
        max_no_progress_events=3, max_wip=3, max_depth=2, max_attempts_per_operation=2,
        max_attempts_total=8, max_tokens=100, max_usage=100, authorities=[
            dict(authority_id="standing-recovery", issuer="owner", source_digest=EVIDENCE,
                 operations=["op-1", "publish"], actions=["read", "repair_edit", "recovery_publish"], expires_ns=now+200*S)])
    value.update(changes)
    return value


def observation(settings, now, **changes):
    value = {k: settings[k] for k in ("account", "quota_pool", "window_id", "units", "window_start_ns", "window_end_ns")}
    value.update(kind="observe_usage", observed_ns=now, fresh_until_ns=min(now+150*S, settings["window_end_ns"]),
                 remaining=100, evidence_digest=EVIDENCE, accounted_attempts=[])
    value.update(changes)
    return value


def admit(operation="op-1", attempt="attempt-1", **changes):
    value = dict(kind="admit", operation_id=operation, task_id="task-"+operation, attempt_id=attempt,
                 parent_operation_id=None, worker_id="worker-1", task_kind="repair", action="repair_edit",
                 risk="low", authority_id=None, tokens=20, usage=20)
    value.update(changes)
    return value


def settle(attempt="attempt-1", **changes):
    value = dict(kind="settle", attempt_id=attempt, disposition="failed", tokens=10, usage=10,
                 worker_stopped=True, evidence_digest=EVIDENCE)
    value.update(changes)
    return value


def _write(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())


def _await(path):
    deadline = time.monotonic()+15
    while not Path(path).exists():
        if time.monotonic() >= deadline:
            raise RuntimeError("synthetic rendezvous timeout")
        time.sleep(.01)


def _guard(event, args):
    blocked = False
    if event in {"open", "os.listdir", "os.scandir", "sqlite3.connect"} and args and isinstance(args[0], (str, bytes)):
        value = os.fsdecode(args[0]).replace(chr(92), "/").casefold()
        roots = ("c:/users/there/emr4", "c:/users/sarashera/emr4", "c:/users/sarashera/emr4-worktrees")
        blocked = any(value == r or value.startswith(r+"/") or value.startswith("file:///"+r+"/") for r in roots)
    if event.startswith("socket.") or event == "os.system":
        blocked = True
    if event == "subprocess.Popen":
        arguments = args[1] if len(args) > 1 else None
        matches = (_CHILD is not None and
                   ((isinstance(arguments, (list, tuple)) and list(arguments) == _CHILD)
                    or (type(arguments) is str and arguments == subprocess.list2cmdline(_CHILD))))
        blocked = not (matches and args[0] in (None, sys.executable))
    if blocked:
        _VIOLATIONS.append(event)
        raise RuntimeError("observation outside synthetic capsule")


def _capsule(persistence_sha, governor_sha):
    global p, g, _PINS
    _PINS = {"clockwork_state": "6e54a4414c3fb22a46caa6b471749d31a4e9fcc356f90f011e9fd8d17a31d052",
             "clockwork_journal": "98686ae95c8477511e0ebee0170e0232ee39c5270b14d1cdcba74def11791b6c",
             "clockwork_governor": governor_sha, "clockwork_persistence": persistence_sha}
    root = Path(__file__).absolute().parents[1]
    if any(n == "orchestration_harness" or n.startswith("orchestration_harness.") for n in sys.modules):
        raise RuntimeError("ambient repository import")
    package = types.ModuleType("orchestration_harness")
    package.__path__ = []
    sys.modules[package.__name__] = package
    for name, digest in _PINS.items():
        path = root / "orchestration_harness" / (name+".py")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise RuntimeError("source changed")
        module = types.ModuleType("orchestration_harness."+name)
        module.__file__ = str(path)
        sys.modules[module.__name__] = module
        setattr(package, name, module)
        exec(compile(raw, str(path), "exec", dont_inherit=True), module.__dict__)
    g, p = package.clockwork_governor, package.clockwork_persistence


def _child(job):
    store = p.GovernorStore(Path(job["database"]))
    if job["mode"] == "recover":
        recovered = store.recover()
        _write(job["result"], {"head": asdict(recovered.head), "state": recovered.state, "narrative": recovered.narrative})
        return
    mode = job["mode"]
    if mode in {"before_commit", "after_commit", "lost_response"}:
        original = p.GovernorStore._connect

        class Boundary:
            def __init__(self, db):
                self.db, self.appended = db, False

            def __getattr__(self, key):
                return getattr(self.db, key)

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
                    raise OSError("lost response after actual commit")
                return result

            def pause(self):
                _write(job["ready"], {"pid": os.getpid(), "boundary": mode,
                    "rollback_journal_present": store.path.with_name(store.path.name+"-journal").exists()})
                while True:
                    time.sleep(1)

        p.GovernorStore._connect = lambda self: Boundary(original(self))
    else:
        _write(job["ready"], {"pid": os.getpid()})
        _await(job["go"])
    try:
        result = store.append(p.Lease(**job["lease"]), p.JournalHead(**job["head"]), job["request_id"], job["command"])
        outcome = {"reason": result.reason, "accepted": result.accepted, "dispatch_allowed": result.dispatch_allowed}
    except p.PersistenceError as error:
        if error.code == "head_conflict" and mode == "contend_reservations":
            # A known pre-effect CAS rejection permits one fresh evaluation.
            result = store.append(p.Lease(**job["lease"]), store.recover().head, job["request_id"], job["command"])
            outcome = {"reason": result.reason, "accepted": result.accepted, "dispatch_allowed": result.dispatch_allowed}
        else:
            outcome = {"reason": error.code, "dispatch_allowed": False}
    _write(job["result"], outcome)


class GovernorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="clockwork-governor-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).absolute()
        self.now = 1000*S
        self.clock = mock.patch.object(p, "_now_ns", lambda: self.now)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.serial = 0
        self.reset()

    def reset(self, **changes):
        self.serial += 1
        self.store = p.GovernorStore.create(self.root / f"governor-{self.serial}.sqlite")
        self.lease = self.store.acquire_lease("coordinator", 600*S)
        self.settings = policy(self.now, **changes)
        self.issue(dict(kind="configure", policy=self.settings), "configured")
        self.issue(observation(self.settings, self.now), "usage_observed")

    def issue(self, command, reason=None):
        self.serial += 1
        result = self.store.append(self.lease, self.store.recover().head, f"request-{self.serial}", command)
        if reason is not None:
            self.assertEqual(result.reason, reason)
        return result

    def start(self, operation="op-1", attempt="attempt-1", **changes):
        self.issue(admit(operation, attempt, **changes), "reserved")
        return self.issue(dict(kind="claim", attempt_id=attempt), "dispatch_claimed")

    def state(self):
        return self.store.recover().state

    def error(self, code, function, *args):
        with self.assertRaises((p.PersistenceError, g.GovernorError)) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)

    def test_reservation_claim_completion_and_narrative_recover_together(self):
        reserved = self.issue(admit(), "reserved")
        self.assertFalse(reserved.dispatch_allowed)
        claimed = self.issue(dict(kind="claim", attempt_id="attempt-1"), "dispatch_claimed")
        self.assertTrue(claimed.dispatch_allowed)
        self.issue(settle(disposition="completed"), "usage_reconciled")
        state = p.GovernorStore(self.store.path).recover()
        self.assertEqual(state.state["attempts"]["attempt-1"]["status"], "completed")
        self.assertIn("Tokens charged/reserved: 10; usage charged/reserved: 10", state.narrative)
        self.issue(admit(attempt="again"), "operation_completed")
        forged = replace(state.replayed, state_bytes=b"null")
        self.error("journal_corrupt", lambda: forged.narrative)
        self.error("journal_corrupt", g.append, forged, {"kind": "tick"}, self.now, "forged")

    def test_global_red_repair_only_and_missing_global_state(self):
        self.issue(admit(task_kind="feature"), "global_red_repair_only")
        self.start()
        self.issue(dict(kind="set_gate", status="unknown", evidence_digest=EVIDENCE), "gate_observed")
        self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "quarantined")
        self.issue(admit("op-2", "a2"), "global_state_unknown")
        self.issue(dict(kind="set_gate", status="green", evidence_digest=EVIDENCE), "gate_observed")
        self.issue(admit("op-2", "a2", task_kind="feature"), "recovery_envelope_only")
        self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "quarantined")

    def test_human_authority_is_scoped_and_low_risk_label_cannot_bypass_publication(self):
        self.issue(admit(risk="high"), "human_authority_required")
        self.issue(admit("op-2", "a2", risk="high", authority_id="standing-recovery"), "human_authority_required")
        self.issue(admit("publish", "pub", action="recovery_publish"), "human_authority_required")
        self.start("publish", "pub", action="recovery_publish", authority_id="standing-recovery")
        self.start(risk="high", authority_id="standing-recovery")
        self.assertEqual(self.state()["attempts"]["pub"]["authority_id"], "standing-recovery")

    def test_unknown_stale_wrong_scope_and_regressed_usage_observations(self):
        self.now += S
        for field in ("account", "quota_pool", "window_id", "units"):
            with self.subTest(field=field):
                self.issue(observation(self.settings, self.now, **{field:"wrong"}), "usage_scope_mismatch")
        self.issue(observation(self.settings, 1000*S), "usage_observation_regressed")
        self.issue(observation(self.settings, self.now, fresh_until_ns=self.now+301*S), "usage_unknown")
        self.now += 150*S
        self.issue(admit(), "usage_unknown")
        self.issue(observation(self.settings, self.now), "usage_observed")
        self.issue(admit(), "reserved")

    def test_cost_and_token_limits_include_all_shared_reservations(self):
        for changes, first, second, reason in (
            ({"max_tokens":30}, {}, {}, "token_budget"),
            ({"max_usage":30}, {}, {}, "usage_budget"),
            ({"max_usage":200}, {"usage":60}, {"usage":41}, "usage_allowance"),
        ):
            with self.subTest(reason=reason):
                self.reset(**changes)
                self.issue(admit(**first), "reserved")
                self.issue(admit("op-2", "a2", **second), reason)
                self.assertEqual(len(self.state()["attempts"]), 1)

    def test_settlement_releases_unused_reservation_without_erasing_charges(self):
        self.start(tokens=60, usage=60)
        self.issue(admit("op-2", "a2", tokens=50, usage=50), "token_budget")
        self.issue(settle(tokens=10, usage=15), "usage_reconciled")
        self.issue(admit("op-2", "a2", tokens=50, usage=50), "reserved")
        self.assertEqual(g._accounting(self.state(), "usage"), 65)

    def test_unresolved_usage_retains_resources_and_wip_until_final_receipt(self):
        self.reset(max_wip=1)
        self.start()
        self.issue(settle(tokens=None, usage=None, worker_stopped=False), "outcome_unknown")
        self.issue(admit("op-2", "a2"), "wip_limit")
        self.issue(admit(attempt="a2"), "operation_unresolved")
        self.assertEqual(g._accounting(self.state(), "tokens"), 20)
        self.issue(settle(tokens=25, usage=None, worker_stopped=False), "outcome_unknown")
        self.assertEqual(g._accounting(self.state(), "tokens"), 25)
        self.issue(settle(tokens=10), "usage_regressed")
        self.issue(settle(tokens=25), "usage_reconciled")
        self.issue(admit("op-2", "a2"), "reserved")

    def test_observation_acknowledges_only_authoritatively_settled_charges(self):
        self.start()
        self.now += S
        self.issue(observation(self.settings, self.now, accounted_attempts=["attempt-1"]), "unresolved_usage_acknowledged")
        self.issue(settle(), "usage_reconciled")
        self.now += S
        self.issue(observation(self.settings, self.now, remaining=90, accounted_attempts=["attempt-1"]), "usage_observed")
        self.assertEqual(g._accounting(self.state(), "usage"), 10)
        self.assertEqual(g._accounting(self.state(), "usage", observation=True), 0)
        self.issue(admit("op-2", "a2", usage=90), "reserved")
        self.now += S
        self.issue(observation(self.settings, self.now, remaining=90), "usage_observation_regressed")

    def test_retry_budget_and_total_attempt_budget_survive_reopen(self):
        self.reset(max_attempts_total=2)
        self.start()
        self.issue(settle(), "usage_reconciled")
        self.store = p.GovernorStore(self.store.path)
        self.start(attempt="a2")
        self.issue(settle("a2"), "usage_reconciled")
        self.issue(admit(attempt="a3"), "attempt_budget")
        self.issue(admit("renamed", "a3"), "attempt_budget")
        self.reset()
        self.start()
        self.issue(settle(), "usage_reconciled")
        self.start(attempt="a2")
        self.issue(settle("a2"), "usage_reconciled")
        self.issue(admit(attempt="a3"), "retry_budget")

    def test_no_progress_count_and_time_quarantine_without_releasing_wip(self):
        self.start()
        for expected in ("progress_recorded", "progress_recorded", "no_progress"):
            self.issue(dict(kind="progress", attempt_id="attempt-1", value=0, evidence_digest=EVIDENCE), expected)
        self.assertEqual(g._accounting(self.state(), "usage"), 20)
        self.issue(settle(), "usage_reconciled")
        self.issue(admit(attempt="retry"), "no_progress")
        self.reset()
        self.start()
        self.now += 90*S
        self.issue({"kind":"tick"}, "checked")
        self.assertEqual(self.state()["attempts"]["attempt-1"]["stop_reason"], "no_progress")

    def test_real_progress_does_not_reset_operation_or_envelope_deadline(self):
        self.reset(max_operation_ns=10*S, max_no_progress_ns=9*S)
        self.start()
        deadline = self.state()["operations"]["op-1"]["deadline_ns"]
        self.now += 8*S
        self.issue(dict(kind="progress", attempt_id="attempt-1", value=1, evidence_digest=EVIDENCE), "progress_recorded")
        self.now += 2*S
        self.issue({"kind":"tick"}, "checked")
        self.assertEqual(self.state()["operations"]["op-1"]["deadline_ns"], deadline)
        self.assertEqual(self.state()["attempts"]["attempt-1"]["stop_reason"], "operation_deadline")
        self.issue(settle(), "usage_reconciled")
        self.issue(admit(attempt="retry"), "operation_deadline")
        self.now = self.settings["deadline_ns"]
        self.issue(admit("new-op", "new-attempt"), "envelope_deadline")

    def test_wip_and_nested_stack_limits_include_unresolved_children(self):
        self.start()
        self.start("child", "child-a", parent_operation_id="op-1")
        self.issue(admit("grandchild", "grandchild-a", parent_operation_id="child"), "stack_limit")
        self.issue(settle(), "children_unresolved")
        self.start("parallel", "parallel-a")
        self.issue(admit("fourth", "fourth-a"), "wip_limit")
        self.issue(dict(kind="stop", attempt_id="attempt-1", reason="worker_lost", evidence_digest=EVIDENCE), "worker_lost")
        self.assertEqual(self.state()["attempts"]["child-a"]["stop_reason"], "parent_not_running")

    def test_owner_stop_survives_settlement_and_cannot_reauthorize_itself(self):
        self.start(risk="high", authority_id="standing-recovery")
        self.issue(dict(kind="stop", attempt_id="attempt-1", reason="owner_stop", evidence_digest=EVIDENCE), "owner_stop")
        self.issue(settle(), "usage_reconciled")
        self.store = p.GovernorStore(self.store.path)
        self.issue(admit(attempt="retry", risk="high", authority_id="standing-recovery"), "owner_stop")

    def test_owner_stop_between_attempts_or_naming_an_old_attempt_stops_operation(self):
        for running_retry in (False, True):
            with self.subTest(running_retry=running_retry):
                self.reset()
                self.start()
                self.issue(settle(), "usage_reconciled")
                if running_retry:
                    self.start(attempt="retry")
                self.issue(dict(kind="stop", attempt_id="attempt-1", reason="owner_stop", evidence_digest=EVIDENCE), "owner_stop")
                state = self.state()
                self.assertEqual(state["attempts"]["attempt-1"]["status"], "failed")
                self.assertEqual(state["operations"]["op-1"]["terminal_reason"], "owner_stop")
                if running_retry:
                    self.assertEqual(state["attempts"]["retry"]["stop_reason"], "owner_stop")
                else:
                    self.issue(admit(attempt="retry"), "owner_stop")

    def test_retry_uses_its_selected_authority_expiry(self):
        authorities = policy(self.now)["authorities"]
        short = {**authorities[0], "authority_id":"short", "expires_ns":self.now+5*S}
        self.reset(authorities=authorities+[short])
        self.start(risk="high", authority_id="standing-recovery")
        self.issue(settle(), "usage_reconciled")
        claim = self.start(attempt="retry", risk="high", authority_id="short")
        self.assertEqual(claim.entry.value["outcome"]["not_after_ns"], short["expires_ns"])
        self.now = short["expires_ns"]
        self.issue({"kind":"tick"}, "checked")
        self.assertEqual(self.state()["attempts"]["retry"]["stop_reason"], "operation_deadline")

    def test_window_and_human_authority_expiry_bound_execution(self):
        self.reset(window_end_ns=self.now+5*S)
        self.start()
        self.assertEqual(self.state()["operations"]["op-1"]["deadline_ns"], self.now+5*S)
        self.now += 5*S
        self.issue({"kind":"tick"}, "usage_window_closed")
        self.assertEqual(g._accounting(self.state(), "usage"), 20)
        self.reset()
        self.settings["authorities"][0]["expires_ns"] = self.now+2*S
        self.reset(authorities=self.settings["authorities"])
        self.issue(admit(risk="high", authority_id="standing-recovery"), "reserved")
        self.now += 2*S
        self.issue(dict(kind="claim", attempt_id="attempt-1"), "operation_deadline")

    def test_completion_requires_claim_and_unclaimed_cancellation_requires_zero_usage(self):
        self.issue(admit(), "reserved")
        self.issue(dict(kind="progress", attempt_id="attempt-1", value=1, evidence_digest=EVIDENCE), "dispatch_not_claimed")
        self.issue(settle(disposition="completed", tokens=0, usage=0), "unclaimed_execution")
        self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "quarantined")
        self.issue(settle(tokens=30, usage=30), "unclaimed_execution")
        self.issue(settle(tokens=0, usage=0), "usage_regressed")
        self.assertEqual(g._accounting(self.state(), "usage"), 30)
        self.reset()
        self.issue(admit(), "reserved")
        self.issue(settle(tokens=0, usage=0), "usage_reconciled")
        self.assertEqual(g._accounting(self.state(), "usage"), 0)

    def test_duplicate_claim_and_readback_never_dispatch_twice(self):
        self.issue(admit(), "reserved")
        head = self.store.recover().head
        command = dict(kind="claim", attempt_id="attempt-1")
        first = self.store.append(self.lease, head, "one-claim", command)
        self.assertTrue(first.dispatch_allowed)
        self.assertFalse(self.store.append(self.lease, head, "one-claim", command).dispatch_allowed)
        self.assertFalse(self.store.lookup("one-claim").dispatch_allowed)
        self.issue(command, "dispatch_already_claimed")
        self.error("request_conflict", self.store.append, self.lease, head, "one-claim", {"kind":"tick"})

    def test_claim_rechecks_current_usage_and_deadline_in_atomic_write(self):
        self.issue(admit(), "reserved")
        self.now += S
        self.issue(observation(self.settings, self.now, remaining=10), "usage_observed")
        self.issue(dict(kind="claim", attempt_id="attempt-1"), "usage_allowance")
        self.reset()
        self.issue(admit(), "reserved")
        original = g.append
        def delayed(*args):
            result = original(*args)
            self.now += 91*S
            return result
        before = self.store.recover().head
        with mock.patch.object(g, "append", delayed):
            self.error("admission_expired", self.issue, dict(kind="claim", attempt_id="attempt-1"))
        self.assertEqual(self.store.recover().head, before)
        self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "reserved")

    def test_expiry_during_real_insert_rolls_back_claim_and_head(self):
        for advance, code in ((91*S, "admission_expired"), (601*S, "stale_lease")):
            with self.subTest(code=code):
                self.reset()
                self.issue(admit(), "reserved")
                original = p.GovernorStore._connect
                case = self
                class SlowInsert:
                    def __init__(self, db):
                        self.db = db
                    def __getattr__(self, key):
                        return getattr(self.db, key)
                    def execute(self, sql, *args):
                        result = self.db.execute(sql, *args)
                        if sql.startswith("INSERT INTO entries"):
                            case.now += advance
                        return result
                before = self.store.recover().head
                with mock.patch.object(p.GovernorStore, "_connect", lambda store: SlowInsert(original(store))):
                    self.error(code, self.issue, dict(kind="claim", attempt_id="attempt-1"))
                self.assertEqual(self.store.recover().head, before)
                self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "reserved")

    def test_overuse_is_recorded_truthfully_and_blocks_further_grants(self):
        self.start()
        self.issue(settle(tokens=101), "usage_reconciled")
        self.assertEqual(g._accounting(self.state(), "tokens"), 101)
        self.issue(admit("op-2", "a2"), "token_budget_exceeded")

    def test_malformed_commands_and_changed_operation_identity_fail_closed(self):
        for changed in (dict(tokens=True), dict(usage=-1), dict(action="provider"), dict(extra=1), dict(kind="unknown")):
            with self.subTest(changed=changed):
                command = admit()
                command.update(changed)
                before = self.store.recover().head
                self.error("invalid_command", self.issue, command)
                self.assertEqual(self.store.recover().head, before)
        self.start()
        self.issue(settle(), "usage_reconciled")
        self.issue(admit(attempt="a2", task_id="different"), "operation_binding_changed")

    def test_finite_policy_and_missing_usage_are_required_without_dollar_inference(self):
        for mutation in ({"max_tokens":True}, {"max_attempts_total":0}, {"max_operation_ns":float("inf")},
                         {"monetary_budget_usd":1}, {"max_depth":None}):
            with self.subTest(mutation=mutation):
                self.error("invalid_command", g.validate_command, dict(kind="configure", policy=policy(self.now, **mutation)))
        empty = g.replay(())
        entry = g.append(empty, {"kind":"tick"}, self.now, "unconfigured")
        self.assertEqual(entry.value["outcome"]["reason"], "not_configured")
        configured = g.append(empty, dict(kind="configure", policy=self.settings), self.now, "configure")
        entry = g.append(g.replay((configured,)), admit(), self.now, "without-usage")
        self.assertEqual(entry.value["outcome"]["reason"], "usage_unknown")

    def test_v1_and_v2_stores_are_explicit_and_do_not_migrate(self):
        self.error("store_corrupt", p.ClockworkStore(self.store.path).recover)
        old = p.ClockworkStore.create(self.root / "v1.sqlite")
        self.error("store_corrupt", p.GovernorStore(old.path).recover)
        self.assertEqual(old.recover().head.sequence, 0)

    def test_v2_tamper_wrong_request_binding_and_forged_outcomes_reject(self):
        self.start()
        entries = self.store.recover().replayed.entries
        value = entries[-1].value
        value["outcome"]["accepted"] = False
        raw = g.canonical(value)
        forged = g.Entry(raw, "sha256:"+hashlib.sha256(raw).hexdigest())
        self.error("journal_corrupt", g.replay, entries[:-1]+(forged,))
        self.error("journal_corrupt", g.replay, entries[1:])
        with closing(sqlite3.connect(self.store.path)) as db:
            db.execute("DROP TRIGGER entries_no_update")
            db.execute("UPDATE entries SET request_id='renamed' WHERE sequence=1")
            db.execute(p._SCHEMA[2])
            db.commit()
        self.error("store_corrupt", self.store.recover)

    def test_storage_capacity_rejects_before_committing_unreadable_database(self):
        with closing(sqlite3.connect(self.store.path)) as db:
            page_size = db.execute("PRAGMA page_size").fetchone()[0]
            pages = db.execute("PRAGMA page_count").fetchone()[0]
        with mock.patch.object(p.GovernorStore, "_storage_limit_bytes", (pages+2)*page_size):
            failed = False
            for _ in range(80):
                before = self.store.recover().head
                try:
                    self.issue({"kind":"tick"})
                except p.PersistenceError as error:
                    self.assertEqual(error.code, "store_full")
                    self.assertEqual(self.store.recover().head, before)
                    failed = True
                    break
            self.assertTrue(failed, "bounded fixture must reach the actual SQLite page limit")
        self.assertLess(self.store.path.stat().st_size, 64*1024*1024)
        self.store.recover()

    def test_stale_lease_fencing_and_clock_regression_apply_to_v2(self):
        self.issue(admit(), "reserved")
        old = self.lease
        self.lease = self.store.renew_lease(old, 600*S)
        self.error("stale_lease", self.store.append, old, self.store.recover().head, "stale", {"kind":"tick"})
        self.now -= 1
        self.error("clock_regressed", self.issue, {"kind":"tick"})

    def native(self, **changes):
        self.clock.stop()
        self.now = time.time_ns()
        self.reset(**changes)

    def child(self, mode, command=None, request="native", **extra):
        global _CHILD
        self.serial += 1
        base = self.root / f"child-{self.serial}"
        job = dict(database=str(self.store.path), mode=mode, lease=asdict(self.lease),
                   head=asdict(self.store.recover().head), command=command, request_id=request,
                   ready=str(base)+".ready", result=str(base)+".result", go=str(self.root / "go"))
        job.update(extra)
        path = str(base)+".json"
        _write(path, job)
        _CHILD = [sys.executable, "-I", "-B", "-S", str(Path(__file__).absolute()),
                  "--persistence-sha256", _PINS["clockwork_persistence"], "--governor-sha256", _PINS["clockwork_governor"], "--child", path]
        try:
            process = subprocess.Popen(_CHILD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        finally:
            _CHILD = None
        self.addCleanup(self.clean_child, process)
        return process, job

    def clean_child(self, process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=15)

    def result(self, process, job):
        stdout, stderr = process.communicate(timeout=20)
        self.assertEqual(process.returncode, 0, (stdout, stderr))
        return json.loads(Path(job["result"]).read_bytes())

    def test_native_two_process_shared_quota_cannot_overreserve(self):
        self.native(max_tokens=200, max_usage=200)
        one = self.child("contend_reservations", admit(usage=60), "contend-1")
        two = self.child("contend_reservations", admit("op-2", "a2", usage=60), "contend-2")
        for process, job in (one, two):
            _await(job["ready"])
        _write(self.root / "go", True)
        results = [self.result(*child) for child in (one, two)]
        self.assertEqual(sorted(r["reason"] for r in results), ["reserved", "usage_allowance"])
        self.assertEqual(g._accounting(self.state(), "usage"), 60)

    def test_native_competing_claims_grant_dispatch_once(self):
        self.native()
        self.issue(admit(), "reserved")
        command = dict(kind="claim", attempt_id="attempt-1")
        one = self.child("contend_claim", command, "same-claim")
        two = self.child("contend_claim", command, "same-claim")
        for process, job in (one, two):
            _await(job["ready"])
        _write(self.root / "go", True)
        results = [self.result(*child) for child in (one, two)]
        self.assertEqual(sum(r["dispatch_allowed"] for r in results), 1)
        self.assertFalse(self.store.lookup("same-claim").dispatch_allowed)

    def test_native_process_death_before_and_after_real_reservation_commit(self):
        for mode in ("before_commit", "after_commit"):
            with self.subTest(mode=mode):
                self.native()
                process, job = self.child(mode, admit(), mode)
                _await(job["ready"])
                marker = json.loads(Path(job["ready"]).read_bytes())
                process.kill()
                process.communicate(timeout=15)
                self.assertNotEqual(process.returncode, 0)
                _KILLS.append(marker)
                result = self.store.lookup(mode)
                self.assertEqual(result is not None, mode == "after_commit")
                self.assertEqual(g._accounting(self.state(), "usage"), 20 if result else 0)
                if result:
                    self.assertFalse(result.dispatch_allowed)

    def test_native_lost_claim_response_keeps_reservation_and_denies_redispatch(self):
        self.native()
        self.issue(admit(), "reserved")
        process, job = self.child("lost_response", dict(kind="claim", attempt_id="attempt-1"), "lost-claim")
        self.assertEqual(self.result(process, job)["reason"], "commit_outcome_unknown")
        self.assertFalse(self.store.lookup("lost-claim").dispatch_allowed)
        self.issue(dict(kind="claim", attempt_id="attempt-1"), "dispatch_already_claimed")
        self.assertEqual(g._accounting(self.state(), "usage"), 20)
        self.assertEqual(self.state()["attempts"]["attempt-1"]["status"], "running")

    def test_native_restart_replays_exact_state_and_derived_narrative(self):
        self.native()
        self.start()
        self.issue(settle(tokens=None), "outcome_unknown")
        before = self.store.recover()
        process, job = self.child("recover")
        after = self.result(process, job)
        self.assertEqual(after, dict(head=asdict(before.head), state=before.state, narrative=before.narrative))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--persistence-sha256", required=True)
    parser.add_argument("--governor-sha256", required=True)
    parser.add_argument("--child", type=Path)
    args = parser.parse_args()
    _capsule(args.persistence_sha256, args.governor_sha256)
    sys.addaudithook(_guard)
    if args.child:
        _child(json.loads(args.child.read_bytes()))
        return 0
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GovernorTests))
    print(json.dumps(dict(status="PASS" if result.wasSuccessful() and not _VIOLATIONS else "FAIL",
        tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
        source_sha256=_PINS, test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=sys.version, sqlite=sqlite3.sqlite_version, process_kill_evidence=_KILLS,
        observation_guard_violations=_VIOLATIONS, loaded_capsule_modules=sorted(_PINS),
        live_repository_tested=False, provider_calls=0, external_worker_dispatches=0), sort_keys=True))
    return 0 if result.wasSuccessful() and not _VIOLATIONS else 1


if __name__ == "__main__":
    raise SystemExit(main())
