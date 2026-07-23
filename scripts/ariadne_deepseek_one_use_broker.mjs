import http from "node:http";
import https from "node:https";
import { createHash, timingSafeEqual } from "node:crypto";

const LISTEN_HOST = "0.0.0.0";
const LISTEN_PORT = 8080;
const ALLOWED_PATH = "/anthropic/v1/messages";
const UPSTREAM_HOST = "api.deepseek.com";
const MODEL_ID = "deepseek-v4-flash";
const MAX_REQUEST_BYTES = 65_536;
const MAX_RESPONSE_BYTES = 262_144;
const MAX_OUTPUT_TOKENS = 2_048;
const UPSTREAM_TIMEOUT_MS = 170_000;

const brokerToken = process.env.BROKER_TOKEN ?? "";
const providerKey = process.env.DEEPSEEK_API_KEY ?? "";
let providerCallCount = 0;

function sha256(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function logEvent(event) {
  process.stdout.write(`${JSON.stringify(event)}\n`);
}

function equalSecret(left, right) {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  return (
    leftBuffer.length === rightBuffer.length &&
    leftBuffer.length > 0 &&
    timingSafeEqual(leftBuffer, rightBuffer)
  );
}

function suppliedToken(request) {
  const apiKey = request.headers["x-api-key"];
  if (typeof apiKey === "string") {
    return apiKey;
  }
  const authorization = request.headers.authorization;
  if (
    typeof authorization === "string" &&
    authorization.toLowerCase().startsWith("bearer ")
  ) {
    return authorization.slice(7);
  }
  return "";
}

function respondJson(response, status, reasonCode) {
  const body = Buffer.from(
    JSON.stringify({ error: { type: "broker_rejection", reason_code: reasonCode } }),
  );
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
        reject(new Error("request-byte-budget-exceeded"));
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", () => reject(new Error("request-read-failed")));
  });
}

function forwardToProvider(body, inboundHeaders) {
  return new Promise((resolve, reject) => {
    const headers = {
      "content-type": "application/json",
      "content-length": String(body.length),
      "x-api-key": providerKey,
      authorization: `Bearer ${providerKey}`,
      "anthropic-version":
        typeof inboundHeaders["anthropic-version"] === "string"
          ? inboundHeaders["anthropic-version"]
          : "2023-06-01",
      "accept-encoding": "identity",
      "user-agent": "emr4-ariadne-one-use-broker/1",
    };
    const upstreamRequest = https.request(
      {
        hostname: UPSTREAM_HOST,
        port: 443,
        method: "POST",
        path: ALLOWED_PATH,
        headers,
        timeout: UPSTREAM_TIMEOUT_MS,
        agent: false,
      },
      (upstreamResponse) => {
        const chunks = [];
        let length = 0;
        upstreamResponse.on("data", (chunk) => {
          length += chunk.length;
          if (length > MAX_RESPONSE_BYTES) {
            upstreamResponse.destroy();
            reject(new Error("response-byte-budget-exceeded"));
            return;
          }
          chunks.push(chunk);
        });
        upstreamResponse.on("end", () => {
          resolve({
            statusCode: upstreamResponse.statusCode ?? 502,
            headers: upstreamResponse.headers,
            body: Buffer.concat(chunks),
          });
        });
        upstreamResponse.on("error", () =>
          reject(new Error("provider-response-failed")),
        );
      },
    );
    upstreamRequest.on("timeout", () => {
      upstreamRequest.destroy(new Error("provider-timeout"));
    });
    upstreamRequest.on("error", (error) => reject(error));
    upstreamRequest.end(body);
  });
}

if (!brokerToken || !providerKey) {
  logEvent({ event: "broker-start-rejected", reason_code: "required-secret-missing" });
  process.exit(2);
}

