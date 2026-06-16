"""
create_diary_file.py -- Generate a daily EMR4 Centaur Diary .docx

The diary file (Diary_DD-MM-YYYY.docx) is hosted on OneDrive/SharePoint and
co-authored by receptionist + nurses in real time via Word Online.  The taskpane
reads the <emr4:document-type>diary</emr4:document-type> Custom XML Part and
switches to Diary Mode (Schedule / Waiting Room / Messages tabs).

In this increment (Phase 2 / Increment 1) the file contains:
  - A shaded date Heading 1
  - A short guide block explaining the chevron appointment syntax
  - A few example »HH:MM Patient Name entries
Phase 2 / Increment 2 will add Parse & Lock (Ctrl+Alt+L) that converts those
chevron lines into locked content-control appointment blocks.

CLI usage:
    python create_diary_file.py
    python create_diary_file.py --date 16-06-2026 --out ./patient_files
"""

import argparse
import zipfile
from datetime import date, datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


# Typography -- match the patient-file style for visual consistency.
EMR4_BLUE    = RGBColor(0x00, 0x00, 0xFF)
BODY_FONT    = "Century Schoolbook"
HEADING_FONT = "Garamond"
BODY_PT      = 11
HEADING_PT   = 12
HEADER_GREY  = "E6E6E6"

# Custom XML -- document-type = diary (taskpane reads this to enter Diary Mode).
_CUSTOM_XML_NS = "http://emr4.com/ns/document"
_CUSTOM_XML_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<emr4:root xmlns:emr4="{_CUSTOM_XML_NS}">
  <emr4:document-type>diary</emr4:document-type>
  <emr4:version>1.0</emr4:version>
</emr4:root>"""

_CUSTOM_XML_RELS_ENTRY = (
    '<Relationship Id="rIdEMR4Custom" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml" '
    'Target="../customXml/item1.xml"/>'
)

_CUSTOM_XML_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ds:datastoreItem ds:itemID="{EMR4-0002-0000-0000-000000000001}"
  xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml">
  <ds:schemaRefs/>
</ds:datastoreItem>"""


# ── Helpers (mirror create_patient_file.py helpers) ───────────────────────────

def _apply_template_styles(doc: Document) -> None:
    """Set Normal and Heading 1 fonts to match the EMR4 patient-file template."""
    normal = doc.styles["Normal"]
    nf = normal.font
    nf.name = BODY_FONT
    nf.size = Pt(BODY_PT)

    h1 = doc.styles["Heading 1"]
    h1f = h1.font
    h1f.name = HEADING_FONT
    h1f.size = Pt(HEADING_PT)
    h1f.bold = True
    h1f.color.rgb = EMR4_BLUE


def _insert_element_before(parent, new_child, before_tag: str) -> None:
    """Insert new_child before the first occurrence of before_tag in parent.
    Falls back to append if the tag is absent. Used to maintain OOXML child-
    element order so Word Online does not silently drop the element."""
    ref = parent.find(qn(before_tag))
    if ref is not None:
        ref.addprevious(new_child)
    else:
        parent.append(new_child)


def _shade_paragraph(para, fill_hex: str) -> None:
    """Apply a solid background fill to a paragraph's <w:pPr>.
    Inserts <w:shd> before <w:spacing> / <w:jc> so Word Online honours it.
    (Word Online is strict about CT_PPr child-element order; Desktop isn't.)"""
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    # Must appear before w:spacing and w:jc in CT_PPr.
    _insert_element_before(pPr, shd, "w:spacing")


