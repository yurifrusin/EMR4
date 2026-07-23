import http from "node:http";
import https from "node:https";
import { createHash, timingSafeEqual } from "node:crypto";
import { readFileSync } from "node:fs";

const LISTEN_HOST = "0.0.0.0";
const LISTEN_PORT = 8080;
const ALLOWED_PATH = "/infer";
const MAX_REQUEST_BYTES = 65_536;
const MAX_RESPONSE_BYTES = 262_144;
const MAX_OUTPUT_TOKENS = 2_048;
const UPSTREAM_TIMEOUT_MS = 170_000;

const laneId = process.env.ARIADNE_LANE_ID ?? "";
const expectedHashes = {
  shared_task_sha256: process.env.EXPECTED_SHARED_TASK_SHA256 ?? "",
  full_output_schema_sha256:
    process.env.EXPECTED_FULL_OUTPUT_SCHEMA_SHA256 ?? "",
  provider_output_schema_sha256:
    process.env.EXPECTED_PROVIDER_OUTPUT_SCHEMA_SHA256 ?? "",
  system_prompt_sha256: process.env.EXPECTED_SYSTEM_PROMPT_SHA256 ?? "",
  prompt_sha256: process.env.EXPECTED_PROMPT_SHA256 ?? "",
};
const brokerToken = readSecret("/run/secrets/broker_token");
const providerKey = readSecret("/run/secrets/provider_key");
let providerCallCount = 0;

const lanes = {
  terra: {
    provider: "openai",
    model: "gpt-5.6-terra",
    host: "api.openai.com",
    path: "/v1/responses",
  },
  gemini: {
    provider: "google",
    model: "gemini-3.5-flash",
    host: "generativelanguage.googleapis.com",
    path: "/v1beta/models/gemini-3.5-flash:generateContent",
  },
};
const lane = lanes[laneId];

function readSecret(path) {
  try {
    return readFileSync(path, "utf8").trim();
  } catch {
    return "";
  }
}

function hash(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function logEvent(event) {
  process.stdout.write(`${JSON.stringify(event)}\n`);
}

function equalSecret(left, right) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length > 0 && a.length === b.length && timingSafeEqual(a, b);
}

function suppliedToken(request) {
  const value = request.headers.authorization;
  return typeof value === "string" && value.toLowerCase().startsWith("bearer ")
    ? value.slice(7)
    : "";
}

function respond(response, status, value) {
  const body = Buffer.from(JSON.stringify(value));
  response.writeHead(status, {
    "content-type": "application/json",
    "content-length": String(body.length),
    "cache-control": "no-store",
  });
  response.end(body);
}

function readBoundedBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let length = 0;
    request.on("data", (chunk) => {
      length += chunk.length;
      if (length > MAX_REQUEST_BYTES) {
        request.destroy();
        reject(new Error("request-byte-budget-exceeded"));
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", () => reject(new Error("request-read-failed")));
  });
}

function hashesMatch(actual) {
  return (
    actual !== null &&
    typeof actual === "object" &&
    Object.entries(expectedHashes).every(
      ([key, expected]) =>
        expected.startsWith("sha256:") && actual[key] === expected,
    )
  );
}

function openAIRequest(payload) {
  return {
    model: lane.model,
    instructions: payload.system_prompt,
    input: payload.prompt,
    max_output_tokens: MAX_OUTPUT_TOKENS,
    reasoning: { effort: "medium" },
    store: false,
    tools: [],
    truncation: "disabled",
    text: {
      format: {
        type: "json_schema",
        name: "ariadne_common_provider_draft_envelope",
        strict: true,
        schema: payload.provider_output_schema,
      },
    },
  };
}

function geminiRequest(payload) {
  return {
    systemInstruction: { parts: [{ text: payload.system_prompt }] },
    contents: [{ role: "user", parts: [{ text: payload.prompt }] }],
    generationConfig: {
      candidateCount: 1,
      maxOutputTokens: MAX_OUTPUT_TOKENS,
      responseMimeType: "application/json",
      responseJsonSchema: payload.provider_output_schema,
      thinkingConfig: { thinkingLevel: "MEDIUM", includeThoughts: false },
    },
    store: false,
  };
}

function upstreamHeaders(bodyLength) {
  const common = {
    "content-type": "application/json",
    "content-length": String(bodyLength),
    "accept-encoding": "identity",
    "user-agent": "emr4-ariadne-comparative-one-use-broker/1",
  };
  return laneId === "terra"
    ? { ...common, authorization: `Bearer ${providerKey}` }
    : { ...common, "x-goog-api-key": providerKey };
}

function callProvider(body) {
  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        hostname: lane.host,
        port: 443,
        method: "POST",
        path: lane.path,
        headers: upstreamHeaders(body.length),
        timeout: UPSTREAM_TIMEOUT_MS,
        agent: false,
      },
      (providerResponse) => {
        const chunks = [];
        let length = 0;
        providerResponse.on("data", (chunk) => {
          length += chunk.length;
          if (length > MAX_RESPONSE_BYTES) {
            providerResponse.destroy();
            reject(new Error("provider-response-byte-budget-exceeded"));
            return;
          }
          chunks.push(chunk);
        });
        providerResponse.on("end", () =>
          resolve({
            statusCode: providerResponse.statusCode ?? 502,
            body: Buffer.concat(chunks),
          }),
        );
        providerResponse.on("error", () =>
          reject(new Error("provider-response-failed")),
        );
      },
    );
    request.on("timeout", () =>
      request.destroy(new Error("provider-request-timeout")),
    );
    request.on("error", () => reject(new Error("provider-request-failed")));
    request.end(body);
  });
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

