#!/usr/bin/env python3
import sys
import re
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

# Set output streams to UTF-8 if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths to EMR4 HTML files relative to repo root
HTML_FILES = [
    "docs/diary/diary.html",
    "docs/taskpane/taskpane.html",
    "docs/command-centre/command-centre.html"
]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOYED_BASE_URL = "https://yurifrusin.github.io/EMR4"

def get_git_diff_files():
    """Returns a list of files with local modifications compared to HEAD."""
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD", "--name-only"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True
        )
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception as e:
        print(f"Error running git diff: {e}")
        return []

def get_git_file_content_at_head(rel_path):
    """Retrieves file content at HEAD using git show."""
    try:
        res = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True
        )
        return res.stdout
    except Exception:
        return None

def fetch_deployed_html(rel_path):
    """Fetches the deployed HTML content from GitHub Pages."""
    url = f"{DEPLOYED_BASE_URL}/{rel_path.replace('docs/', '')}"
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "https" or parsed_url.netloc != "yurifrusin.github.io":
        raise ValueError(f"Refusing to fetch unexpected deployed URL: {url}")
    try:
        # Add a cache buster query parameter to ensure we fetch fresh content
        req = urllib.request.Request(
            f"{url}?probe={urllib.parse.quote(str(sys.float_info))}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        # URL is constrained to GitHub Pages HTTPS above.
        with urllib.request.urlopen(req, timeout=5) as response:  # nosec B310
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Warning: Could not fetch deployed version of {url}: {e}")
        return None

def parse_asset_versions(html_content):
    """Parses script and link tags to extract referenced local assets and their ?v=X versions."""
    if not html_content:
        return {}
    # Matches src="asset.js?v=N" or href="asset.css?v=N"
    script_pattern = re.compile(r'<(?:script\s+[^>]*src|link\s+[^>]*href)=["\']([^"\']+)["\']', re.IGNORECASE)
    
    assets = {}
    for match in script_pattern.finditer(html_content):
        url = match.group(1)
        # Filter for local CSS/JS references with ?v= query parameter
        if (".js" in url or ".css" in url) and not url.startswith("http") and not url.startswith("//"):
            parts = url.split("?v=")
            name = parts[0]
            version = parts[1] if len(parts) > 1 else None
            assets[name] = version
    return assets

def main():
    print("=" * 70)
    print(" EMR4 Frontend Asset Version Integrity Check")
    print("=" * 70)

    modified_files = get_git_diff_files()
    errors_found = 0

    for html_rel_path in HTML_FILES:
        html_path = REPO_ROOT / html_rel_path
        if not html_path.exists():
            print(f"[ERROR] {html_rel_path} does not exist.")
            errors_found += 1
            continue

        print(f"\nAnalyzing: {html_rel_path}")
        html_content = html_path.read_text(encoding="utf-8", errors="ignore")
        local_assets = parse_asset_versions(html_content)

        # Retrieve HEAD version of the HTML
        head_html_content = get_git_file_content_at_head(html_rel_path)
        head_assets = parse_asset_versions(head_html_content) if head_html_content else {}

        # Fetch deployed version of the HTML
        deployed_html_content = fetch_deployed_html(html_rel_path)
        deployed_assets = parse_asset_versions(deployed_html_content) if deployed_html_content else {}

        for asset_name, local_v in local_assets.items():
            # Resolve the asset file path relative to HTML directory
            html_dir = Path(html_rel_path).parent
            asset_rel_path = (html_dir / asset_name).as_posix()
            asset_abs_path = REPO_ROOT / asset_rel_path

            # 1. Verify file exists
            if not asset_abs_path.exists():
                print(f"  [ERROR] Referenced asset '{asset_name}' not found at {asset_rel_path}")
                errors_found += 1
                continue

            # 2. Check if local asset file has been modified compared to HEAD
            is_modified = asset_rel_path in modified_files
            head_v = head_assets.get(asset_name)
            deployed_v = deployed_assets.get(asset_name)

            print(f"  - {asset_name:<25} Local v={local_v or 'None':<5} HEAD v={head_v or 'None':<5} Deployed v={deployed_v or 'None':<5}")

            if is_modified:
                print(f"    * Note: '{asset_name}' has unsaved changes compared to HEAD.")
                if local_v == head_v:
                    print(f"    [ERROR] '{asset_rel_path}' is modified, but version in '{html_rel_path}' remains '{local_v}' (not bumped compared to HEAD).")
                    errors_found += 1
                else:
                    print(f"    [OK] Version successfully bumped from '{head_v}' to '{local_v}'.")
            elif local_v != head_v and head_v is not None:
                print(f"    * Note: Version bumped without local file changes (e.g. metadata only sync).")

    print("\n" + "=" * 70)
    if errors_found > 0:
        print(f" [FAILED] Verification Failed: Found {errors_found} version-bump or asset path errors.")
        print("Please resolve the version mismatches before committing.")
        print("=" * 70)
        sys.exit(1)
    else:
        print(" [PASSED] Verification Passed: All modified assets have appropriate version bumps.")
        print("=" * 70)
        sys.exit(0)

if __name__ == "__main__":
    main()
