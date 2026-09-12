"""Single-host persistence for the accepted, closed Clockwork journal.

The journal is the state authority. A SQLite transaction appends an immutable
entry and advances its checked head together; recovery always runs the accepted
reducer again. Narrative is a disposable projection of that recovered state.
No command is executed and no existing Clockwork writer is imported or enabled.

The caller supplies an ordinary file in a private, stable local directory.
SQLite rollback journaling and EXTRA synchronization provide the commit point.
Process-death tests cover both sides of it; they are not power-loss or hostile
filesystem proofs. Storage/locking/flush guarantees depend on the local OS.
See https://www.sqlite.org/atomiccommit.html for those substrate assumptions.

Leases fence cooperating writers within the same atomic write transaction.
Expiry is checked again immediately before commit, under SQLite's writer lock;
this is not a promise about wall-clock time after a slow disk flush completes.
A process with direct write access to the database is outside this boundary.
An uncertain response is resolved by lookup(request_id), never blind retry.
"""
from __future__ import annotations

from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import time

from orchestration_harness.clockwork_journal import (
    GENESIS_PREVIOUS_DIGEST,
    JournalEntry,
    ReplayResult,
    append_entry,
    canonical_entry_bytes,
    replay,
)
from orchestration_harness.clockwork_state import (
    COMMAND_SCHEMA_VERSION,
    EVENT_SCHEMA_VERSION,
    STATE_SCHEMA_VERSION,
    ClockworkCommand,
    ClockworkEvent,
    ClockworkState,
    InvalidTransition,
    TransitionResult,
)

STORE_SCHEMA_VERSION = "ariadne.clockwork_store.v1"
_APPLICATION_ID = 0x434C4B31
_MAX_INT = (1 << 63) - 1
_MAX_ENTRIES = 4096
_MAX_TTL_NS = 3_600_000_000_000
_SCHEMA = (
    "CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK(id=1), version TEXT NOT NULL, "
    "store_id TEXT NOT NULL, head_sequence INTEGER NOT NULL, head_digest TEXT NOT NULL, "
    "fence INTEGER NOT NULL, owner TEXT, token TEXT, expires_ns INTEGER NOT NULL, "
    "last_ns INTEGER NOT NULL) STRICT",
    "CREATE TABLE entries (sequence INTEGER PRIMARY KEY, request_id TEXT NOT NULL UNIQUE, "
    "payload BLOB NOT NULL, digest TEXT NOT NULL, fence INTEGER NOT NULL) STRICT",
    "CREATE TRIGGER entries_no_update BEFORE UPDATE ON entries BEGIN "
    "SELECT RAISE(ABORT, 'append_only_journal'); END",
    "CREATE TRIGGER entries_no_delete BEFORE DELETE ON entries BEGIN "
    "SELECT RAISE(ABORT, 'append_only_journal'); END",
)


class PersistenceError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _need(condition: bool, code: str) -> None:
    if not condition:
        raise PersistenceError(code)


def _integer(value: object, minimum: int = 0, maximum: int = _MAX_INT) -> bool:
    return type(value) is int and minimum <= value <= maximum