const server = http.createServer(async (request, response) => {
  if (request.method !== "POST" || request.url !== ALLOWED_PATH) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "method-or-path-not-allowlisted",
    });
    respondJson(response, 404, "method-or-path-not-allowlisted");
    return;
  }
  if (!equalSecret(suppliedToken(request), brokerToken)) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "broker-authentication-failed",
    });
    respondJson(response, 401, "broker-authentication-failed");
    return;
  }
  if (providerCallCount >= 1) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "provider-call-budget-exhausted",
      provider_call_count: providerCallCount,
    });
    respondJson(response, 429, "provider-call-budget-exhausted");
    return;
  }

  let incomingBody;
  try {
    incomingBody = await readBoundedBody(request);
  } catch (error) {
    logEvent({
      event: "broker-request-rejected",
      reason_code:
        error instanceof Error ? error.message : "request-read-failed",
    });
    if (!response.headersSent) {
      respondJson(response, 413, "request-byte-budget-exceeded");
    }
    return;
  }

  let payload;
  try {
    payload = JSON.parse(incomingBody.toString("utf8"));
  } catch {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "request-json-invalid",
    });
    respondJson(response, 400, "request-json-invalid");
    return;
  }
  if (payload?.model !== MODEL_ID) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "model-not-allowlisted",
    });
    respondJson(response, 400, "model-not-allowlisted");
    return;
  }
  if (Array.isArray(payload?.tools) && payload.tools.length > 0) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "provider-tools-not-allowed",
    });
    respondJson(response, 400, "provider-tools-not-allowed");
    return;
  }

  const requestedMaxTokens = Number.isInteger(payload.max_tokens)
    ? payload.max_tokens
    : MAX_OUTPUT_TOKENS;
  payload.max_tokens = Math.min(
    Math.max(requestedMaxTokens, 1),
    MAX_OUTPUT_TOKENS,
  );
  const outboundBody = Buffer.from(JSON.stringify(payload));
  if (outboundBody.length > MAX_REQUEST_BYTES) {
    logEvent({
      event: "broker-request-rejected",
      reason_code: "canonical-request-byte-budget-exceeded",
    });
    respondJson(response, 413, "canonical-request-byte-budget-exceeded");
    return;
  }

  providerCallCount += 1;
  logEvent({
    event: "provider-call-started",
    provider_call_count: providerCallCount,
    model_id: MODEL_ID,
    request_bytes: outboundBody.length,
    request_sha256: sha256(outboundBody),
    maximum_output_tokens: payload.max_tokens,
    token_cap_applied: requestedMaxTokens !== payload.max_tokens,
  });

  try {
    const upstream = await forwardToProvider(outboundBody, request.headers);
    const responseHeaders = {
      "content-type":
        typeof upstream.headers["content-type"] === "string"
          ? upstream.headers["content-type"]
          : "application/json",
      "content-length": String(upstream.body.length),
      "cache-control": "no-store",
    };
    response.writeHead(upstream.statusCode, responseHeaders);
    response.end(upstream.body);
    logEvent({
      event: "provider-call-completed",
      provider_call_count: providerCallCount,
      provider_status: upstream.statusCode,
      response_bytes: upstream.body.length,
      response_sha256: sha256(upstream.body),
    });
  } catch (error) {
    const reasonCode =
      error instanceof Error && error.message === "provider-timeout"
        ? "provider-timeout"
        : "provider-transport-failed";
    logEvent({
      event: "provider-call-failed",
      provider_call_count: providerCallCount,
      reason_code: reasonCode,
    });
    respondJson(response, 502, reasonCode);
  }
});

server.on("clientError", (_error, socket) => {
  socket.end("HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n");
});

server.listen(LISTEN_PORT, LISTEN_HOST, () => {
  logEvent({
    event: "broker-ready",
    listen_port: LISTEN_PORT,
    allowed_path: ALLOWED_PATH,
    maximum_provider_calls: 1,
    maximum_request_bytes: MAX_REQUEST_BYTES,
    maximum_output_tokens: MAX_OUTPUT_TOKENS,
  });
});

process.on("SIGTERM", () => {
  server.close(() => process.exit(0));
});
