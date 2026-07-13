import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import pty from "node-pty";

const ADAPTER_VERSION = "ariadne.deepcode_pty_receipt.v1";
const MAX_TRANSCRIPT_EVENTS = 256;
const MAX_TRANSCRIPT_BYTES = 64 * 1024;
function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`unexpected argument: ${key}`);
    if (key === "--fixture") {
      options.fixture = argv[++index];
      continue;
    }
    options[key.slice(2)] = argv[++index];
  }
  for (const required of ["cwd", "packet", "artifact", "outbox", "receipt"]) {
    if (!options[required]) throw new Error(`--${required} is required`);
  }
  options.timeout = Number(options.timeout || "180");
  if (!Number.isFinite(options.timeout) || options.timeout < 0 || options.timeout > 3600) {
    throw new Error("--timeout must be 0 (disabled) or between 1 and 3600 seconds");
  }
  options["exit-timeout"] = Number(options["exit-timeout"] || "30");
  if (!Number.isFinite(options["exit-timeout"]) || options["exit-timeout"] < 1 || options["exit-timeout"] > 60) {
    throw new Error("--exit-timeout must be between 1 and 60 seconds");
  }
  options["artifact-kind"] = options["artifact-kind"] || "decision";
  if (!["decision", "completion"].includes(options["artifact-kind"])) {
    throw new Error("--artifact-kind must be decision or completion");
  }
  return options;
}

function resolveWithin(root, candidate, label) {
  const resolvedRoot = path.resolve(root);
  const resolved = path.resolve(resolvedRoot, candidate);
  const relative = path.relative(resolvedRoot, resolved);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`${label} must resolve inside --cwd`);
  }
  return resolved;
}

function listEvents(outbox) {
  if (!fs.existsSync(outbox)) return new Set();
  return new Set(fs.readdirSync(outbox).filter((name) => name.endsWith(".json")));
}

function stripAnsi(value) {
  return value
    .replace(/\x1B\[[0-?]*[ -/]*[@-~]/g, "")
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "");
}

