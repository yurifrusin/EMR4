# Ariadne agent error and correction register revision 154

Date: 2026-08-10

Status: corrected; database gate pending

Revision 154 adds AER-0180.

## AER-0180 — serial pytest option delimiter omitted

The first expanded static packet put pytest options immediately after the
serial-wrapper script without its required `--` argparse remainder delimiter.
The wrapper rejected the command before acquiring the shared lock or starting
pytest. No database, Docker, provider or evidence operation occurred.

The fresh invocation used `scripts/ariadne_serial_pytest.py --` before the
pytest vector and acquired the shared lock. This delimiter is now mandatory
whenever the first forwarded argument begins with a dash.