def _inject_custom_xml(doc_path: Path) -> None:
    """Inject the EMR4 Custom XML Part (document-type=diary) into the .docx zip.

    python-docx's blank Document ships with its own customXml/item1.xml
    (a Bibliography Sources stub) — we unconditionally replace it with ours.
    Mirrors the fixed approach in create_patient_file.py.
    """
    import shutil

    OUR_SLOTS = {
        "customXml/item1.xml",
        "customXml/itemProps1.xml",
        "customXml/_rels/item1.xml.rels",
    }
    _ITEM_RELS = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdProps1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXmlProps" '
        'Target="itemProps1.xml"/>'
        '</Relationships>'
    )

    tmp = doc_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(doc_path, "r") as zin:
        rels_xml = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        if "rIdEMR4Custom" not in rels_xml:
            rels_xml = rels_xml.replace(
                "</Relationships>",
                _CUSTOM_XML_RELS_ENTRY + "</Relationships>",
            )
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in OUR_SLOTS:
                    continue  # replaced unconditionally below
                data = (
                    rels_xml.encode("utf-8")
                    if item.filename == "word/_rels/document.xml.rels"
                    else zin.read(item.filename)
                )
                if item.filename == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    if "customXml/item1.xml" not in text:
                        entry = '<Override PartName="/customXml/item1.xml" ContentType="application/xml"/>'
                        props = '<Override PartName="/customXml/itemProps1.xml" ContentType="application/vnd.openxmlformats-officedocument.customXmlProperties+xml"/>'
                        text = text.replace("</Types>", entry + props + "</Types>")
                    data = text.encode("utf-8")
                zout.writestr(item, data)
            # Write our Custom XML Part unconditionally (replaces the python-docx
            # Bibliography stub that occupies this slot in a blank Document).
            zout.writestr("customXml/item1.xml", _CUSTOM_XML_CONTENT.encode("utf-8"))
            zout.writestr("customXml/itemProps1.xml", _CUSTOM_XML_PROPS.encode("utf-8"))
            zout.writestr("customXml/_rels/item1.xml.rels", _ITEM_RELS.encode("utf-8"))

    shutil.move(str(tmp), str(doc_path))


# ── Diary generator ───────────────────────────────────────────────────────────

def create_diary_docx(diary_date: date, output_dir: Path = Path(".")) -> Path:
    """Generate a Diary_DD-MM-YYYY.docx for the given date.

    Returns the Path of the written file.
    """
    doc = Document()
    _apply_template_styles(doc)

    date_str = diary_date.strftime("%d-%m-%Y")
    # %-d (no-pad day) is Linux-only; strip the leading zero manually for portability.
    day_label = diary_date.strftime("%A %d %B %Y").replace(
        " 0", " ", 1  # "Monday 06 June" -> "Monday 6 June"
    )

    # Date heading (Heading 1, shaded grey, centred).
    h = doc.add_heading(f"Diary  {day_label}", level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _shade_paragraph(h, HEADER_GREY)

    # Guide block.
    doc.add_paragraph()
    guide = doc.add_paragraph()
    guide_run = guide.add_run(
        "Type appointments as:  » HH:MM  Patient Name  [Appointment Type]\n"
        "Press Ctrl+Alt+L (Parse & Lock) to register them in the system and lock the line.\n"
        "Press Ctrl+Alt+U (Unlock) to release a line for editing."
    )
    guide_run.font.name = BODY_FONT
    guide_run.font.size = Pt(BODY_PT)
    guide_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)  # grey guide text
    _shade_paragraph(guide, "F0F0F0")

    doc.add_paragraph()

    # Example chevron entries (illustrative; not yet parsed).
    examples = [
        "» 09:00  Margaret Thompson  Standard Consult",
        "» 09:15  Billy Frusin  Standard Consult",
        "» 09:30  [Available]",
        "» 09:45  [Available]",
        "» 10:00  [Available]",
    ]
    for line in examples:
        p = doc.add_paragraph(line)
        run = p.runs[0]
        run.font.name = BODY_FONT
        run.font.size = Pt(BODY_PT)

    # Write to disk.
    filename = f"Diary_{date_str}.docx"
    out_path = output_dir / filename
    doc.save(str(out_path))

    # Inject Custom XML Part (document-type=diary).
    _inject_custom_xml(out_path)

    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an EMR4 diary .docx for a given date.")
    parser.add_argument("--date", default=None,
                        help="Date as DD-MM-YYYY (default: today)")
    parser.add_argument("--out", default=".", help="Output directory (default: .)")
    args = parser.parse_args()

    if args.date:
        diary_date = datetime.strptime(args.date, "%d-%m-%Y").date()
    else:
        diary_date = date.today()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = create_diary_docx(diary_date, output_dir=out_dir)
    print(f"Created: {path}")