def _label(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", value) is not None


def _digest(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def _hex(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _now_ns() -> int:
    return time.time_ns()


@dataclass(frozen=True, slots=True)
class JournalHead:
    sequence: int
    digest: str


@dataclass(frozen=True, slots=True)
class Lease:
    store_id: str
    owner: str
    fence: int
    token: str = field(repr=False)
    expires_ns: int


@dataclass(frozen=True, slots=True)
class Snapshot:
    replayed: ReplayResult

    @property
    def head(self) -> JournalHead:
        return JournalHead(self.replayed.next_sequence - 1, self.replayed.previous_digest)

    @property
    def state(self) -> ClockworkState:
        return self.replayed.state

    @property
    def narrative(self) -> str:
        # Derive again so a supplied/forged cached result cannot become authority.
        result = replay(self.replayed.validated_journal)
        _need(result.rejection is None and result == self.replayed, "store_corrupt")
        text = f"Clockwork state: {result.state.value}. Journal entries: {result.next_sequence - 1}."
        if result.validated_journal:
            last = result.validated_journal[-1]
            outcome = ("accepted" if last.stored_result.invalid is None else
                       "rejected: " + last.stored_result.invalid.code)
            text += f" Last attempt: {last.event.value}/{last.command.value}, {outcome}."
        return text


@dataclass(frozen=True, slots=True)
class CommitResult:
    entry: JournalEntry
    already_committed: bool

    @property
    def accepted(self) -> bool:
        """False means an invalid attempt was audited without advancing state."""
        return self.entry.stored_result.invalid is None


def _decode(raw: bytes, digest: str) -> JournalEntry:
    def pairs(items):
        out = {}
        for key, value in items:
            _need(key not in out, "store_corrupt")
            out[key] = value
        return out

    def reject_constant(value):
        raise PersistenceError("store_corrupt")

    _need(type(raw) is bytes and len(raw) <= 4096 and _digest(digest), "store_corrupt")
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)
        _need(type(value) is dict and set(value) == {
            "schema_version", "sequence", "previous_digest", "event", "command", "stored_result"
        }, "store_corrupt")
        result = value["stored_result"]
        _need(type(result) is dict and set(result) == {
            "state_schema_version", "event_schema_version", "command_schema_version",
            "state", "command", "invalid"
        }, "store_corrupt")
        _need(result["state_schema_version"] == STATE_SCHEMA_VERSION
              and result["event_schema_version"] == EVENT_SCHEMA_VERSION
              and result["command_schema_version"] == COMMAND_SCHEMA_VERSION, "store_corrupt")
        _need(result["invalid"] is None or (type(result["invalid"]) is str
              and result["invalid"] == "invalid_transition"), "store_corrupt")
        _need(all(type(value[k]) is str for k in ("schema_version", "previous_digest", "event", "command"))
              and _integer(value["sequence"], 1), "store_corrupt")
        _need(type(result["state"]) is str and type(result["command"]) is str, "store_corrupt")
        stored = TransitionResult(ClockworkState(result["state"]), ClockworkCommand(result["command"]),
                                  None if result["invalid"] is None else InvalidTransition(result["invalid"]))
        entry = JournalEntry(value["schema_version"], value["sequence"], value["previous_digest"],
                             ClockworkEvent(value["event"]), ClockworkCommand(value["command"]), stored, digest)
        _need(canonical_entry_bytes(entry) == raw, "store_corrupt")
        return entry
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise PersistenceError("store_corrupt") from error


def _ordinary(path: Path, *, missing: bool = False, directory: bool = False) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        _need(missing, "missing_store")
        return
    _need(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
          "unsafe_path")
    _need(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode), "unsafe_path")
    if not directory:
        _need(info.st_nlink == 1 and info.st_size <= 64 * 1024 * 1024, "unsafe_path")


class ClockworkStore:
    """Each operation opens a short connection; no live handle crosses a fork."""

    _schema_version = STORE_SCHEMA_VERSION
    _user_version = 1

    def __init__(self, path: Path):
        _need(isinstance(path, Path) and path.is_absolute() and ".." not in path.parts, "unsafe_path")
        _need(not str(path).startswith(("//", "\\\\")), "unsafe_path")
        self.path = path

    def _check_path(self, *, missing: bool = False) -> None:
        for parent in reversed(self.path.parents):
            _ordinary(parent, directory=True)
        _ordinary(self.path, missing=missing)
        _ordinary(self.path.with_name(self.path.name + "-journal"), missing=True)
        for suffix in ("-wal", "-shm"):
            try:
                self.path.with_name(self.path.name + suffix).lstat()
            except FileNotFoundError:
                continue
            raise PersistenceError("unsafe_path")

    def _connect(self) -> sqlite3.Connection:
        self._check_path()
        db = sqlite3.connect(self.path.as_uri() + "?mode=rw", uri=True,
                             isolation_level=None, timeout=2.0)
        try:
            _need(db.execute("PRAGMA journal_mode").fetchone() == ("delete",), "store_corrupt")
            db.execute("PRAGMA trusted_schema=OFF")
            db.execute("PRAGMA synchronous=EXTRA")
            _need(db.execute("PRAGMA synchronous").fetchone() == (3,), "storage_error")
            return db
        except BaseException:
            db.close()
            raise

    @contextmanager
    def _transaction(self, *, write: bool = False):
        db = None
        committing = False
        try:
            db = self._connect()
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db
            committing = True
            db.execute("COMMIT")
        except BaseException as error:
            if db is not None and db.in_transaction:
                with suppress(sqlite3.Error):
                    db.execute("ROLLBACK")
            if committing and isinstance(error, Exception):
                raise PersistenceError("commit_outcome_unknown") from error
            if isinstance(error, sqlite3.Error):
                code = getattr(error, "sqlite_errorcode", 0) & 0xFF
                reason = ("store_busy" if code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED) else
                          "store_full" if code == sqlite3.SQLITE_FULL else "storage_error")
                raise PersistenceError(reason) from error
            raise
        finally:
            if db is not None:
                db.close()

    @classmethod
    def create(cls, path: Path) -> ClockworkStore:
        store = cls(path)
        store._check_path(missing=True)
        try:
            path.with_name(path.name + "-journal").lstat()
        except FileNotFoundError:
            pass
        else:
            raise PersistenceError("unsafe_path")
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        except FileExistsError as error:
            raise PersistenceError("store_exists") from error
        os.close(fd)
        # A failed creation leaves an explicit incomplete file, never an
        # automatic reset of a pre-existing or partially initialized store.
        with store._transaction(write=True) as db:
            for statement in _SCHEMA:
                db.execute(statement)
            now = _now_ns()
            _need(_integer(now), "clock_regressed")
            db.execute(f"PRAGMA application_id={_APPLICATION_ID}")
            db.execute(f"PRAGMA user_version={store._user_version}")
            db.execute("INSERT INTO metadata VALUES (1,?,?,?,?,?,?,?,?,?)", (
                store._schema_version, secrets.token_hex(32), 0, GENESIS_PREVIOUS_DIGEST,
                0, None, None, 0, now))
        return store

    def _load(self, db):
        _need(db.execute("PRAGMA application_id").fetchone() == (_APPLICATION_ID,)
              and db.execute("PRAGMA user_version").fetchone() == (self._user_version,), "store_corrupt")
        schema = db.execute("SELECT sql FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*'").fetchall()
        _need(len(schema) == len(_SCHEMA) and {row[0] for row in schema} == set(_SCHEMA), "store_corrupt")
        rows = db.execute("SELECT * FROM metadata LIMIT 2").fetchall()
        _need(len(rows) == 1 and len(rows[0]) == 10, "store_corrupt")
        keys = ("id", "version", "store_id", "sequence", "digest", "fence", "owner", "token", "expires", "last")
        meta = dict(zip(keys, rows[0]))
        _need(meta["id"] == 1 and meta["version"] == self._schema_version and _hex(meta["store_id"]), "store_corrupt")
        _need(_integer(meta["sequence"], maximum=_MAX_ENTRIES) and _digest(meta["digest"])
              and _integer(meta["fence"]) and _integer(meta["expires"]) and _integer(meta["last"]), "store_corrupt")
        if meta["owner"] is None:
            _need(meta["token"] is None and meta["expires"] == 0, "store_corrupt")
        else:
            _need(_label(meta["owner"]) and _hex(meta["token"]) and meta["fence"] > 0
                  and meta["expires"] > 0, "store_corrupt")
        rows = db.execute("SELECT sequence,request_id,payload,digest,fence FROM entries "
                          "ORDER BY sequence LIMIT ?", (_MAX_ENTRIES + 1,)).fetchall()
        _need(len(rows) <= _MAX_ENTRIES, "store_corrupt")
        journal, requests, fence = [], {}, 0
        for sequence, request_id, payload, digest, entry_fence in rows:
            _need(_label(request_id) and request_id not in requests and
                  _integer(entry_fence, max(1, fence), meta["fence"]), "store_corrupt")
            entry = self._decode_entry(payload, digest, request_id, meta["last"])
            _need(sequence == entry.sequence, "store_corrupt")
            journal.append(entry)
            requests[request_id] = entry
            fence = entry_fence
        snapshot = self._recover_entries(tuple(journal))
        _need(snapshot.head == JournalHead(meta["sequence"], meta["digest"]), "store_corrupt")
        return meta, snapshot, requests

    @staticmethod
    def _decode_entry(payload, digest, request_id, last_ns):
        return _decode(payload, digest)

    @staticmethod
    def _recover_entries(entries):
        derived = replay(entries)
        _need(derived.rejection is None, "store_corrupt")
        return Snapshot(derived)

    @staticmethod
    def _commit_result(entry, already_committed):
        return CommitResult(entry, already_committed)

    @staticmethod
    def _stamp(meta) -> int:
        now = _now_ns()
        _need(_integer(now) and now >= meta["last"], "clock_regressed")
        meta["last"] = now
        return now

    @staticmethod
    def _lease(meta, lease: Lease, now: int) -> None:
        _need(type(lease) is Lease and _hex(lease.store_id) and _label(lease.owner)
              and _integer(lease.fence, 1) and _hex(lease.token) and _integer(lease.expires_ns, 1), "stale_lease")
        _need((lease.store_id, lease.owner, lease.fence, lease.token, lease.expires_ns) ==
              (meta["store_id"], meta["owner"], meta["fence"], meta["token"], meta["expires"])
              and now < meta["expires"], "stale_lease")

    def recover(self) -> Snapshot:
        with self._transaction() as db:
            _, snapshot, _ = self._load(db)
            return snapshot

    def lookup(self, request_id: str) -> CommitResult | None:
        _need(_label(request_id), "invalid_argument")
        with self._transaction() as db:
            _, _, requests = self._load(db)
            entry = requests.get(request_id)
            return None if entry is None else self._commit_result(entry, True)

    def acquire_lease(self, owner: str, ttl_ns: int) -> Lease:
        _need(_label(owner) and _integer(ttl_ns, 1, _MAX_TTL_NS), "invalid_argument")
        with self._transaction(write=True) as db:
            meta, _, _ = self._load(db)
            now = self._stamp(meta)
            _need(meta["owner"] is None or now >= meta["expires"], "lease_busy")
            _need(meta["fence"] < _MAX_INT and now <= _MAX_INT - ttl_ns, "invalid_argument")
            lease = Lease(meta["store_id"], owner, meta["fence"] + 1, secrets.token_hex(32), now + ttl_ns)
            self._stamp(meta)
            _need(meta["last"] < lease.expires_ns, "stale_lease")
            db.execute("UPDATE metadata SET fence=?,owner=?,token=?,expires_ns=?,last_ns=? WHERE id=1",
                       (lease.fence, owner, lease.token, lease.expires_ns, meta["last"]))
            return lease

    def renew_lease(self, lease: Lease, ttl_ns: int) -> Lease:
        _need(_integer(ttl_ns, 1, _MAX_TTL_NS), "invalid_argument")
        with self._transaction(write=True) as db:
            meta, _, _ = self._load(db)
            now = self._stamp(meta)
            self._lease(meta, lease, now)
            _need(now <= _MAX_INT - ttl_ns, "invalid_argument")
            renewed = Lease(lease.store_id, lease.owner, lease.fence, secrets.token_hex(32), now + ttl_ns)
            self._lease(meta, lease, self._stamp(meta))
            _need(meta["last"] < renewed.expires_ns, "stale_lease")
            db.execute("UPDATE metadata SET token=?,expires_ns=?,last_ns=? WHERE id=1",
                       (renewed.token, renewed.expires_ns, meta["last"]))
            return renewed

    def release_lease(self, lease: Lease) -> None:
        with self._transaction(write=True) as db:
            meta, _, _ = self._load(db)
            self._lease(meta, lease, self._stamp(meta))
            db.execute("UPDATE metadata SET owner=NULL,token=NULL,expires_ns=0,last_ns=? WHERE id=1", (meta["last"],))

    def append(self, lease: Lease, expected: JournalHead, request_id: str,
               event: ClockworkEvent, command: ClockworkCommand) -> CommitResult:
        _need(type(expected) is JournalHead and _integer(expected.sequence, maximum=_MAX_ENTRIES)
              and _digest(expected.digest) and _label(request_id)
              and type(event) is ClockworkEvent and type(command) is ClockworkCommand, "invalid_argument")
        with self._transaction(write=True) as db:
            meta, snapshot, requests = self._load(db)
            self._lease(meta, lease, self._stamp(meta))
            existing = requests.get(request_id)
            if existing is not None:
                _need(existing.event is event and existing.command is command
                      and expected == JournalHead(existing.sequence - 1, existing.previous_digest), "request_conflict")
                return CommitResult(existing, True)
            _need(expected == snapshot.head, "head_conflict")
            _need(meta["sequence"] < _MAX_ENTRIES, "store_full")
            derived = append_entry(snapshot.replayed.validated_journal, event, command)
            _need(derived.rejection is None, "store_corrupt")
            entry = derived.validated_journal[-1]
            db.execute("INSERT INTO entries VALUES (?,?,?,?,?)",
                       (entry.sequence, request_id, canonical_entry_bytes(entry), entry.digest, lease.fence))
            self._lease(meta, lease, self._stamp(meta))
            db.execute("UPDATE metadata SET head_sequence=?,head_digest=?,last_ns=? WHERE id=1",
                       (entry.sequence, entry.digest, meta["last"]))
            return CommitResult(entry, False)


