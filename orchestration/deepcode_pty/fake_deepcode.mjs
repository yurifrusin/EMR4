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
} else if (mode === "success" || mode === "ignore_exit") {
  fs.mkdirSync(path.dirname(artifactPath), { recursive: true });
  fs.writeFileSync(artifactPath, "DECISION: pass\n\nSynthetic PTY fixture.\n", "utf8");
  process.stdout.write("Artifact written\r\nstatus: completed · tokens: 1\r\n");
} else {
  process.exit(64);
}

process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  if (!chunk.includes("/exit") || mode === "ignore_exit") return;
  process.exit(0);
});

setInterval(() => {}, 1000);
