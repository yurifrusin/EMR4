"""Closed, replayed recovery governor journal, explicitly separate from v1.

This module performs no observations or effects. The trusted caller verifies
policy, human authority, usage-window and settlement evidence before submitting
them. A string digest records that evidence; it does not authenticate it. G1D's
provenance boundary and a dispatch adapter remain separate requirements.

One store coordinates one shared account/quota/window. All cooperating workers
must use that store. Reservations are conservative until an authoritative final
usage receipt confirms that the worker stopped. An observation can acknowledge
only settled attempts whose charges it actually includes; it cannot free live
or uncertain reservations. Dollar estimates never determine admission/fallback.

The recovery envelope admits repair work only. Deadlines/no-progress limits are
checked at every event; callers must also enforce a running worker's deadline.
This library neither starts nor kills a worker. No automatic v1 migration exists.
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
import re

JOURNAL_VERSION = "ariadne.clockwork_governor_journal.v2"
GENESIS = "sha256:" + "0" * 64
MAX_ENTRIES = 4096
MAX_INT = (1 << 63) - 1
MAX_DURATION_NS = 86_400_000_000_000
ACTIONS = frozenset({"read", "repair_edit", "recovery_publish"})
KINDS = frozenset({"configure", "observe_usage", "set_gate", "admit", "claim", "progress", "settle", "stop", "tick"})
LIVE = frozenset({"reserved", "running", "quarantined"})


class GovernorError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def need(value: bool, code: str = "invalid_command") -> None:
    if not value:
        raise GovernorError(code)


def integer(value, lo=0, hi=MAX_INT):
    return type(value) is int and lo <= value <= hi


def label(value):
    return type(value) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value) is not None


def digest(value):
    return type(value) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def keys(value, names):
    need(type(value) is dict and set(value) == set(names.split()))
    return value


def canonical(value) -> bytes:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        need(len(raw) <= 65536)
        return raw
    except (ValueError, TypeError, RecursionError) as error:
        raise GovernorError("invalid_command") from error


def document(raw: bytes) -> dict:
    def pairs(rows):
        value = {}
        for key, item in rows:
            need(key not in value)
            value[key] = item
        return value

    def constant(value):
        raise GovernorError("invalid_command")

    need(type(raw) is bytes and len(raw) <= 65536)
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
        need(type(value) is dict and canonical(value) == raw)
        return value
    except (ValueError, TypeError, RecursionError, UnicodeError) as error:
        raise GovernorError("invalid_command") from error


def _labels(value, maximum=32):
    need(type(value) is list and 1 <= len(value) <= maximum
         and all(label(v) for v in value) and len(set(value)) == len(value))


def validate_policy(value):
    keys(value, "envelope_id owner scope_digest account quota_pool window_id units window_start_ns window_end_ns "
         "deadline_ns max_operation_ns max_no_progress_ns max_usage_age_ns max_no_progress_events max_wip max_depth "
         "max_attempts_per_operation max_attempts_total max_tokens max_usage authorities")
    need(all(label(value[k]) for k in ("envelope_id", "owner", "account", "quota_pool", "window_id", "units")))
    need(digest(value["scope_digest"]))
    need(all(integer(value[k]) for k in ("window_start_ns", "window_end_ns", "deadline_ns")))
    need(value["window_start_ns"] < value["window_end_ns"])
    for key, maximum in (("max_operation_ns", MAX_DURATION_NS), ("max_no_progress_ns", MAX_DURATION_NS),
                         ("max_usage_age_ns", 3_600_000_000_000), ("max_no_progress_events", 1024), ("max_wip", 64), ("max_depth", 16),
                         ("max_attempts_per_operation", 1024), ("max_attempts_total", 1024),
                         ("max_tokens", 10**12), ("max_usage", 10**12)):
        need(integer(value[key], 1, maximum))
    need(type(value["authorities"]) is list and len(value["authorities"]) <= 8)
    ids = set()
    for authority in value["authorities"]:
        keys(authority, "authority_id issuer source_digest operations actions expires_ns")
        need(label(authority["authority_id"]) and authority["authority_id"] not in ids
             and authority["issuer"] == value["owner"] and digest(authority["source_digest"])
             and integer(authority["expires_ns"], 1))
        _labels(authority["operations"])
        _labels(authority["actions"], 3)
        need(set(authority["actions"]) <= ACTIONS)
        ids.add(authority["authority_id"])


def validate_command(command):
    need(type(command) is dict and type(command.get("kind")) is str and command["kind"] in KINDS)
    kind = command["kind"]
    if kind == "configure":
        keys(command, "kind policy")
        validate_policy(command["policy"])
    elif kind == "observe_usage":
        keys(command, "kind account quota_pool window_id units window_start_ns window_end_ns observed_ns "
             "fresh_until_ns remaining evidence_digest accounted_attempts")
        need(all(label(command[k]) for k in ("account", "quota_pool", "window_id", "units")))
        need(all(integer(command[k]) for k in ("window_start_ns", "window_end_ns", "observed_ns",
                                               "fresh_until_ns", "remaining")))
        need(command["window_start_ns"] <= command["observed_ns"] < command["fresh_until_ns"] <= command["window_end_ns"])
        need(digest(command["evidence_digest"]) and type(command["accounted_attempts"]) is list
             and len(command["accounted_attempts"]) <= 1024
             and all(label(v) for v in command["accounted_attempts"])
             and len(set(command["accounted_attempts"])) == len(command["accounted_attempts"]))
    elif kind == "set_gate":
        keys(command, "kind status evidence_digest")
        need(type(command["status"]) is str and command["status"] in {"red", "green", "unknown"}
             and digest(command["evidence_digest"]))
    elif kind == "admit":
        keys(command, "kind operation_id task_id attempt_id parent_operation_id worker_id task_kind action risk authority_id tokens usage")
        need(all(label(command[k]) for k in ("operation_id", "task_id", "attempt_id", "worker_id")))
        need(command["parent_operation_id"] is None or label(command["parent_operation_id"]))
        need(command["authority_id"] is None or label(command["authority_id"]))
        need(type(command["task_kind"]) is str and command["task_kind"] in {"repair", "feature"})
        need(type(command["action"]) is str and command["action"] in ACTIONS)
        need(type(command["risk"]) is str and command["risk"] in {"low", "high"})
        need(integer(command["tokens"], 1, 10**12) and integer(command["usage"], 1, 10**12))
    elif kind == "claim":
        keys(command, "kind attempt_id")
        need(label(command["attempt_id"]))
    elif kind == "progress":
        keys(command, "kind attempt_id value evidence_digest")
        need(label(command["attempt_id"]) and integer(command["value"]) and digest(command["evidence_digest"]))
    elif kind == "settle":
        keys(command, "kind attempt_id disposition tokens usage worker_stopped evidence_digest")
        need(label(command["attempt_id"]) and type(command["disposition"]) is str
             and command["disposition"] in {"completed", "failed"})
        need(all(command[k] is None or integer(command[k], 0, 10**12) for k in ("tokens", "usage")))
        need(type(command["worker_stopped"]) is bool and digest(command["evidence_digest"]))
    elif kind == "stop":
        keys(command, "kind attempt_id reason evidence_digest")
        need(label(command["attempt_id"]) and type(command["reason"]) is str
             and command["reason"] in {"owner_stop", "worker_lost"} and digest(command["evidence_digest"]))
    else:
        keys(command, "kind")
    # Reject non-JSON aliases/types and copy before any state change.
    need(document(canonical(command)) == command)


def _accounting(state, dimension, *, observation=False):
    acknowledged = set(state["observation"]["accounted_attempts"]) if observation and state["observation"] else set()
    return sum(max(attempt["reserved_" + dimension], attempt["reported_" + dimension]) if attempt["status"] in LIVE else attempt["actual_" + dimension]
               for identity, attempt in state["attempts"].items() if identity not in acknowledged)


def _quarantine(attempt, reason):
    if attempt["status"] in {"reserved", "running"}:
        attempt.update(status="quarantined", stop_reason=reason)


def _sweep(state, now):
    policy = state["policy"]
    reason = None
    if now >= policy["deadline_ns"]:
        reason = "envelope_deadline"
    elif now >= policy["window_end_ns"]:
        reason = "usage_window_closed"
    elif _accounting(state, "tokens") > policy["max_tokens"]:
        reason = "token_budget_exceeded"
    elif _accounting(state, "usage") > policy["max_usage"]:
        reason = "usage_budget_exceeded"
    if reason:
        state["halt_reason"] = state["halt_reason"] or reason
    for attempt in state["attempts"].values():
        operation = state["operations"][attempt["operation_id"]]
        reason = state["halt_reason"] or operation["terminal_reason"]
        if reason is None and state["global_gate"] == "unknown":
            reason = "global_state_unknown"
        if reason is None and now >= operation["deadline_ns"]:
            reason = "operation_deadline"
        if reason is None and (now - operation["last_progress_ns"] >= policy["max_no_progress_ns"]
                               or operation["no_progress_events"] >= policy["max_no_progress_events"]):
            reason = "no_progress"
        if reason:
            _quarantine(attempt, reason)
    # Parent precedes child by admission; repeat for nested stopped ancestors.
    for _ in range(policy["max_depth"]):
        for attempt in state["attempts"].values():
            parent = state["operations"][attempt["operation_id"]]["spec"]["parent_operation_id"]
            if parent is not None:
                parent_attempt = state["attempts"][state["operations"][parent]["last_attempt"]]
                if parent_attempt["status"] != "running":
                    _quarantine(attempt, "parent_not_running")


def _outcome(accepted, reason, attempt_id=None):
    return {"accepted": accepted, "reason": reason, "attempt_id": attempt_id}


def transition(before, command, now):
    """Return a new projection and structured result; malformed input raises."""
    validate_command(command)
    need(integer(now), "clock_regressed")
    kind = command["kind"]
    if before is None:
        if kind != "configure":
            return None, _outcome(False, "not_configured")
        policy = copy.deepcopy(command["policy"])
        if not now < policy["deadline_ns"] <= now + MAX_DURATION_NS:
            return None, _outcome(False, "invalid_deadline")
        if not policy["window_start_ns"] <= now < policy["window_end_ns"]:
            return None, _outcome(False, "usage_window_closed")
        state = {"policy": policy, "global_gate": "red", "gate_evidence": policy["scope_digest"],
                 "observation": None, "operations": {}, "attempts": {}, "halt_reason": None, "last_ns": now}
        return state, _outcome(True, "configured")
    need(now >= before["last_ns"], "clock_regressed")
    state = copy.deepcopy(before)
    state["last_ns"] = now
    _sweep(state, now)
    policy = state["policy"]
    if kind == "configure":
        return state, _outcome(False, "already_configured")
    if kind == "tick":
        return state, _outcome(True, state["halt_reason"] or "checked")
    if kind == "observe_usage":
        if any(command[k] != policy[k] for k in ("account", "quota_pool", "window_id", "units", "window_start_ns", "window_end_ns")):
            return state, _outcome(False, "usage_scope_mismatch")
        if not command["observed_ns"] <= now < command["fresh_until_ns"] or command["fresh_until_ns"] - command["observed_ns"] > policy["max_usage_age_ns"]:
            return state, _outcome(False, "usage_unknown")
        old = state["observation"]
        if old and (command["observed_ns"] <= old["observed_ns"]
                    or not set(old["accounted_attempts"]) <= set(command["accounted_attempts"])):
            return state, _outcome(False, "usage_observation_regressed")
        if any(identity not in state["attempts"] or state["attempts"][identity]["status"] in LIVE
               or state["attempts"][identity]["settled_ns"] > command["observed_ns"]
               for identity in command["accounted_attempts"]):
            return state, _outcome(False, "unresolved_usage_acknowledged")
        state["observation"] = copy.deepcopy(command)
        return state, _outcome(True, "usage_observed")
    if kind == "set_gate":
        state.update(global_gate=command["status"], gate_evidence=command["evidence_digest"])
        _sweep(state, now)
        return state, _outcome(True, "gate_observed")
    if kind == "admit":
        return _admit(state, command, now)
    identity = command["attempt_id"]
    attempt = state["attempts"].get(identity)
    if attempt is None:
        return state, _outcome(False, "attempt_unknown", identity)
    operation = state["operations"][attempt["operation_id"]]
    if kind == "stop" and command["reason"] == "owner_stop":
        # Owner authority stops the operation even between settled attempts,
        # or when the request names an older attempt of a currently running retry.
        operation["terminal_reason"] = "owner_stop"
        _sweep(state, now)
        return state, _outcome(True, "owner_stop", identity)
    if attempt["status"] not in LIVE:
        return state, _outcome(False, "attempt_settled", identity)
    if kind == "claim":
        if attempt["status"] != "reserved":
            return state, _outcome(False, attempt["stop_reason"] or "dispatch_already_claimed", identity)
        observation = state["observation"]
        if observation is None or now >= observation["fresh_until_ns"]:
            return state, _outcome(False, "usage_unknown", identity)
        if _accounting(state, "usage", observation=True) > observation["remaining"]:
            return state, _outcome(False, "usage_allowance", identity)
        spec = operation["spec"]
        if spec["risk"] == "high" or spec["action"] == "recovery_publish":
            authority = next((a for a in policy["authorities"] if a["authority_id"] == attempt["authority_id"]), None)
            if authority is None or now >= authority["expires_ns"]:
                return state, _outcome(False, "human_authority_required", identity)
        attempt.update(status="running", claimed_ns=now)
        return state, _outcome(True, "dispatch_claimed", identity)
    if kind == "stop":
        _quarantine(attempt, command["reason"])
        _sweep(state, now)
        return state, _outcome(True, attempt["stop_reason"], identity)
    if kind == "progress":
        if attempt["status"] != "running":
            return state, _outcome(False, attempt["stop_reason"] or "dispatch_not_claimed", identity)
        if command["value"] < operation["progress"]:
            return state, _outcome(False, "progress_regressed", identity)
        if command["value"] == operation["progress"]:
            operation["no_progress_events"] += 1
        else:
            operation.update(progress=command["value"], last_progress_ns=now, no_progress_events=0)
        operation["progress_evidence"] = command["evidence_digest"]
        _sweep(state, now)
        return state, _outcome(attempt["status"] == "running", attempt["stop_reason"] or "progress_recorded", identity)
    if any(command[k] is not None and command[k] < attempt["reported_" + k] for k in ("tokens", "usage")):
        return state, _outcome(False, "usage_regressed", identity)
    for dimension in ("tokens", "usage"):
        if command[dimension] is not None:
            attempt["reported_" + dimension] = command[dimension]
    _sweep(state, now)
    if not command["worker_stopped"] or command["tokens"] is None or command["usage"] is None:
        _quarantine(attempt, "outcome_unknown")
        _sweep(state, now)
        return state, _outcome(False, "outcome_unknown", identity)
    if attempt["claimed_ns"] is None and (command["disposition"] == "completed" or command["tokens"] != 0 or command["usage"] != 0):
        _quarantine(attempt, "unclaimed_execution")
        operation["terminal_reason"] = "unclaimed_execution"
        _sweep(state, now)
        return state, _outcome(False, "unclaimed_execution", identity)
    if any(a["status"] in LIVE and state["operations"][a["operation_id"]]["spec"]["parent_operation_id"] == attempt["operation_id"]
           for a in state["attempts"].values()):
        return state, _outcome(False, "children_unresolved", identity)
    attempt.update(status=command["disposition"], actual_tokens=command["tokens"], actual_usage=command["usage"],
                   settled_ns=now, settlement_evidence=command["evidence_digest"])
    if command["disposition"] == "failed":
        operation["no_progress_events"] += 1
    _sweep(state, now)
    return state, _outcome(True, "usage_reconciled", identity)


def _admit(state, command, now):
    identity = command["attempt_id"]

    def reject(reason):
        return state, _outcome(False, reason, identity)

    policy = state["policy"]
    if state["halt_reason"]:
        return reject(state["halt_reason"])
    if state["global_gate"] == "unknown":
        return reject("global_state_unknown")
    if command["task_kind"] != "repair":
        return reject("global_red_repair_only" if state["global_gate"] == "red" else "recovery_envelope_only")
    # Publication always requires human scope, even if a caller labels it low risk.
    if command["risk"] == "high" or command["action"] == "recovery_publish":
        authority = next((a for a in policy["authorities"] if a["authority_id"] == command["authority_id"]), None)
        if authority is None or not (now < authority["expires_ns"] and command["operation_id"] in authority["operations"]
                                     and command["action"] in authority["actions"]):
            return reject("human_authority_required")
    if identity in state["attempts"]:
        return reject("attempt_id_used")
    if len(state["attempts"]) >= policy["max_attempts_total"]:
        return reject("attempt_budget")
    spec = {k: command[k] for k in ("task_id", "parent_operation_id", "worker_id", "task_kind", "action", "risk")}
    operation = state["operations"].get(command["operation_id"])
    if operation:
        if operation["terminal_reason"]:
            return reject(operation["terminal_reason"])
        if operation["spec"] != spec:
            return reject("operation_binding_changed")
        previous = state["attempts"][operation["last_attempt"]]
        if previous["status"] != "failed":
            return reject("operation_unresolved" if previous["status"] in LIVE else "operation_completed")
        if operation["attempt_count"] >= policy["max_attempts_per_operation"]:
            return reject("retry_budget")
        if now >= operation["deadline_ns"]:
            return reject("operation_deadline")
        if now - operation["last_progress_ns"] >= policy["max_no_progress_ns"] or operation["no_progress_events"] >= policy["max_no_progress_events"]:
            return reject("no_progress")
    parent = command["parent_operation_id"]
    depth = 1
    if parent is not None:
        parent_operation = state["operations"].get(parent)
        if parent_operation is None or state["attempts"][parent_operation["last_attempt"]]["status"] != "running":
            return reject("parent_not_running")
        depth = parent_operation["depth"] + 1
    if depth > policy["max_depth"]:
        return reject("stack_limit")
    if sum(a["status"] in LIVE for a in state["attempts"].values()) >= policy["max_wip"]:
        return reject("wip_limit")
    observation = state["observation"]
    if observation is None or not observation["observed_ns"] <= now < observation["fresh_until_ns"]:
        return reject("usage_unknown")
    if command["tokens"] + _accounting(state, "tokens") > policy["max_tokens"]:
        return reject("token_budget")
    if command["usage"] + _accounting(state, "usage") > policy["max_usage"]:
        return reject("usage_budget")
    if command["usage"] + _accounting(state, "usage", observation=True) > observation["remaining"]:
        return reject("usage_allowance")
    if operation is None:
        authority_expiry = authority["expires_ns"] if command["risk"] == "high" or command["action"] == "recovery_publish" else MAX_INT
        operation = {"spec": spec, "depth": depth, "deadline_ns": min(policy["deadline_ns"], policy["window_end_ns"], authority_expiry, now + policy["max_operation_ns"]),
                     "attempt_count": 0, "last_attempt": None, "last_progress_ns": now, "progress": 0,
                     "no_progress_events": 0, "progress_evidence": None, "terminal_reason": None}
        state["operations"][command["operation_id"]] = operation
    elif command["risk"] == "high" or command["action"] == "recovery_publish":
        # A retry may use another applicable human grant, but cannot inherit a
        # longer execution lifetime from its predecessor's grant.
        operation["deadline_ns"] = min(operation["deadline_ns"], authority["expires_ns"])
    operation["attempt_count"] += 1
    operation["last_attempt"] = identity
    state["attempts"][identity] = {"operation_id": command["operation_id"], "status": "reserved", "stop_reason": None,
        "reserved_tokens": command["tokens"], "reserved_usage": command["usage"], "actual_tokens": None,
        "actual_usage": None, "reported_tokens": 0, "reported_usage": 0, "settled_ns": None,
        "settlement_evidence": None, "authority_id": command["authority_id"], "claimed_ns": None}
    return state, _outcome(True, "reserved", identity)


@dataclass(frozen=True, slots=True)
class Entry:
    payload: bytes
    digest: str

    @property
    def value(self):
        return document(self.payload)

    @property
    def sequence(self):
        return self.value["sequence"]

    @property
    def previous_digest(self):
        return self.value["previous_digest"]


@dataclass(frozen=True, slots=True)
class Recovery:
    entries: tuple[Entry, ...]
    state_bytes: bytes

    @property
    def state(self):
        return json.loads(self.state_bytes)

    @property
    def narrative(self):
        need(replay(self.entries).state_bytes == self.state_bytes, "journal_corrupt")
        state = self.state
        if state is None:
            return "Recovery governor: unconfigured."
        reserved = sum(a["status"] == "reserved" for a in state["attempts"].values())
        running = sum(a["status"] == "running" for a in state["attempts"].values())
        quarantined = sum(a["status"] == "quarantined" for a in state["attempts"].values())
        return (f"Recovery governor: {state['global_gate']}; reserved {reserved}; running {running}; quarantined {quarantined}. "
                f"Tokens charged/reserved: {_accounting(state, 'tokens')}; usage charged/reserved: {_accounting(state, 'usage')}. "
                f"Stop: {state['halt_reason'] or 'none'}. Journal entries: {len(self.entries)}.")


def _state_bytes(state):
    # Projection grows with bounded attempts; event size has its separate bound.
    return json.dumps(state, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _finish_outcome(state, command, outcome):
    outcome["not_after_ns"] = None
    if outcome["accepted"] and command["kind"] in {"admit", "claim"}:
        attempt = state["attempts"][command["attempt_id"]]
        operation = state["operations"][attempt["operation_id"]]
        outcome["not_after_ns"] = min(operation["deadline_ns"], state["observation"]["fresh_until_ns"],
                                       operation["last_progress_ns"] + state["policy"]["max_no_progress_ns"])
    outcome["state_digest"] = "sha256:" + hashlib.sha256(_state_bytes(state)).hexdigest()
    return outcome


def append(recovered: Recovery, command: dict, now: int, request_id: str) -> Entry:
    need(type(recovered) is Recovery and label(request_id) and integer(now))
    need(replay(recovered.entries) == recovered, "journal_corrupt")
    need(len(recovered.entries) < MAX_ENTRIES, "journal_full")
    state, outcome = transition(recovered.state, command, now)
    _finish_outcome(state, command, outcome)
    value = {"schema_version": JOURNAL_VERSION, "sequence": len(recovered.entries) + 1,
             "previous_digest": recovered.entries[-1].digest if recovered.entries else GENESIS,
             "at_ns": now, "request_id": request_id, "command": command, "outcome": outcome}
    raw = canonical(value)
    return Entry(raw, "sha256:" + hashlib.sha256(raw).hexdigest())


def replay(entries: tuple[Entry, ...]) -> Recovery:
    need(type(entries) is tuple and len(entries) <= MAX_ENTRIES, "journal_corrupt")
    state, previous, stamp, requests = None, GENESIS, 0, set()
    for sequence, entry in enumerate(entries, 1):
        need(type(entry) is Entry and digest(entry.digest), "journal_corrupt")
        try:
            value = document(entry.payload)
            keys(value, "schema_version sequence previous_digest at_ns request_id command outcome")
            need(value["schema_version"] == JOURNAL_VERSION and type(value["sequence"]) is int
                 and value["sequence"] == sequence and value["previous_digest"] == previous
                 and integer(value["at_ns"], stamp) and label(value["request_id"])
                 and value["request_id"] not in requests, "journal_corrupt")
            state, outcome = transition(state, value["command"], value["at_ns"])
            _finish_outcome(state, value["command"], outcome)
            need(canonical(value["outcome"]) == canonical(outcome)
                 and entry.digest == "sha256:" + hashlib.sha256(entry.payload).hexdigest(), "journal_corrupt")
        except (GovernorError, KeyError, TypeError, ValueError, RecursionError) as error:
            raise GovernorError("journal_corrupt") from error
        requests.add(value["request_id"])
        stamp, previous = value["at_ns"], entry.digest
    return Recovery(entries, _state_bytes(state))
