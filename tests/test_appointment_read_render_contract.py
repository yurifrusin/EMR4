"""Source checks and deferred direct-DOM conformance specification.

No browser is launched by this module. The reviewed browser profile must later
mount the exact HTML/CSS/JS files and assert:

* Tab reaches each labelled selector and focus remains visibly indicated.
* After a reviewed serializer run, normal and fallback accepted modes have
  identical row text, local accessible start/end/zone/status/warning, source
  line, row order, and table-cell facts.
* At 390px the list has no horizontal clipping; table mode scrolls horizontally
  while retaining native headers and a caption.
* Rejected mode after a previously accepted render removes all source/row/
  warning facts and never reveals the planted raw-input marker.
* A forged object with unknown fields, empty or truncated columns, a write
  affordance, or a bad version
  yields only the generic empty state, including after a previously valid view.
* The preview issues no request and exposes no booking or confirmation control.
* With no generated snapshots module, the page stays generic empty and its
  three selectors remain disabled. Keyboard and focus inspection follows a
  reviewed snapshot generation, never a hand-authored demo constant.

These cases are a specification, not claimed executed DOM evidence.
"""

from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "static" / "demo"


class ShellParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


class ReadRenderSourceContractTests(unittest.TestCase):
    def test_shell_has_only_three_labelled_demo_controls(self):
        parser = ShellParser()
        parser.feed((ROOT / "appointment-read-render.html").read_text(encoding="utf-8"))
        labels = {a.get("for") for tag, a in parser.attrs if tag == "label"}
        selects = {a.get("id") for tag, a in parser.attrs if tag == "select"}
        self.assertEqual(labels, {"view-choice", "mode-choice", "scenario-choice"})
        self.assertEqual(selects, labels)
        self.assertTrue(all("disabled" in a for tag, a in parser.attrs if tag == "select"))
        self.assertNotIn("form", parser.tags)
        self.assertNotIn("button", parser.tags)
        self.assertNotIn("a", parser.tags)
        self.assertFalse(any(any(k.startswith("on") for k in a) for _, a in parser.attrs))

    def test_shell_loads_only_local_sources_with_closed_connection_policy(self):
        parser = ShellParser()
        parser.feed((ROOT / "appointment-read-render.html").read_text(encoding="utf-8"))
        scripts = [a for tag, a in parser.attrs if tag == "script"]
        links = [a for tag, a in parser.attrs if tag == "link"]
        self.assertEqual([a.get("src") for a in scripts], ["appointment-read-render.js"])
        self.assertEqual([a.get("href") for a in links], ["appointment-read-render.css"])
        policies = [a.get("content", "") for tag, a in parser.attrs if tag == "meta" and a.get("http-equiv") == "Content-Security-Policy"]
        self.assertEqual(len(policies), 1)
        self.assertIn("connect-src 'none'", policies[0])
        self.assertIn("form-action 'none'", policies[0])

    def test_dom_source_avoids_html_injection_and_network_primitives(self):
        source = (ROOT / "appointment-read-render.js").read_text(encoding="utf-8")
        self.assertIn("export function renderReadOnly", source)
        self.assertIn("node.textContent = value", source)
        self.assertIn('candidate.columns.length !== 4', source)
        self.assertIn('import("./generated-snapshots.js")', source)
        self.assertIn("presentedRow(row, snapshot.timezone)", source)
        self.assertNotIn("33333333-3333-4333-8333-333333333333", source)
        for forbidden in ("innerHTML", "outerHTML", "insertAdjacentHTML", "fetch(", "XMLHttpRequest", "WebSocket", "document.write"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
