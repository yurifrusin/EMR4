const SAFE_METADATA = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$/;
const SAFE_FIELD_NAME = /^[A-Za-z_][A-Za-z0-9_.-]{0,63}$/;

const PROFILE_RULES = {
  terra: {
    allowedKeywords: new Set([
      "additionalProperties",
      "anyOf",
      "enum",
      "items",
      "maxItems",
      "minItems",
      "properties",
      "required",
      "title",
      "type",
    ]),
    enumTypes: new Set(["string", "integer", "number", "boolean"]),
    booleanEnumAllowed: true,
  },
  gemini: {
    allowedKeywords: new Set([
      "additionalProperties",
      "anyOf",
      "enum",
      "items",
      "maxItems",
      "minItems",
      "properties",
      "required",
      "title",
      "type",
    ]),
    enumTypes: new Set(["string", "integer", "number"]),
    booleanEnumAllowed: false,
  },
};

function valueMatchesType(value, type) {
  if (type === "string") return typeof value === "string";
  if (type === "boolean") return typeof value === "boolean";
  if (type === "integer") return Number.isInteger(value);
  if (type === "number") return typeof value === "number" && Number.isFinite(value);
  return false;
}

function walkSchema(node, profile, path = "$") {
  if (node === null || typeof node !== "object" || Array.isArray(node)) {
    throw new Error(`provider-schema-node-invalid:${path}`);
  }
  for (const keyword of Object.keys(node)) {
    if (!profile.allowedKeywords.has(keyword)) {
      throw new Error(`provider-schema-keyword-invalid:${path}:${keyword}`);
    }
  }
  if (Object.hasOwn(node, "enum")) {
    if (
      typeof node.type !== "string" ||
      !profile.enumTypes.has(node.type) ||
      !Array.isArray(node.enum) ||
      node.enum.length === 0 ||
      node.enum.some((value) => !valueMatchesType(value, node.type))
    ) {
      throw new Error(`provider-schema-enum-invalid:${path}`);
    }
    if (node.type === "boolean" && !profile.booleanEnumAllowed) {
      throw new Error(`provider-schema-boolean-enum-invalid:${path}`);
    }
  }
  if (node.type === "object") {
    if (
      node.additionalProperties !== false ||
      node.properties === null ||
      typeof node.properties !== "object" ||
      Array.isArray(node.properties) ||
      !Array.isArray(node.required) ||
      node.required.length !== Object.keys(node.properties).length ||
      !Object.keys(node.properties).every((key) => node.required.includes(key))
    ) {
      throw new Error(`provider-schema-object-invalid:${path}`);
    }
    for (const [key, child] of Object.entries(node.properties)) {
      walkSchema(child, profile, `${path}.properties.${key}`);
    }
  }
  if (node.type === "array") {
    walkSchema(node.items, profile, `${path}.items`);
  }
  if (Object.hasOwn(node, "anyOf")) {
    if (!Array.isArray(node.anyOf) || node.anyOf.length === 0) {
      throw new Error(`provider-schema-anyof-invalid:${path}`);
    }
    node.anyOf.forEach((child, index) =>
      walkSchema(child, profile, `${path}.anyOf[${index}]`),
    );
  }
}

export function compileProviderSchema(schema, laneId) {
  const profile = PROFILE_RULES[laneId];
  if (profile === undefined) throw new Error("provider-profile-invalid");
  const compiled = structuredClone(schema);
  if (
    compiled?.type !== "object" ||
    Object.hasOwn(compiled, "anyOf")
  ) {
    throw new Error("provider-schema-root-invalid");
  }
  walkSchema(compiled, profile);
  return compiled;
}

