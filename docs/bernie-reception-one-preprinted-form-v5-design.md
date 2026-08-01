# Reception One Pre-printed Form v5 Design

## Form ownership

The transport is split into two exact objects:

- the model body contains `operator_note`, `goal_code` and `steps`; and
- the broker-owned pre-print contains only `version_code: 3`.

The model body rejects missing and additional fields. After it passes, the
broker copies the three values without normalization and inserts the constant.
The resulting four-field object must pass the unchanged PlanProgram v3 JSON
Schema before compilation.

Three hashes make the assembly externally inspectable without retaining a raw
provider response:

1. model-form-body hash;
2. pre-printed-field-manifest hash; and
3. assembled PlanProgram hash.

The audit also records the two field manifests and
`broker_judgement_repair: false`.

## Untaught baseline

The system instruction explains the closed form, catalogue and safety
constraints, but provides no example answer, demonstration, prompt curriculum,
prompt search, fine-tune or weight change. Temperature and thinking budget are
zero. The purpose is to observe form-filling performance before adding a
teaching intervention.

## Correction dialogue

The inherited deterministic proofreader may open one correction turn only for
the existing allowlisted, coordinate-bounded findings. The ticket includes the
prior `goal_code` and `steps`, but excludes the rejected `operator_note` and the
broker-owned version. It contains no replacement selection or free-form
message. Turn two replaces all three model-authored fields and is terminal.

## Runtime topology

The occupied topology remains:

`credential-free cell -> internal relay -> one-use host broker -> exact Sydney Vertex endpoint`

The cell has the typed task and one-use relay capability, but no ADC, OAuth
credential, Google CLI state, provider key, service-account identifier, product
mount, database mount or unrestricted network. Only the broker reads the
existing impersonated ADC and constructs the Vertex request.

The provider-free real-isolation proof uses two separate non-root, read-only,
network-none fixture cells. Each emits only the three-field model body. Host
code performs the version injection, unchanged compilation, proofreader and
proposal-only in-memory execution. Both containers and images are removed and
the temporary build contexts disappear.

## API Spine disposition

This remains an internal default-off `admin_proposal` adapter. No API surface,
GraphQL mutation, REST command, database access, appointment confirmation or
write path changes. The backend-owned confirmation path is untouched.
