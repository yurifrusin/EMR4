import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize, sep } from "node:path";

const PORT = Number.parseInt(process.env.PORT || "8080", 10);
const MODE = process.env.RAISA_HOSTING_MODE || "";
const EXPECTED_ORIGIN = process.env.EXPECTED_PUBLIC_ORIGIN || "";
const PUBLIC_ROOT = join(import.meta.dirname, "public");

const MIME_TYPES = Object.freeze({
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
});

function parseExpectedOrigin() {
  let url;
  try {
    url = new URL(EXPECTED_ORIGIN);
  } catch {
    throw new Error("EXPECTED_PUBLIC_ORIGIN must be an absolute origin");
  }
  if (url.origin !== EXPECTED_ORIGIN || url.pathname !== "/") {
    throw new Error("EXPECTED_PUBLIC_ORIGIN must contain an origin only");
  }
  if (MODE === "local_acceptance") {
    if (
      url.protocol !== "http:"
      || url.hostname !== "127.0.0.1"
      || !url.port
    ) {
      throw new Error("local_acceptance requires an exact loopback HTTP origin");
    }
    return url;
  }
  if (MODE === "public_https_development") {
    const exactService =
      url.hostname.startsWith("raisa-office-web-dev-")
      && (
        url.hostname.endsWith(".a.run.app")
        || url.hostname.endsWith(".australia-southeast1.run.app")
      );
    if (url.protocol !== "https:" || url.port || !exactService) {
      throw new Error(
        "public_https_development requires the exact raisa-office-web-dev run.app origin"
      );
    }
    return url;
  }
  throw new Error("RAISA_HOSTING_MODE is not admitted");
}

const expectedUrl = parseExpectedOrigin();
const manifest = JSON.parse(
  await readFile(join(PUBLIC_ROOT, "content-manifest.json"), "utf8")
);
if (
  manifest.contract_version !== "raisa.static-content-manifest.v1"
  || !Array.isArray(manifest.files)
) {
  throw new Error("content manifest is not admitted");
}
const allowedFiles = new Set(
  manifest.files.map(item => {
    if (
      !item
      || typeof item.path !== "string"
      || !/^[a-zA-Z0-9][a-zA-Z0-9._/-]*$/.test(item.path)
      || item.path.includes("..")
      || typeof item.sha256 !== "string"
    ) {
      throw new Error("content manifest contains an unsafe entry");
    }
    return `/${item.path}`;
  })
);
allowedFiles.add("/content-manifest.json");

const contentSecurityPolicy = [
  "default-src 'self'",
  "base-uri 'none'",
  "object-src 'none'",
  "form-action 'none'",
  "frame-src 'self'",
  [
    "frame-ancestors",
    "https://onedrive.live.com",
    "https://word.cloud.microsoft",
    "https://*.officeapps.live.com",
    "https://*.office.com",
    "https://*.microsoft365.com",
    "https://*.sharepoint.com",
  ].join(" "),
  "script-src 'self' https://appsforoffice.microsoft.com",
  "style-src 'self'",
  "img-src 'self' data:",
  [
    "connect-src",
    "'self'",
    "https://appsforoffice.microsoft.com",
    "https://*.officeapps.live.com",
  ].join(" "),
].join("; ");

function applyHeaders(response, contentType) {
  response.setHeader("Cache-Control", "no-store, max-age=0");
  response.setHeader("Content-Security-Policy", contentSecurityPolicy);
  response.setHeader("Cross-Origin-Resource-Policy", "same-origin");
  response.setHeader("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()");
  response.setHeader("Referrer-Policy", "no-referrer");
  response.setHeader("X-Content-Type-Options", "nosniff");
  if (contentType) response.setHeader("Content-Type", contentType);
}

function send(response, status, body, contentType) {
  applyHeaders(response, contentType);
  const payload = Buffer.from(body);
  response.statusCode = status;
  response.setHeader("Content-Length", String(payload.length));
  if (response.req.method === "HEAD") {
    response.end();
  } else {
    response.end(payload);
  }
}

function hostingPolicyScript() {
  const publicMode = MODE === "public_https_development";
  const policy = {
    contract_version: "raisa.public-hosting-policy.v1",
    mode: publicMode ? MODE : "local_acceptance",
    data_class: "authored_synthetic",
    expected_origin: EXPECTED_ORIGIN,
    provider_authority: false,
    backend_authority: false,
    credential_authority: false,
    microphone_authority: false,
    command_authority: false,
    document_write_authority: false,
    production_authority: false,
  };
  return `window.RAISA_PUBLIC_HOSTING_POLICY=Object.freeze(${JSON.stringify(policy)});\n`;
}

function requestMatchesExpectedHost(request) {
  const host = request.headers.host || "";
  const forwardedProto = request.headers["x-forwarded-proto"];
  if (MODE === "local_acceptance") {
    return host === expectedUrl.host && !forwardedProto;
  }
  return host === expectedUrl.host && forwardedProto === "https";
}

const server = createServer(async (request, response) => {
  if (request.method !== "GET" && request.method !== "HEAD") {
    response.setHeader("Allow", "GET, HEAD");
    send(response, 405, "method not allowed\n", "text/plain; charset=utf-8");
    return;
  }
  if (!requestMatchesExpectedHost(request)) {
    send(response, 421, "origin mismatch\n", "text/plain; charset=utf-8");
    return;
  }

  let url;
  try {
    url = new URL(request.url, EXPECTED_ORIGIN);
  } catch {
    send(response, 400, "bad request\n", "text/plain; charset=utf-8");
    return;
  }
  const path = url.pathname === "/" ? "/taskpane.html" : url.pathname;
  // Cloud Run reserves some externally requested paths ending in "z".
  // Keep /healthz for existing local acceptance while exposing /health for
  // the real run.app route.
  if (path === "/health" || path === "/healthz") {
    send(
      response,
      200,
      '{"status":"ok","authority":"none"}\n',
      "application/json; charset=utf-8"
    );
    return;
  }
  if (path === "/hosting-policy.js") {
    send(
      response,
      200,
      hostingPolicyScript(),
      "text/javascript; charset=utf-8"
    );
    return;
  }
  let decodedPath;
  try {
    decodedPath = decodeURIComponent(path);
  } catch {
    send(response, 400, "bad request\n", "text/plain; charset=utf-8");
    return;
  }
  if (
    path.includes("\\")
    || path.includes("\0")
    || decodedPath.includes("..")
    || decodedPath !== path
    || !allowedFiles.has(path)
  ) {
    send(response, 404, "not found\n", "text/plain; charset=utf-8");
    return;
  }

  const relative = path.slice(1);
  const candidate = normalize(join(PUBLIC_ROOT, relative));
  if (!candidate.startsWith(`${normalize(PUBLIC_ROOT)}${sep}`)) {
    send(response, 404, "not found\n", "text/plain; charset=utf-8");
    return;
  }
  try {
    const fileStat = await stat(candidate);
    if (!fileStat.isFile()) throw new Error("not a file");
    const body = await readFile(candidate);
    send(
      response,
      200,
      body,
      MIME_TYPES[extname(candidate)] || "application/octet-stream"
    );
  } catch {
    send(response, 404, "not found\n", "text/plain; charset=utf-8");
  }
});

server.listen(PORT, "0.0.0.0");
