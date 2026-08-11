# Ariadne agent error and correction register — revision 242

Date: 2026-08-11

Revision 242 records and closes AER-0275. The register now contains 275 bounded
known incidents.

## AER-0275 — stale behavior-parent equality constants corrected

The CF-D2 broad deterministic implementation gate found one repository defect:
the historical behavior-plan equality test still expected the pre-recovery
frame-mask parse evidence plus the older inert-SQL and manifest heads and
hashes. The accepted behavior contract had already been rebound to the later
admission-replay exact reproduction and the unchanged 424-statement artifact at
its accepted recovery heads.

The live CF-D2 parent validator correctly admitted the current contract and all
bound bytes. Only the three duplicated test tuples were stale. They now match
the accepted behavior contract exactly:

- runtime evidence `provider-free-disposable-postgresql-evidence-admission-replay-winner-exact-reproduction.json`, source `36f076775e676620f99650043b05bd852e3a84be`, SHA-256 `9ad82882150f8795789c332db8bed6e4b50d150986a6066ce832f12e48246d24`;
- inert SQL source `5a9a7ae907308aa0a8a4256e9043b833f8c416ae`, SHA-256 `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`; and
- render manifest at the same source, SHA-256 `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`.

The corrected focused equality node passes. No runtime evidence, accepted
contract, SQL, provider, Docker resource, product data, protected evidence or
Git ref changed. The complete inherited deterministic packet remains mandatory
before the CF-D2 implementation veto.
