import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import {
  buildGeminiGenerateContentRequest,
  compileProviderSchema,
} from "./ariadne_provider_contracts.mjs";

const ROOT = new URL("../", import.meta.url);
const SOURCE_DIR = new URL(
  "orchestration/continuity/ariadne-terra-gemini-comparison/",
  ROOT,
);
const SCHEMA_URL = new URL("provider-output.schema.json", SOURCE_DIR);
const PROFILES_URL = new URL("provider-contract-profiles.json", SOURCE_DIR);
const OBSERVATION_URL = new URL(
  "attempt-003-gemini-request-contract-observation.json",
  SOURCE_DIR,
);

function readJson(url) {
  return JSON.parse(readFileSync(url, "utf8"));
}

function hash(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

function assertEqual(actual, expected, reason) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(reason);
  }
}

const schema = compileProviderSchema(readJson(SCHEMA_URL), "gemini");
const profile = readJson(PROFILES_URL).profiles.gemini;
const observation = readJson(OBSERVATION_URL);
const request = buildGeminiGenerateContentRequest(
  {
    system_prompt: "authored-synthetic-system-sentinel",
    prompt: "authored-synthetic-user-sentinel",
  },
  schema,
  2_048,
);
const generationConfigFields = Object.keys(request.generationConfig).sort();
const expectedGenerationConfigFields = [
  "maxOutputTokens",
  "responseJsonSchema",
  "responseMimeType",
  "thinkingConfig",
];
const unsupportedFields = profile.unsupported_generation_config_fields;
const historicalFields =
  observation.observed_before_repair.generation_config_fields;

assertEqual(
  unsupportedFields,
  ["candidateCount"],
  "gemini-unsupported-field-profile-invalid",
);
if (!historicalFields.includes("candidateCount")) {
  throw new Error("attempt3-candidate-count-observation-missing");
}
if (Object.hasOwn(request.generationConfig, "candidateCount")) {
  throw new Error("gemini-3x-candidate-count-still-present");
}
assertEqual(
  generationConfigFields,
  expectedGenerationConfigFields,
  "gemini-generation-config-fields-invalid",
);
if (
  request.generationConfig.responseJsonSchema !== schema ||
  request.generationConfig.responseMimeType !== "application/json" ||
  request.generationConfig.maxOutputTokens !== 2_048 ||
  request.generationConfig.thinkingConfig.thinkingLevel !== "MEDIUM" ||
  request.generationConfig.thinkingConfig.includeThoughts !== false ||
  request.store !== false
) {
  throw new Error("gemini-request-bounded-values-invalid");
}

const result = {
  schema_version: "ariadne.gemini_provider_blocked_diagnostic.v1",
  status: "passed",
  result: "ariadne_gemini_provider_blocked_request_contract_diagnostic_pass",
  runtime_attempt_id_examined: observation.runtime_attempt_id,
  attempt_003_observation:
    observation.attempt_003_audit_observation,
  diagnosis: {
    finding_code: "gemini_3x_candidate_count_unsupported",
    unsupported_field: "candidateCount",
    field_observed_in_attempt_003_constructor: true,
    field_present_after_repair: false,
    capable_of_observed_invalid_argument: true,
    exact_historical_cause_proven: false,
    uncertainty_reason:
      "raw_provider_error_message_was_intentionally_not_retained",
    schema_complexity_excluded_as_possible_cause: false,
  },
  repaired_request_contract: {
    top_level_fields: Object.keys(request).sort(),
    generation_config_fields: generationConfigFields,
    provider_schema_sha256: hash(Buffer.from(JSON.stringify(schema))),
    maximum_output_tokens: request.generationConfig.maxOutputTokens,
    response_mime_type: request.generationConfig.responseMimeType,
    thinking_level: request.generationConfig.thinkingConfig.thinkingLevel,
    thoughts_included: request.generationConfig.thinkingConfig.includeThoughts,
    provider_storage_requested: request.store,
    prompt_or_schema_values_recorded: false,
  },
  boundaries: {
    authored_synthetic_sentinels_only: true,
    provider_call_performed: false,
    credential_read: false,
    prompt_transmitted: false,
    network_opened: false,
    container_started: false,
    database_accessed: false,
    product_api_accessed: false,
    attempt_003_ledger_mutated: false,
  },
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
