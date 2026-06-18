"""
Copy taskpane source files into docs/ for GitHub Pages hosting.
Run this after editing any file in EMR4 Sidebar/src/taskpane/, then git push.

Usage:
    .venv\Scripts\python sync_taskpane.py
"""
import shutil
from pathlib import Path

SRC  = Path("EMR4 Sidebar/src/taskpane")
DEST = Path("docs/taskpane")

files = ["taskpane.html", "taskpane.css", "shortcuts.json"]
for f in files:
    shutil.copy2(SRC / f, DEST / f)
    print(f"  copied {f}")

# taskpane.js gets special treatment — the docs/ version has the GitHub Pages
# BACKEND_URL patch. Re-apply it after copying.
src_js  = (SRC / "taskpane.js").read_text(encoding="utf-8")
patched = src_js.replace(
    "// When served by Node dev server (localhost:3000), hit the local FastAPI directly.\n"
    "// When served by FastAPI itself (via ngrok or production), use the same origin.\n"
    "const BACKEND_URL = (window.location.port === \"3000\")\n"
    "  ? \"http://localhost:8001\"\n"
    "  : window.location.origin;",
    "// Dev server (port 3000) → local FastAPI; ngrok URL → same origin; GitHub Pages → ngrok.\n"
    "const NGROK_URL   = \"https://property-cinch-backfield.ngrok-free.dev\";\n"
    "const BACKEND_URL = (window.location.port === \"3000\")\n"
    "  ? \"http://localhost:8001\"\n"
    "  : window.location.hostname.includes(\"ngrok\")\n"
    "    ? window.location.origin\n"
    "    : NGROK_URL;"
)
(DEST / "taskpane.js").write_text(patched, encoding="utf-8")
print("  copied + patched taskpane.js")

shutil.copy2(SRC / "assets" / "emr_centaur_logo.png", DEST / "assets" / "emr_centaur_logo.png")
print("  copied assets/emr_centaur_logo.png")
if (SRC / "assets" / "cuboid4.png").exists():
    shutil.copy2(SRC / "assets" / "cuboid4.png", DEST / "assets" / "cuboid4.png")
    print("  copied assets/cuboid4.png")

# Patch command-centre.js with the real ngrok URL (it lives directly in docs/command-centre/)
NGROK_URL = "https://property-cinch-backfield.ngrok-free.dev"
CC_JS = Path("docs/command-centre/command-centre.js")
if CC_JS.exists():
    cc_js = CC_JS.read_text(encoding="utf-8")
    if "PLACEHOLDER_NGROK_URL" in cc_js:
        CC_JS.write_text(cc_js.replace("PLACEHOLDER_NGROK_URL", NGROK_URL), encoding="utf-8")
        print("  patched docs/command-centre/command-centre.js (ngrok URL)")
    else:
        print("  command-centre.js already patched")

print("Done. Run: git add docs/ && git commit -m 'sync taskpane' && git push")