def _governor():
    # v1 users retain their exact three-module boundary. v2 is opt-in, with no
    # automatic migration, reinterpretation or dependency on legacy writers.
    from orchestration_harness import clockwork_governor
    return clockwork_governor


@dataclass(frozen=True, slots=True)
class GovernorSnapshot:
    replayed: object

    @property
    def head(self):
        entries = self.replayed.entries
        return JournalHead(len(entries), entries[-1].digest if entries else GENESIS_PREVIOUS_DIGEST)

    @property
    def state(self):
        return self.replayed.state

    @property
    def narrative(self):
        return self.replayed.narrative


@dataclass(frozen=True, slots=True)
class GovernorCommitResult:
    entry: object
    already_committed: bool

    @property
    def accepted(self):
        return self.entry.value["outcome"]["accepted"]

    @property
    def reason(self):
        return self.entry.value["outcome"]["reason"]

    @property
    def dispatch_allowed(self):
        """Only a fresh, committed dispatch claim can be consumed once by a caller.

        Readback/duplicate invocation is evidence, never a second dispatch. The
        Admission first reserves resources; a separate claim rechecks current
        state under the lease and consumes the dispatch right. The trusted
        executor still owes authority verification and its deadline timer.
        No worker is run here; a lost claim response never licenses a retry.
        """
        return self.accepted and not self.already_committed and self.entry.value["command"]["kind"] == "claim"


