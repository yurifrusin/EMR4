# Disposable PostgreSQL parse/catalogue RLS lock-visibility rebind

Date: 2026-08-09

Status: bounded characterization candidate; behavior runtime remains closed

The deterministic parent at exact source
`3644c951f9b0a446d802ed31ef04c23f139cb0d7` is renderer 2.0.10's 412-statement,
1,391,506 canonical LF bytes in its inert artifact with SHA-256
`sha256:28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800`
and render-manifest file SHA-256
`sha256:8ced08cb218b4a19cb1abbf41930db3dcec0ac1e60fa132d38e9fba8c813c49e`.

The sole SQL semantic change from the preceding accepted artifact is
`LIFECYCLE` visibility in `pol_cf_01_update USING`. The producer-only
`WITH CHECK`, direct grants, functions, triggers, relations, role population
and statement population remain unchanged.

Because PostgreSQL owns canonical policy-expression deparsing, the fixed-path
parse harness first binds this exact parent in `characterization_only` mode.
One newly owned `postgres:16-bookworm` container may install the exact artifact
under `--pull=never` and `--network=none`, reproduce the rollback and complete
catalogue population checks, emit only the closed query digests and then be
removed by exact verified ID. No characterized digest is accepted by itself.

Only after that container is absent may the contract bind the full exact
digest set, with every unchanged catalogue query required to equal its prior
accepted value and only the policy digest eligible to differ. A second newly
owned container must then reproduce the exact digest-bound pass and exact-ID
cleanup. Characterization and exact pass are separate attempts; neither may
reuse a container or mutate the inert parent.

This descendant proves parse, atomic installation, catalogue/privilege shape
and cleanup only. It invokes no entry point, trigger or policy behavior and
opens no application migration, operational database, product or patient
data, provider, application/API/Diary wiring, watcher/listener/feed,
command/write, deployment, production, release, Pages or protected-ref
authority.
