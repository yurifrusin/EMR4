import fs from "node:fs";
import path from "node:path";

const [mode, artifactPath, outboxPath] = process.argv.slice(2);

if (!mode || !artifactPath || !outboxPath) {
  process.exit(64);
}

if (mode === "permission") {
  process.stdout.write("Permission required\r\nDo you want to proceed?\r\n");
} else if (mode === "hang") {
  process.stdout.write("Working\r\n");
} else if (mode === "success" || mode === "ignore_exit" || mode === "markdown_decision" || mode === "completion" || mode === "markdown_completion" || mode === "bold_completion" || mode === "artifact_only" || mode === "diagnostic_burst") {
  fs.mkdirSync(path.dirname(artifactPath), { recursive: true });
  const decision = mode === "completion"
    ? "STATUS: complete"
    : mode === "markdown_completion" ? "## STATUS: complete"
      : mode === "bold_completion" ? "**STATUS: complete**"
        : mode === "markdown_decision" ? "| Decision | **`DECISION: pass`** |" : "DECISION: pass";
  fs.writeFileSync(artifactPath, `${decision}\n\nSynthetic PTY fixture.\n`, "utf8");
  process.stdout.write(mode === "artifact_only"
    ? "Artifact written\r\n"
    : "Artifact written\r\nstatus: completed · tokens: 1\r\n");
  if (mode === "diagnostic_burst") {
    for (let index = 0; index < 4096; index += 1) {
      process.stdout.write(`diag ${index} Authorization: Bearer super-secret-token-${index} api_key=sk-secret-${index}\r\n`);
    }
  }
} else {
  process.exit(64);
}

process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  if (!chunk.includes("/exit") || mode === "ignore_exit") return;
  process.exit(0);
});

setInterval(() => {}, 1000);