export function buildGeminiGenerateContentRequest(
  payload,
  providerSchema,
  maximumOutputTokens = 2_048,
) {
  if (
    payload === null ||
    typeof payload !== "object" ||
    Array.isArray(payload) ||
    typeof payload.system_prompt !== "string" ||
    payload.system_prompt.length === 0 ||
    typeof payload.prompt !== "string" ||
    payload.prompt.length === 0 ||
    providerSchema === null ||
    typeof providerSchema !== "object" ||
    Array.isArray(providerSchema) ||
    !Number.isSafeInteger(maximumOutputTokens) ||
    maximumOutputTokens < 1
  ) {
    throw new Error("gemini-request-input-invalid");
  }
  const request = {
    systemInstruction: { parts: [{ text: payload.system_prompt }] },
    contents: [{ role: "user", parts: [{ text: payload.prompt }] }],
    generationConfig: {
      maxOutputTokens: maximumOutputTokens,
      responseMimeType: "application/json",
      responseJsonSchema: providerSchema,
      thinkingConfig: { thinkingLevel: "MEDIUM", includeThoughts: false },
    },
    store: false,
  };
  if (Object.hasOwn(request.generationConfig, "candidateCount")) {
    throw new Error("gemini-3x-candidate-count-unsupported");
  }
  return request;
}

function boundedScalar(value) {
  if (typeof value === "string" && SAFE_METADATA.test(value)) return value;
  if (typeof value === "number" && Number.isSafeInteger(value)) return value;
  return undefined;
}

function canonicalJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  }
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map(
        (key) =>
          `${JSON.stringify(key)}:${canonicalJson(value[key])}`,
      )
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sealAuditEvent(
  event,
  auditSequence,
  previousEventHash,
  hashFunction,
) {
  if (
    event === null ||
    typeof event !== "object" ||
    Array.isArray(event) ||
    !Number.isSafeInteger(auditSequence) ||
    auditSequence < 1 ||
    typeof previousEventHash !== "string" ||
    typeof hashFunction !== "function"
  ) {
    throw new Error("audit-event-input-invalid");
  }
  const record = {
    audit_sequence: auditSequence,
    previous_event_sha256: previousEventHash,
    ...event,
  };
  const eventHash = hashFunction(Buffer.from(canonicalJson(record)));
  return { ...record, event_sha256: eventHash };
}

export function typedOutputAuditManifest(drafts, hashFunction) {
  if (!Array.isArray(drafts) || typeof hashFunction !== "function") return [];
  return drafts.map((draft) => {
    const value =
      draft !== null && typeof draft === "object" && !Array.isArray(draft)
        ? draft
        : {};
    const payload =
      value.payload !== null &&
      typeof value.payload === "object" &&
      !Array.isArray(value.payload)
        ? value.payload
        : {};
    const result = {
      draft_sha256: hashFunction(Buffer.from(canonicalJson(value))),
      top_level_field_names: Object.keys(value)
        .filter((key) => SAFE_FIELD_NAME.test(key))
        .sort(),
      payload_field_names: Object.keys(payload)
        .filter((key) => SAFE_FIELD_NAME.test(key))
        .sort(),
    };
    for (const key of ["id", "output_port_id", "frame_type"]) {
      const clean = boundedScalar(value[key]);
      if (clean !== undefined) result[key] = clean;
    }
    return result;
  });
}

function namedHeader(headers, names) {
  if (headers === null || typeof headers !== "object") return undefined;
  for (const name of names) {
    const raw = headers[name] ?? headers[name.toLowerCase()];
    const value = Array.isArray(raw) ? raw[0] : raw;
    const clean = boundedScalar(value);
    if (clean !== undefined) return clean;
  }
  return undefined;
}

export function sanitiseProviderErrorMetadata(
  laneId,
  responseBody,
  responseHeaders = {},
) {
  let parsed;
  try {
    const text = Buffer.isBuffer(responseBody)
      ? responseBody.toString("utf8")
      : String(responseBody);
    parsed = JSON.parse(text);
  } catch {
    parsed = {};
  }
  const error =
    parsed?.error !== null &&
    typeof parsed?.error === "object" &&
    !Array.isArray(parsed.error)
      ? parsed.error
      : {};
  const result = {};
  const fields = {
    provider_error_status: error.status,
    provider_error_type: error.type,
    provider_error_code: error.code,
    provider_error_parameter: error.param,
  };
  for (const [key, value] of Object.entries(fields)) {
    const clean = boundedScalar(value);
    if (clean !== undefined) result[key] = clean;
  }
  const requestId = namedHeader(
    responseHeaders,
    laneId === "terra"
      ? ["x-request-id"]
      : ["x-goog-request-id", "x-request-id"],
  );
  if (requestId !== undefined) result.provider_request_id = requestId;
  return result;
}
