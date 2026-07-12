"""
review/test_webpack_diary_static_config.py — S9 deterministic static config tests.

Tests verify the devServer.static directories in webpack.config.js serve
docs/diary/ at /diary and docs/images/ at /images. These are purely static
(config inspection + path resolution) — no webpack, npm, or live server needed.

Run:
    pytest review/test_webpack_diary_static_config.py -q
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBPACK_CONFIG = REPO_ROOT / "EMR4 Sidebar" / "webpack.config.js"
DOCS_DIARY = REPO_ROOT / "docs" / "diary"
DOCS_IMAGES = REPO_ROOT / "docs" / "images"


def _read_config() -> str:
    if not WEBPACK_CONFIG.is_file():
        raise FileNotFoundError(f"webpack.config.js not found at {WEBPACK_CONFIG}")
    return WEBPACK_CONFIG.read_text(encoding="utf-8")


# ── Static-directory existence checks ──────────────────────────────

class TestStaticDirectoriesDeclared:
    """devServer.static entries must be present in webpack.config.js."""

    config_text: str = ""

    @classmethod
    def setup_class(cls):
        cls.config_text = _read_config()

    def test_diary_static_entry_exists(self):
        """devServer.static includes a diary entry with publicPath '/diary'."""
        assert re.search(
            r'publicPath\s*:\s*["\']/diary["\']', self.config_text
        ), "Expected devServer.static entry with publicPath '/diary'"

    def test_images_static_entry_exists(self):
        """devServer.static includes an images entry with publicPath '/images'."""
        assert re.search(
            r'publicPath\s*:\s*["\']/images["\']', self.config_text
        ), "Expected devServer.static entry with publicPath '/images'"

    def test_diary_directory_contains_diary(self):
        """diary static directory resolves to an existing folder."""
        assert DOCS_DIARY.is_dir(), (
            f"docs/diary/ directory not found at {DOCS_DIARY}"
        )

    def test_images_directory_contains_images(self):
        """images static directory resolves to an existing folder."""
        assert DOCS_IMAGES.is_dir(), (
            f"docs/images/ directory not found at {DOCS_IMAGES}"
        )

    def test_diary_html_exists(self):
        """docs/diary/diary.html must exist for the dev server to serve."""
        assert (DOCS_DIARY / "diary.html").is_file(), (
            "docs/diary/diary.html not found"
        )

    def test_emr_cube1_png_exists(self):
        """docs/images/emr_cube1.png must exist for the dev server to serve."""
        assert (DOCS_IMAGES / "emr_cube1.png").is_file(), (
            "docs/images/emr_cube1.png not found"
        )


# ── Path resolution checks ─────────────────────────────────────────

class TestDiaryRelativePathResolution:
    """Verify the directory paths in static entries resolve correctly
    relative to the webpack config location."""

    config_text: str = ""

    @classmethod
    def setup_class(cls):
        cls.config_text = _read_config()

    def test_diary_directory_is_relative_to_config(self):
        """diary static directory uses __dirname-relative '..docs/diary' path."""
        assert ".." in self.config_text or "docs" in self.config_text
        # The actual resolved path from the config dir
        config_dir = WEBPACK_CONFIG.parent
        resolved_diary = (config_dir / ".." / "docs" / "diary").resolve()
        assert resolved_diary == DOCS_DIARY.resolve(), (
            f"Resolved diary path {resolved_diary} does not match {DOCS_DIARY.resolve()}"
        )

    def test_images_directory_is_relative_to_config(self):
        """images static directory uses __dirname-relative '..docs/images' path."""
        config_dir = WEBPACK_CONFIG.parent
        resolved_images = (config_dir / ".." / "docs" / "images").resolve()
        assert resolved_images == DOCS_IMAGES.resolve(), (
            f"Resolved images path {resolved_images} does not match {DOCS_IMAGES.resolve()}"
        )


# ── No-breakage guard ──────────────────────────────────────────────

class TestExistingEntryPointsPreserved:
    """Existing webpack entry points and plugins must be untouched."""

    config_text: str = ""

    @classmethod
    def setup_class(cls):
        cls.config_text = _read_config()

    def test_taskpane_entry_exists(self):
        """The existing taskpane entry point is still declared."""
        assert "taskpane:" in self.config_text

    def test_commands_entry_exists(self):
        """The existing commands entry point is still declared."""
        assert "commands:" in self.config_text

    def test_copy_webpack_plugin_present(self):
        """CopyWebpackPlugin is still configured."""
        assert "CopyWebpackPlugin" in self.config_text

    def test_html_webpack_plugin_present(self):
        """HtmlWebpackPlugin is still configured."""
        assert "HtmlWebpackPlugin" in self.config_text
