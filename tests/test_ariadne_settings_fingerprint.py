from pathlib import Path

from orchestration_harness.settings_fingerprint import settings_fingerprint


def test_fingerprint_changes_when_any_yaml_setting_changes(tmp_path: Path):
    (tmp_path / "worker_pool.yaml").write_text("workers: []\n", encoding="utf-8")
    (tmp_path / "deepcode_mailbox_profile.yaml").write_text("pty: disabled\n", encoding="utf-8")
    before = settings_fingerprint(tmp_path)

    (tmp_path / "deepcode_mailbox_profile.yaml").write_text("pty: enabled\n", encoding="utf-8")

    assert settings_fingerprint(tmp_path) != before


def test_fingerprint_rejects_empty_settings_directory(tmp_path: Path):
    try:
        settings_fingerprint(tmp_path)
    except ValueError as error:
        assert "contains no YAML files" in str(error)
    else:
        raise AssertionError("empty settings directory must fail closed")


def test_fingerprint_is_stable_across_lf_and_crlf_checkouts(tmp_path: Path):
    lf = tmp_path / "lf"
    crlf = tmp_path / "crlf"
    lf.mkdir()
    crlf.mkdir()
    (lf / "worker_pool.yaml").write_bytes(b"workers:\n  - id: one\n")
    (crlf / "worker_pool.yaml").write_bytes(b"workers:\r\n  - id: one\r\n")

    assert settings_fingerprint(lf) == settings_fingerprint(crlf)