function redactTerminalData(value) {
  let redactions = 0;
  const replace = (pattern, replacement) => {
    value = value.replace(pattern, (...args) => {
      redactions += 1;
      return `${args[1]}${replacement}`;
    });
  };
  replace(/((?:authorization|proxy-authorization)\s*[:=]\s*(?:bearer\s+)?)[^\s,;]+/gi, "[REDACTED]");
  replace(/((?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|secret|token)\s*[:=]\s*["']?)[^\s,"']+/gi, "[REDACTED]");
  replace(/((?:sk|rk|ghp|gho|github_pat|xox[baprs])-)[A-Za-z0-9._-]+/g, "[REDACTED]");
  replace(/(AIza)[A-Za-z0-9_-]{20,}/g, "[REDACTED]");
  value = value.replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g, () => {
    redactions += 1;
    return "[REDACTED]";
  });
  return { value, redactions };
}

function transcriptPathFor(receipt, outbox, requested) {
  return requested || path.join(outbox, `${path.basename(receipt)}.terminal.jsonl`);
}

function acquireArtifactOwnerLock(artifact) {
  const lockPath = `${artifact}.ariadne-owner.lock`;
  fs.mkdirSync(path.dirname(lockPath), { recursive: true });
  let handle;
  try {
    handle = fs.openSync(lockPath, "wx");
  } catch (error) {
    if (error?.code === "EEXIST") {
      throw new Error(`artifact owner lock already exists: ${path.basename(lockPath)}`);
    }
    throw error;
  }
  fs.writeFileSync(handle, JSON.stringify({ pid: process.pid, artifact, acquired_at: new Date().toISOString() }) + "\n");
  fs.closeSync(handle);
  let released = false;
  const release = () => {
    if (released) return;
    released = true;
    try {
      fs.unlinkSync(lockPath);
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
    }
  };
  process.once("exit", release);
  return { release };
}

function createTranscriptWriter(transcriptPath, cwd) {
  fs.mkdirSync(path.dirname(transcriptPath), { recursive: true });
  fs.writeFileSync(transcriptPath, "", "utf8");
  let bytes = 0;
  let events = 0;
  let redactions = 0;
  let eventLimitReached = false;
  let byteLimitReached = false;

  function serialize(text, sequence) {
    return JSON.stringify({
      schema_version: "ariadne.deepcode_terminal_event.v1",
      sequence,
      recorded_at: new Date().toISOString(),
      kind: "pty_data",
      text,
    }) + "\n";
  }

  function fitToBytes(text, sequence, available) {
    if (Buffer.byteLength(serialize(text, sequence), "utf8") <= available) return text;
    const characters = Array.from(text);
    let low = 0;
    let high = characters.length;
    let best = "";
    while (low <= high) {
      const middle = Math.floor((low + high) / 2);
      const candidate = characters.slice(0, middle).join("");
      if (Buffer.byteLength(serialize(candidate, sequence), "utf8") <= available) {
        best = candidate;
        low = middle + 1;
      } else {
        high = middle - 1;
      }
    }
    return best;
  }

  return {
    record(data) {
      const sanitized = redactTerminalData(stripAnsi(data));
      redactions += sanitized.redactions;
      if (!sanitized.value) return sanitized;
      if (events >= MAX_TRANSCRIPT_EVENTS) {
        eventLimitReached = true;
        return sanitized;
      }
      const sequence = events + 1;
      const available = MAX_TRANSCRIPT_BYTES - bytes;
      const text = fitToBytes(sanitized.value, sequence, available);
      const serialized = serialize(text, sequence);
      if (!text && Buffer.byteLength(serialized, "utf8") > available) {
        byteLimitReached = true;
        return sanitized;
      }
      if (text.length !== sanitized.value.length) byteLimitReached = true;
      fs.appendFileSync(transcriptPath, serialized, "utf8");
      bytes += Buffer.byteLength(serialized, "utf8");
      events += 1;
      return sanitized;
    },
    metadata() {
      return {
        path: path.relative(cwd, transcriptPath).replaceAll("\\", "/"),
        event_count: events,
        byte_count: bytes,
        max_event_count: MAX_TRANSCRIPT_EVENTS,
        max_bytes: MAX_TRANSCRIPT_BYTES,
        event_count_truncated: eventLimitReached,
        byte_truncated: byteLimitReached,
        redacted: redactions > 0,
        redacted_value_count: redactions,
      };
    },
  };
}

function normalizeMarkerText(value) {
  value = value.trim();
  for (let pass = 0; pass < 4; pass += 1) {
    const heading = value.match(/^#{1,6}\s+(.+)$/);
    if (heading) {
      value = heading[1].trim();
      continue;
    }
    let changed = false;
    for (const wrapper of ["**", "__", "`", "*", "_"]) {
      if (value.startsWith(wrapper) && value.endsWith(wrapper) && value.length > wrapper.length * 2) {
        value = value.slice(wrapper.length, -wrapper.length).trim();
        changed = true;
        break;
      }
    }
    if (!changed) break;
  }
  return value;
}

function parseArtifactMarker(body, artifactKind) {
  const supported = artifactKind === "completion"
    ? new Set(["STATUS: COMPLETE"])
    : new Set(["DECISION: PASS", "DECISION: REVISION_REQUIRED"]);
  const prefix = artifactKind === "completion" ? "STATUS:" : "DECISION:";
  const lines = [];
  for (const line of body.split(/\r?\n/)) {
    const cells = line.includes("|") ? line.split("|") : [line];
    for (const cell of cells) {
      const normalized = normalizeMarkerText(cell);
      if (normalized) lines.push(normalized);
    }
  }
  const tailStart = Math.max(0, lines.length - 8);
  const found = lines
    .map((line, index) => ({ line: line.toUpperCase(), index }))
    .filter(({ line }) => supported.has(line));
  const terminalLines = lines.slice(tailStart).map((line) => line.toUpperCase()).filter((line) => line.startsWith(prefix));
  if (found.length !== 1) return { valid: false };
  if (found[0].index < tailStart) return { valid: false };
  if (terminalLines.some((line) => !supported.has(line)) || terminalLines.length !== 1) return { valid: false };
  return { valid: true };
}

function validArtifact(artifact, artifactKind) {
  if (!fs.existsSync(artifact)) return false;
  const body = fs.readFileSync(artifact, "utf8");
  return parseArtifactMarker(body, artifactKind).valid;
}

function writeReceipt(receiptPath, payload) {
  fs.mkdirSync(path.dirname(receiptPath), { recursive: true });
  fs.writeFileSync(receiptPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

function writeAdapterEvent(outbox, artifact, cwd) {
  fs.mkdirSync(outbox, { recursive: true });
  const eventId = crypto.randomUUID();
  const recordedAt = new Date().toISOString();
  const filename = `${recordedAt.replaceAll(":", "").replace("Z", "_0000")}_${eventId}.json`;
  fs.writeFileSync(
    path.join(outbox, filename),
    `${JSON.stringify({
      schema_version: "ariadne.deepcode_pty_event.v1",
      event_id: eventId,
      recorded_at: recordedAt,
      source: "deepcode_pty_adapter",
      status: "completed",
      artifact: path.relative(cwd, artifact).replaceAll("\\", "/"),
      trust: "untrusted_transport_completion_requires_artifact_validation",
    }, null, 2)}\n`,
    "utf8",
  );
  return filename;
}

function quoteCmd(value) {
  return `"${value.replaceAll('"', '""')}"`;
}

function liveCommand(packetRelative, artifactRelative, artifactKind, sharedPython, sharedNode) {
  const packetPath = packetRelative.replaceAll("\\", "/");
  const artifactPath = artifactRelative.replaceAll("\\", "/");
  const prompt = [
    `Read and follow ${packetPath} exactly.`,
    `Write the final durable artifact to exactly ${artifactPath}.`,
    "Do not choose, infer, or substitute another artifact filename.",
    artifactKind === "completion"
      ? "Include a canonical STATUS: complete line only after the packet work and evidence are complete."
      : "Include a canonical DECISION: pass or DECISION: revision_required line.",
    sharedPython
      ? `Use this shared Python for tests: ${sharedPython}. Do not claim Python or pytest is unavailable before trying it.`
      : "No shared Python interpreter was discovered; report that exact preflight limitation if Python tests are required.",
    sharedNode
      ? `Use this shared Node executable for JavaScript checks: ${sharedNode}.`
      : "No shared Node executable was discovered; report that exact preflight limitation if Node checks are required.",
  ].join(" ");
  if (process.platform === "win32") {
    return {
      executable: process.env.ComSpec || "cmd.exe",
      args: `/d /s /c deepcode -p ${quoteCmd(prompt)}`,
    };
  }
  return { executable: "deepcode", args: ["-p", prompt] };
}

function fixtureCommand(mode, artifact, outbox) {
  if (!process.env.ARIADNE_PTY_TEST_MODE) {
    throw new Error("--fixture requires ARIADNE_PTY_TEST_MODE");
  }
  if (!["success", "permission", "hang", "ignore_exit", "markdown_decision", "completion", "markdown_completion", "bold_completion", "artifact_only", "diagnostic_burst"].includes(mode)) {
    throw new Error("unsupported fixture mode");
  }
  const fixture = path.join(path.dirname(fileURLToPath(import.meta.url)), "fake_deepcode.mjs");
  return { executable: process.execPath, args: [fixture, mode, artifact, outbox] };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const cwd = path.resolve(options.cwd);
  const packet = resolveWithin(cwd, options.packet, "packet");
  const artifact = resolveWithin(cwd, options.artifact, "artifact");
  const outbox = resolveWithin(cwd, options.outbox, "outbox");
  const receipt = resolveWithin(cwd, options.receipt, "receipt");
  const transcript = resolveWithin(cwd, transcriptPathFor(receipt, outbox, options.transcript), "transcript");
  if (!fs.existsSync(packet)) throw new Error("packet does not exist");
  if (fs.existsSync(artifact)) throw new Error("artifact must not exist before PTY launch");
  if (transcript === receipt || transcript === artifact) throw new Error("transcript must be distinct from receipt and artifact");

  const artifactOwner = acquireArtifactOwnerLock(artifact);
  const transcriptWriter = createTranscriptWriter(transcript, cwd);

  const baselineEvents = listEvents(outbox);
  const command = options.fixture
    ? fixtureCommand(options.fixture, artifact, outbox)
    : liveCommand(
        path.relative(cwd, packet),
        path.relative(cwd, artifact),
        options["artifact-kind"],
        options["shared-python"] || null,
        options["shared-node"] || null,
      );
  const startedAt = new Date();
  let terminalWindow = "";
  let artifactObserved = false;
  let exitSent = false;
  let permissionPrompt = false;
  let childExitCode = null;
  let artifactDeadlineReached = false;
  let turnCompletionObserved = false;
  let completionSignal = null;
  let exitSignalStage = 0;
  let nextExitSignalAt = null;

  const child = pty.spawn(command.executable, command.args, {
    cwd,
    cols: 120,
    rows: 40,
    env: {
      ...process.env,
      TERM: process.env.TERM || "xterm-256color",
      DEEPCODE_NOTIFY: path.join(
        cwd,
        "scripts",
        process.platform === "win32" ? "ariadne_deepcode_notify.cmd" : "ariadne_deepcode_notify.sh",
      ),
      ARIADNE_SHARED_PYTHON: options["shared-python"] || "",
      ARIADNE_SHARED_NODE: options["shared-node"] || "",
    },
    name: "xterm-256color",
    useConptyDll: process.platform === "win32",
  });

  child.onData((data) => {
    const sanitized = transcriptWriter.record(data);
    terminalWindow = `${terminalWindow}${sanitized.value}`.slice(-4000);
    if (/permission required/i.test(terminalWindow) && /do you want to proceed\?/i.test(terminalWindow)) {
      permissionPrompt = true;
      child.write("\x03");
    }
    if (/status:\s*(completed|failed)\s*·\s*tokens:/i.test(terminalWindow)) {
      turnCompletionObserved = true;
    }
  });
  child.onExit(({ exitCode }) => {
    childExitCode = exitCode;
  });

  const artifactDeadline = options.timeout === 0
    ? Number.POSITIVE_INFINITY
    : Date.now() + options.timeout * 1000;
  let exitDeadline = null;
  while (true) {
    if (permissionPrompt) break;
    if (!artifactObserved && validArtifact(artifact, options["artifact-kind"])) {
      artifactObserved = true;
      turnCompletionObserved = true;
      completionSignal = "artifact_marker";
    }
    if (artifactObserved && turnCompletionObserved && !exitSent) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      child.write("/exit\r");
      exitSent = true;
      exitSignalStage = 1;
      nextExitSignalAt = Date.now() + 5000;
      exitDeadline = Date.now() + options["exit-timeout"] * 1000;
    }
    if (exitSent && childExitCode === null && Date.now() >= nextExitSignalAt) {
      if (exitSignalStage === 1) {
        child.write("/exit\r");
        nextExitSignalAt = Date.now() + 5000;
      } else if (exitSignalStage === 2) {
        child.write("\x04");
        nextExitSignalAt = Date.now() + 1000;
      } else if (exitSignalStage === 3) {
        child.write("\x04");
        nextExitSignalAt = Number.POSITIVE_INFINITY;
      }
      exitSignalStage += 1;
    }
    if (childExitCode !== null) break;
    if (!artifactObserved && Date.now() >= artifactDeadline) break;
    if (exitDeadline !== null && Date.now() >= exitDeadline) break;
    await new Promise((resolve) => setTimeout(resolve, 200));
  }

  artifactDeadlineReached = !permissionPrompt && !artifactObserved && childExitCode === null;
  const exitDeadlineReached = artifactObserved && exitSent && childExitCode === null;
  const forcedCleanup = exitDeadlineReached;

  if (childExitCode === null) {
    child.kill();
    const cleanupDeadline = Date.now() + 5000;
    while (childExitCode === null && Date.now() < cleanupDeadline) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  const processCleanupConfirmed = childExitCode !== null;

  if (artifactObserved && exitSent && turnCompletionObserved && processCleanupConfirmed && !permissionPrompt) {
    writeAdapterEvent(outbox, artifact, cwd);
  }
  const newEvents = [...listEvents(outbox)].filter((name) => !baselineEvents.has(name));

  let status = "completed";
  let reason = "artifact_and_mailbox_observed";
  if (permissionPrompt) {
    status = "blocked";
    reason = "unexpected_permission_prompt";
  } else if (!artifactObserved) {
    status = "failed";
    reason = artifactDeadlineReached ? "artifact_timeout" : "process_exited_without_artifact";
  } else if (!processCleanupConfirmed) {
    status = "failed";
    reason = "process_cleanup_unconfirmed";
  } else if (newEvents.length === 0) {
    status = "failed";
    reason = "mailbox_event_missing";
  } else if (forcedCleanup) {
    reason = "artifact_and_adapter_event_observed_forced_cleanup";
  }

  writeReceipt(receipt, {
    schema_version: ADAPTER_VERSION,
    status,
    reason,
    started_at: startedAt.toISOString(),
    finished_at: new Date().toISOString(),
    platform: os.platform(),
    packet: path.relative(cwd, packet).replaceAll("\\", "/"),
    artifact: path.relative(cwd, artifact).replaceAll("\\", "/"),
    artifact_kind: options["artifact-kind"],
    artifact_deadline_active: options.timeout > 0,
    configured_model: options.model || null,
    configured_reasoning: options.reasoning || null,
    artifact_observed: artifactObserved,
    turn_completion_observed: turnCompletionObserved,
    completion_signal: completionSignal,
    exit_sent_after_artifact: exitSent,
    exit_signal_count: exitSignalStage,
    forced_cleanup: forcedCleanup,
    process_cleanup_confirmed: processCleanupConfirmed,
    permission_prompt_observed: permissionPrompt,
    mailbox_event_count: newEvents.length,
    mailbox_events: newEvents.sort(),
    child_exit_code: childExitCode,
    terminal_output_persisted: true,
    terminal_transcript: transcriptWriter.metadata(),
  });
  artifactOwner.release();
  process.stdout.write(`${JSON.stringify({ status, reason, receipt }, null, 2)}\n`);
  return status === "completed" ? 0 : status === "blocked" ? 3 : 4;
}

main().then((code) => process.exit(code)).catch((error) => {
  process.stderr.write(`ariadne Deep Code PTY adapter failed: ${error.message}\n`);
  process.exit(2);
});
