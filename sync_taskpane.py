r"""
Copy taskpane source files into docs/ for GitHub Pages hosting.
Run this after editing any file in EMR4 Sidebar/src/taskpane/, then git push.

Usage:
    .venv\Scripts\python sync_taskpane.py
"""
import shutil
from pathlib import Path

SRC  = Path("EMR4 Sidebar/src/taskpane")
DEST = Path("docs/taskpane")

files = [
    "taskpane.html",
    "taskpane.css",
    "shortcuts.json",
    "office-host-runtime.js",
    "clinician-one-document-context.js",
    "hosting-policy.js",
]
for f in files:
    shutil.copy2(SRC / f, DEST / f)
    print(f"  copied {f}")

# Keep the published taskpane byte-identical to the source. Environment-specific
# routing belongs in deployment configuration, not a hidden publication rewrite.
shutil.copy2(SRC / "taskpane.js", DEST / "taskpane.js")
print("  copied taskpane.js")

if (SRC / "assets" / "emr_cube1.png").exists():
    shutil.copy2(SRC / "assets" / "emr_cube1.png", DEST / "assets" / "emr_cube1.png")
    print("  copied assets/emr_cube1.png")

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