class GovernorStore(ClockworkStore):
    """Explicit v2 journal, using v1's transaction, lease, fencing and head CAS."""

    _schema_version = "ariadne.clockwork_store.v2"
    _user_version = 2
    _storage_limit_bytes = 60 * 1024 * 1024

    def _connect(self):
        db = super()._connect()
        try:
            page_size = db.execute("PRAGMA page_size").fetchone()[0]
            _need(_integer(page_size, 512, 65536), "store_corrupt")
            maximum = self._storage_limit_bytes // page_size
            _need(db.execute(f"PRAGMA max_page_count={maximum}").fetchone() == (maximum,), "store_full")
            return db
        except BaseException:
            db.close()
            raise

    @staticmethod
    def _decode_entry(payload, digest, request_id, last_ns):
        g = _governor()
        try:
            entry = g.Entry(payload, digest)
            value = entry.value
            _need(value.get("request_id") == request_id and g.integer(value.get("at_ns"), 0, last_ns), "store_corrupt")
            return entry
        except (g.GovernorError, KeyError, TypeError) as error:
            raise PersistenceError("store_corrupt") from error

    @staticmethod
    def _recover_entries(entries):
        g = _governor()
        try:
            return GovernorSnapshot(g.replay(entries))
        except g.GovernorError as error:
            raise PersistenceError("store_corrupt") from error

    @staticmethod
    def _commit_result(entry, already_committed):
        return GovernorCommitResult(entry, already_committed)

    def append(self, lease: Lease, expected: JournalHead, request_id: str, command: dict) -> GovernorCommitResult:
        g = _governor()
        _need(type(expected) is JournalHead and _integer(expected.sequence, maximum=_MAX_ENTRIES)
              and _digest(expected.digest) and _label(request_id), "invalid_argument")
        try:
            g.validate_command(command)
            raw_command = g.canonical(command)
            command = g.document(raw_command)
        except g.GovernorError as error:
            raise PersistenceError(error.code) from error
        with self._transaction(write=True) as db:
            meta, snapshot, requests = self._load(db)
            self._lease(meta, lease, self._stamp(meta))
            existing = requests.get(request_id)
            if existing is not None:
                _need(g.canonical(existing.value["command"]) == raw_command
                      and expected == JournalHead(existing.sequence - 1, existing.previous_digest), "request_conflict")
                return GovernorCommitResult(existing, True)
            _need(expected == snapshot.head, "head_conflict")
            _need(meta["sequence"] < _MAX_ENTRIES, "store_full")
            try:
                entry = g.append(snapshot.replayed, command, self._stamp(meta), request_id)
            except g.GovernorError as error:
                raise PersistenceError(error.code) from error
            db.execute("INSERT INTO entries VALUES (?,?,?,?,?)",
                       (entry.sequence, request_id, entry.payload, entry.digest, lease.fence))
            self._lease(meta, lease, self._stamp(meta))
            if command["kind"] in {"admit", "claim"} and entry.value["outcome"]["accepted"]:
                _need(meta["last"] < entry.value["outcome"]["not_after_ns"], "admission_expired")
            db.execute("UPDATE metadata SET head_sequence=?,head_digest=?,last_ns=? WHERE id=1",
                       (entry.sequence, entry.digest, meta["last"]))
            return GovernorCommitResult(entry, False)
