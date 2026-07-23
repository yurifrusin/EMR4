import http from "node:http";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

const MANIFEST_PATH = "/opt/ariadne/comparison-manifest.json";
const TASK_PATH = "/opt/ariadne/shared-task.json";
const FULL_SCHEMA_PATH = "/opt/ariadne/full-output.schema.json";
const PROVIDER_SCHEMA_PATH = "/opt/ariadne/provider-output.schema.json";
const TOKEN_PATH = "/run/secrets/broker_token";
const MAX_BROKER_RESPONSE_BYTES = 32_768;

function hash(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function fail(reasonCode, extra = {}) {
  process.stdout.write(
    `${JSON.stringify({ status: "failed", reason_code: reasonCode, ...extra })}\n`,
  );
  process.exitCode = 2;
}

function numericOnly(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return undefined;
  }
  const result = {};
  for (const [key, item] of Object.entries(value)) {
    const clean = numericOnly(item);
    if (clean !== undefined) result[key] = clean;
  }
  return result;
}

function callBroker(body, token, deadlineSeconds) {
  return new Promise((resolve, reject) => {
    const encoded = Buffer.from(JSON.stringify(body));
    const request = http.request(
      {
        hostname: "broker",
        port: 8080,
        method: "POST",
        path: "/infer",
        headers: {
          authorization: `Bearer ${token}`,
          "content-type": "application/json",
          "content-length": String(encoded.length),
          "accept-encoding": "identity",
        },
        timeout: deadlineSeconds * 1_000,
      },
      (response) => {
        const chunks = [];
        let length = 0;
        response.on("data", (chunk) => {
          length += chunk.length;
          if (length > MAX_BROKER_RESPONSE_BYTES) {
            response.destroy();
            reject(new Error("broker-response-byte-budget-exceeded"));
            return;
          }
          chunks.push(chunk);
        });
        response.on("end", () =>
          resolve({
            statusCode: response.statusCode ?? 502,
            body: Buffer.concat(chunks),
          }),
        );
        response.on("error", () => reject(new Error("broker-response-failed")));
      },
    );
    request.on("timeout", () => request.destroy(new Error("broker-timeout")));
    request.on("error", () => reject(new Error("broker-request-failed")));
    request.end(encoded);
  });
}

async function main() {
  let manifestBytes;
  let taskBytes;
  let fullSchemaBytes;
  let providerSchemaBytes;
  let token;
  let manifest;
  let task;
  let fullSchema;
  let providerSchema;
  try {
    [manifestBytes, taskBytes, fullSchemaBytes, providerSchemaBytes, token] =
      await Promise.all([
        readFile(MANIFEST_PATH),
        readFile(TASK_PATH),
        readFile(FULL_SCHEMA_PATH),
        readFile(PROVIDER_SCHEMA_PATH),
        readFile(TOKEN_PATH, "utf8"),
      ]);
    manifest = JSON.parse(manifestBytes.toString("utf8"));
    task = JSON.parse(taskBytes.toString("utf8"));
    fullSchema = JSON.parse(fullSchemaBytes.toString("utf8"));
    providerSchema = JSON.parse(providerSchemaBytes.toString("utf8"));
  } catch {
    fail("sealed-input-read-or-parse-failed");
    return;
  }

  if (
    manifest?.protocol_id !== "ariadne-terra-gemini-comparative-rehearsal" ||
    task?.model_contract !== undefined ||
    task?.attempt_id !== "generated-attempt-001" ||
    task?.context_frames?.length !== 6 ||
    manifest?.budgets?.maximum_provider_calls_per_lane !== 1 ||
    manifest?.budgets?.maximum_attempts_per_lane !== 1 ||
    token.trim().length < 32
  ) {
    fail("sealed-policy-invalid");
    return;
  }

  const systemPrompt = manifest.system_prompt;
  const prompt = [
    ...manifest.task_prompt_prefix,
    `TASK=${JSON.stringify(task)}`,
    `FULL_OUTPUT_SCHEMA=${JSON.stringify(fullSchema)}`,
  ].join("\n");
  const promptBytes = Buffer.byteLength(prompt, "utf8");
  if (promptBytes > manifest.budgets.maximum_prompt_bytes) {
    fail("compiled-prompt-byte-budget-exceeded", { prompt_bytes: promptBytes });
    return;
  }

  const requestEnvelope = {
    system_prompt: systemPrompt,
    prompt,
    provider_output_schema: providerSchema,
    hashes: {
      shared_task_sha256: hash(taskBytes),
      full_output_schema_sha256: hash(fullSchemaBytes),
      provider_output_schema_sha256: hash(
        Buffer.from(JSON.stringify(providerSchema)),
      ),
      system_prompt_sha256: hash(Buffer.from(systemPrompt)),
      prompt_sha256: hash(Buffer.from(prompt)),
    },
  };

  let brokerResponse;
  try {
    brokerResponse = await callBroker(
      requestEnvelope,
      token.trim(),
      manifest.budgets.deadline_seconds,
    );
  } catch {
    fail("broker-transport-failed");
    return;
  }

  let normalised;
  try {
    normalised = JSON.parse(brokerResponse.body.toString("utf8"));
  } catch {
    fail("broker-response-json-invalid", {
      broker_status: brokerResponse.statusCode,
    });
    return;
  }
  if (brokerResponse.statusCode !== 200 || normalised?.status !== "completed") {
    fail(
      typeof normalised?.reason_code === "string"
        ? normalised.reason_code
        : "broker-rejected-or-provider-failed",
      { broker_status: brokerResponse.statusCode },
    );
    return;
  }

  const generated = { drafts: normalised.drafts };
  const generatedCanonical = JSON.stringify(generated);
  const generatedBytes = Buffer.byteLength(generatedCanonical, "utf8");
  if (
    generatedBytes > manifest.budgets.maximum_output_bytes ||
    !Array.isArray(generated.drafts) ||
    generated.drafts.length > manifest.budgets.maximum_output_drafts
  ) {
    fail("generated-output-budget-invalid");
    return;
  }

  process.stdout.write(
    `${JSON.stringify({
      status: "completed",
      schema_version: "ariadne.comparative_work_cell_result.v1",
      shared_task_sha256: requestEnvelope.hashes.shared_task_sha256,
      full_output_schema_sha256:
        requestEnvelope.hashes.full_output_schema_sha256,
      provider_output_schema_sha256:
        requestEnvelope.hashes.provider_output_schema_sha256,
      system_prompt_sha256: requestEnvelope.hashes.system_prompt_sha256,
      prompt_sha256: requestEnvelope.hashes.prompt_sha256,
      prompt_bytes: promptBytes,
      generated_output_sha256: hash(Buffer.from(generatedCanonical)),
      generated_output_bytes: generatedBytes,
      generated_draft_count: generated.drafts.length,
      usage: numericOnly(normalised.usage) ?? {},
      drafts: generated.drafts,
    })}\n`,
  );
}

await main();
