# Durability behavior RLS lock-visibility parent rebind

Date: 2026-08-09

Status: deterministic candidate pending fresh independent veto; runtime closed

Behavior attempts 001-023 remain immutable. Attempt 023 stopped at `BTR-E01`
with `CF004`, admitted zero of the exactly twenty ordered scenarios and removed
its exact owned container. The bounded diagnosis and accepted recovery preserve
the existing row lock while allowing the lifecycle entry point to see the
stream head through `pol_cf_01_update USING`; producer-only `WITH CHECK` and
zero lifecycle direct table DML/SELECT remain unchanged.

The behavior contract is rebound to:

- accepted parse evidence source
  `a7a780f9735d3c41095703d464611752f89685d9`;
- inert artifact SHA-256
  `sha256:28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800`;
- render-manifest file SHA-256
  `sha256:8ced08cb218b4a19cb1abbf41930db3dcec0ac1e60fa132d38e9fba8c813c49e`;
- structural source `338c30ddb01561ce97a4b9837317e771b555c221`;
  and
- body source `987f64a9f68c8dec2b99d5d39aa74e28411a82fa`.

The scenario order, scenario objects and `6/4/3/4/3` category coverage remain
byte-for-byte unchanged under canonical digest
`sha256:eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
No SQLSTATE, expected effect, principal, isolation shape, fixture coordinate,
rollback rule, claim boundary or containment rule is weakened.

Before attempt 024, the complete deterministic and hostile packet must pass
and one genuinely fresh Gemini 3.6 Flash/high exact-HEAD veto must accept the
current source. Only then may Sol run one newly owned `--pull=never`,
`--network=none` PostgreSQL 16 container with exact-ID cleanup. A failure
continues the accepted diagnose-repair-rerun sequence and never authorizes
scenario removal, superuser substitution, RLS disablement or parent mutation.

This rebind grants no applied migration, operational database, application,
API or Diary wiring, watcher/listener/feed, provider, command/write, patient,
product or protected data, deployment, production, release, Pages or
protected-ref authority. `docs/branding/` and unrelated untracked files remain
preserved and excluded.