function extractOpenAI(response) {
  const texts = [];
  for (const item of response?.output ?? []) {
    if (item?.type !== "message") continue;
    for (const part of item?.content ?? []) {
      if (part?.type === "output_text" && typeof part.text === "string") {
        texts.push(part.text);
      }
    }
  }
  if (texts.length !== 1) throw new Error("provider-output-text-count-invalid");
  return { generated: JSON.parse(texts[0]), usage: numericOnly(response.usage) ?? {} };
}

function extractGemini(response) {
  if (!Array.isArray(response?.candidates) || response.candidates.length !== 1) {
    throw new Error("provider-candidate-count-invalid");
  }
  const texts = (response.candidates[0]?.content?.parts ?? [])
    .filter((part) => part?.thought !== true && typeof part?.text === "string")
    .map((part) => part.text);
  if (texts.length !== 1) throw new Error("provider-output-text-count-invalid");
  return {
    generated: JSON.parse(texts[0]),
    usage: numericOnly(response.usageMetadata) ?? {},
  };
}

if (
  lane === undefined ||
  brokerToken.length < 32 ||
  providerKey.length < 16 ||
  Object.values(expectedHashes).some((value) => !value.startsWith("sha256:"))
) {
  logEvent({ event: "broker-start-rejected", reason_code: "sealed-policy-invalid" });
  process.exit(2);
}

const server = http.createServer(async (request, response) => {
  if (request.method !== "POST" || request.url !== ALLOWED_PATH) {
    logEvent({ event: "broker-request-rejected", reason_code: "path-invalid" });
    respond(response, 404, { status: "failed", reason_code: "path-invalid" });
    return;
  }
  if (!equalSecret(suppliedToken(request), brokerToken)) {
    logEvent({ event: "broker-request-rejected", reason_code: "auth-invalid" });
    respond(response, 401, { status: "failed", reason_code: "auth-invalid" });
    return;
  }
  if (providerCallCount >= 1) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "provider-call-budget-exhausted",
      provider_call_count: providerCallCount,
    });
    respond(response, 429, {
      status: "failed",
      reason_code: "provider-call-budget-exhausted",
    });
    return;
  }

  let payload;
  try {
    payload = JSON.parse((await readBoundedBody(request)).toString("utf8"));
  } catch {
    respond(response, 400, {
      status: "failed",
      reason_code: "request-invalid",
    });
    return;
  }
  if (
    typeof payload?.system_prompt !== "string" ||
    typeof payload?.prompt !== "string" ||
    payload?.provider_output_schema === null ||
    typeof payload?.provider_output_schema !== "object" ||
    !hashesMatch(payload?.hashes) ||
    hash(Buffer.from(payload.system_prompt)) !==
      expectedHashes.system_prompt_sha256 ||
    hash(Buffer.from(payload.prompt)) !== expectedHashes.prompt_sha256 ||
    hash(Buffer.from(JSON.stringify(payload.provider_output_schema))) !==
      expectedHashes.provider_output_schema_sha256
  ) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "sealed-request-mismatch",
    });
    respond(response, 400, {
      status: "failed",
      reason_code: "sealed-request-mismatch",
    });
    return;
  }

  const outbound = laneId === "terra" ? openAIRequest(payload) : geminiRequest(payload);
  const outboundBody = Buffer.from(JSON.stringify(outbound));
  if (outboundBody.length > MAX_REQUEST_BYTES) {
    respond(response, 413, {
      status: "failed",
      reason_code: "provider-request-byte-budget-exceeded",
    });
    return;
  }

  providerCallCount += 1;
  logEvent({
    event: "provider-call-started",
    lane_id: laneId,
    provider: lane.provider,
    model_id: lane.model,
    provider_call_count: providerCallCount,
    request_bytes: outboundBody.length,
    request_sha256: hash(outboundBody),
    maximum_output_tokens: MAX_OUTPUT_TOKENS,
  });

  try {
    const upstream = await callProvider(outboundBody);
    logEvent({
      event: "provider-call-completed",
      lane_id: laneId,
      provider_call_count: providerCallCount,
      provider_status: upstream.statusCode,
      response_bytes: upstream.body.length,
      response_sha256: hash(upstream.body),
    });
    if (upstream.statusCode < 200 || upstream.statusCode >= 300) {
      respond(response, 502, {
        status: "failed",
        reason_code: "provider-non-success",
        provider_status: upstream.statusCode,
      });
      return;
    }
    let providerResponse;
    let extracted;
    try {
      providerResponse = JSON.parse(upstream.body.toString("utf8"));
      extracted =
        laneId === "terra"
          ? extractOpenAI(providerResponse)
          : extractGemini(providerResponse);
    } catch {
      respond(response, 502, {
        status: "failed",
        reason_code: "provider-output-invalid",
      });
      return;
    }
    if (!Array.isArray(extracted.generated?.drafts)) {
      respond(response, 502, {
        status: "failed",
        reason_code: "provider-drafts-missing",
      });
      return;
    }
    respond(response, 200, {
      status: "completed",
      drafts: extracted.generated.drafts,
      usage: extracted.usage,
    });
  } catch {
    logEvent({
      event: "provider-call-failed",
      lane_id: laneId,
      provider_call_count: providerCallCount,
      reason_code: "provider-transport-failed",
    });
    respond(response, 502, {
      status: "failed",
      reason_code: "provider-transport-failed",
    });
  }
});

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  logEvent({
    event: "broker-ready",
    lane_id: laneId,
    allowed_path: ALLOWED_PATH,
    upstream_host: lane.host,
    upstream_path: lane.path,
    model_id: lane.model,
    maximum_provider_calls: 1,
  });
});

process.on("SIGTERM", () => server.close(() => process.exit(0)));
