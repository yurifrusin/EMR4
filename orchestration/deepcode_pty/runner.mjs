import fs from "node:fs";
import crypto from "node:crypto";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import pty from "node-pty";

const ADAPTER_VERSION = "ariadne.deepcode_pty_receipt.v1";
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

function validArtifact(artifact, artifactKind) {
  if (!fs.existsSync(artifact)) return false;
  const body = fs.readFileSync(artifact, "utf8");
  return body.split(/\r?\n/).some((line) => {
    const cells = line.includes("|") ? line.split("|") : [line];
    return cells.some((cell) => {
      const normalized = cell.trim().replace(/^[*`_]+|[*`_]+$/g, "").trim();
      if (artifactKind === "completion") return /^STATUS:\s*complete$/i.test(normalized);
      return /^DECISION:\s*(pass|revision_required)$/i.test(normalized);
    });
  });
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

function liveCommand(packetRelative, artifactRelative, artifactKind) {
  const packetPath = packetRelative.replaceAll("\\", "/");
  const artifactPath = artifactRelative.replaceAll("\\", "/");
  const prompt = [
    `Read and follow ${packetPath} exactly.`,
    `Write the final durable artifact to exactly ${artifactPath}.`,
    "Do not choose, infer, or substitute another artifact filename.",
    artifactKind === "completion"
      ? "Include a canonical STATUS: complete line only after the packet work and evidence are complete."
      : "Include a canonical DECISION: pass or DECISION: revision_required line.",
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
  if (!["success", "permission", "hang", "ignore_exit", "markdown_decision", "completion"].includes(mode)) {
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
  if (!fs.existsSync(packet)) throw new Error("packet does not exist");
  if (fs.existsSync(artifact)) throw new Error("artifact must not exist before PTY launch");

  const baselineEvents = listEvents(outbox);
  const command = options.fixture
    ? fixtureCommand(options.fixture, artifact, outbox)
    : liveCommand(path.relative(cwd, packet), path.relative(cwd, artifact), options["artifact-kind"]);
  const startedAt = new Date();
  let terminalWindow = "";
  let artifactObserved = false;
  let exitSent = false;
  let permissionPrompt = false;
  let childExitCode = null;
  let artifactDeadlineReached = false;
  let turnCompletionObserved = false;
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
    },
    name: "xterm-256color",
    useConptyDll: process.platform === "win32",
  });

  child.onData((data) => {
    terminalWindow = stripAnsi(`${terminalWindow}${data}`).slice(-4000);
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
  let turnCompletionDeadline = null;
  let exitDeadline = null;
  while (true) {
    if (permissionPrompt) break;
    if (!artifactObserved && validArtifact(artifact, options["artifact-kind"])) {
      artifactObserved = true;
      turnCompletionDeadline = Date.now() + 60000;
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
    if (artifactObserved && !turnCompletionObserved && Date.now() >= turnCompletionDeadline) break;
    if (exitDeadline !== null && Date.now() >= exitDeadline) break;
    await new Promise((resolve) => setTimeout(resolve, 200));
  }

  artifactDeadlineReached = !permissionPrompt && !artifactObserved && childExitCode === null;
  const exitDeadlineReached = artifactObserved && exitSent && childExitCode === null;
  const turnCompletionDeadlineReached = artifactObserved && !turnCompletionObserved;
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
  } else if (turnCompletionDeadlineReached) {
    status = "failed";
    reason = "turn_completion_timeout";
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
    artifact_observed: artifactObserved,
    turn_completion_observed: turnCompletionObserved,
    exit_sent_after_artifact: exitSent,
    exit_signal_count: exitSignalStage,
    forced_cleanup: forcedCleanup,
    process_cleanup_confirmed: processCleanupConfirmed,
    permission_prompt_observed: permissionPrompt,
    mailbox_event_count: newEvents.length,
    mailbox_events: newEvents.sort(),
    child_exit_code: childExitCode,
    terminal_output_persisted: false,
  });
  process.stdout.write(`${JSON.stringify({ status, reason, receipt }, null, 2)}\n`);
  return status === "completed" ? 0 : status === "blocked" ? 3 : 4;
}

main().then((code) => process.exit(code)).catch((error) => {
  process.stderr.write(`ariadne Deep Code PTY adapter failed: ${error.message}\n`);
  process.exit(2);
});
