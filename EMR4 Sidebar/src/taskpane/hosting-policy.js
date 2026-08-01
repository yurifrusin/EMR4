/*
 * Fail-closed default. A narrowly configured development host may replace
 * this response at request time with an origin-bound synthetic-only policy.
 */
window.RAISA_PUBLIC_HOSTING_POLICY = Object.freeze({
  contract_version: "raisa.public-hosting-policy.v1",
  mode: "disabled",
  data_class: "none",
  expected_origin: "",
  provider_authority: false,
  backend_authority: false,
  credential_authority: false,
  microphone_authority: false,
  command_authority: false,
  document_write_authority: false,
  production_authority: false,
});
