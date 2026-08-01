#!/usr/bin/env python3
"""Build the closed, synthetic-only Raisa Office public-host context."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_ROOT = REPO_ROOT / "deploy" / "raisa-office-web-dev"
SIDEBAR_ROOT = REPO_ROOT / "EMR4 Sidebar"
DIST_ROOT = SIDEBAR_ROOT / "dist"
DIARY_ROOT = REPO_ROOT / "docs" / "diary"
IMAGES_ROOT = REPO_ROOT / "docs" / "images"

DIST_FILES = (
    "taskpane.html",
    "taskpane.css",
    "taskpane.js",
    "polyfill.js",
    "hosting-policy.js",
    "assets/emr_cube1.png",
    "assets/icon-32.png",
    "assets/icon-80.png",
)
DIARY_FILES = (
    "diary.html",
    "diary.css",
    "diary.js",
    "meta-grid.css",
    "meta-grid.js",
    "office-bootstrap.js",
)
ROOT_FILES = ("Dockerfile", ".dockerignore", "server.mjs")
PUBLIC_PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_origin(origin: str) -> str:
    parsed = urlparse(origin)
    if (
        parsed.params
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or not parsed.netloc
    ):
        raise ValueError("origin must contain scheme and authority only")
    normalized = f"{parsed.scheme}://{parsed.netloc}"
    local = parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
    cloud_run = (
        parsed.scheme == "https"
        and parsed.hostname is not None
        and parsed.hostname.startswith("raisa-office-web-dev-")
        and (
            parsed.hostname.endswith(".a.run.app")
            or parsed.hostname.endswith(".australia-southeast1.run.app")
        )
        and parsed.port is None
    )
    if not (local or cloud_run):
        raise ValueError(
            "origin must be exact loopback HTTP or raisa-office-web-dev run.app HTTPS"
        )
    return normalized


def require_file(root: Path, relative: str) -> Path:
    if (
        relative != ".dockerignore"
        and not PUBLIC_PATH_RE.fullmatch(relative)
    ) or ".." in Path(relative).parts:
        raise ValueError(f"unsafe allowlist path: {relative}")
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"missing, non-file or symlinked input: {path}")
    return path


def validate_dist() -> None:
    html = require_file(DIST_ROOT, "taskpane.html").read_text(encoding="utf-8")
    required = (
        'src="hosting-policy.js?v=1"',
        'src="polyfill.js"',
        'src="taskpane.js"',
        'href="taskpane.css?v=57"',
    )
    for marker in required:
        if html.count(marker) != 1:
            raise ValueError(f"production taskpane must contain exactly one {marker}")
    forbidden = (
        "office-host-runtime.js",
        "clinician-one-document-context.js",
        "taskpane.js?v=",
        "www.contoso.com",
        "localhost:8001",
    )
    for marker in forbidden:
        if marker in html:
            raise ValueError(f"production taskpane contains forbidden marker: {marker}")
    if list(DIST_ROOT.glob("*.map")):
        raise ValueError("production build emitted source maps")


def prepare(output: Path, origin: str) -> dict:
    exact_origin = validate_origin(origin)
    validate_dist()
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    public = output / "public"
    public.mkdir()

    copied: list[Path] = []
    for relative in DIST_FILES:
        source = require_file(DIST_ROOT, relative)
        target = public / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(target)
    for relative in DIARY_FILES:
        source = require_file(DIARY_ROOT, relative)
        target = public / "diary" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied.append(target)
    image_source = require_file(IMAGES_ROOT, "emr_cube1.png")
    image_target = public / "images" / "emr_cube1.png"
    image_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(image_source, image_target)
    copied.append(image_target)

    for relative in ROOT_FILES:
        source = require_file(DEPLOY_ROOT, relative)
        shutil.copyfile(source, output / relative)

    manifest = {
        "contract_version": "raisa.static-content-manifest.v1",
        "data_class": "authored_synthetic",
        "authority": {
            "backend": False,
            "command": False,
            "credential": False,
            "document_write": False,
            "microphone": False,
            "production": False,
            "provider": False,
        },
        "files": [
            {
                "path": path.relative_to(public).as_posix(),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in sorted(copied)
        ],
    }
    manifest_path = public / "content-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    manifest_template = require_file(
        DEPLOY_ROOT, "manifest-template.xml"
    ).read_text(encoding="utf-8")
    if manifest_template.count("__RAISA_PUBLIC_ORIGIN__") != 4:
        raise ValueError("Office manifest origin placeholder count changed")
    materialized = manifest_template.replace("__RAISA_PUBLIC_ORIGIN__", exact_origin)
    if "__RAISA_PUBLIC_ORIGIN__" in materialized:
        raise ValueError("Office manifest retains an origin placeholder")
    (output / "manifest.xml").write_text(
        materialized, encoding="utf-8", newline="\n"
    )

    context_files = sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    )
    expected_context = sorted(
        [
            *ROOT_FILES,
            "manifest.xml",
            "public/content-manifest.json",
            *(f"public/{relative}" for relative in DIST_FILES),
            *(f"public/diary/{relative}" for relative in DIARY_FILES),
            "public/images/emr_cube1.png",
        ]
    )
    if context_files != expected_context:
        raise ValueError("generated context differs from its closed allowlist")
    return {
        "result": "pass",
        "output": str(output.resolve()),
        "origin": exact_origin,
        "context_file_count": len(context_files),
        "content_manifest_sha256": sha256(manifest_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--origin", required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.output.resolve(), args.origin)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"result": "fail", "reason": str(error)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
