# Ariadne agent error and correction register — revision 223

Date: 2026-08-11

Revision 223 records AER-0258 and brings the register to 258 bounded known
incidents.

## AER-0258 — wrong exact API Spine test filename

The first Sol AES-C3 recovery regression command named nonexistent
`tests/test_api_spine_contract.py`. Pytest returned
`file or directory not found` before collecting tests. That command supplied
no passing evidence and changed no source, fixture, runtime or ref.

Sol recovered the already frozen exact path from the committed worker packet:
`tests/test_api_spine_artifacts.py`. The complete C3/C2/C1/C0/API packet was
then rerun serially from the start and all 106 tests passed. Future focused
dispatches copy exact paths from the frozen packet or verify the one named path
before starting pytest.
