"""
create_patient_file.py — Generate a new EMR4 Centaur patient .docx

The core function `create_patient_docx()` is the integration point for the future
New Patient userform.  Import it from a FastAPI endpoint like so:

    from create_patient_file import create_patient_docx, PatientData
    path = create_patient_docx(patient, output_dir=Path("/mnt/sharepoint/patients"))

CLI usage:
    python create_patient_file.py
    python create_patient_file.py --first Billy --last Frusin --dob 15-10-2015 \\
        --sex Male --address "15 Rose St Blacktown NSW 2148" \\
        --phone "0412 345 678" --medicare "1234567891"
"""

import argparse
import shutil
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


# ── Section headings — Dr Shera structure ─────────────────────────────────────
# Order and exact text must match PROTECTED_SECTIONS in taskpane.js.
# "Contemporaneous Notes" is the AI anchor — do not rename.
SECTION_HEADINGS = [
    "Care Plans, Health Assessments and Recalls",
    "Family History",
    "Medical History",
    "Social History",
    "Current Drugs",
    "Drug Reactions",
    "Contemporaneous Notes",
    "Vaccinations",
    "Specialist Reports",
    "Diagnostic Imaging",
    "Pathology Results",
    "ECG Records",
    "Prescription Records",
    "Correspondence",
    "Management Articles",
]

EMR4_BLUE   = RGBColor(0x00, 0x00, 0xCC)
HEADER_GREY = "E8E8E8"

_CUSTOM_XML_NS = "http://emr4.com/ns/document"
_CUSTOM_XML_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<emr4:root xmlns:emr4="{_CUSTOM_XML_NS}">
  <emr4:document-type>patient</emr4:document-type>
  <emr4:version>1.0</emr4:version>
</emr4:root>"""

_CUSTOM_XML_RELS_ENTRY = (
    '<Relationship Id="rIdEMR4Custom" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml" '
    'Target="../customXml/item1.xml"/>'
)

_CUSTOM_XML_PROPS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ds:datastoreItem ds:itemID="{EMR4-0001-0000-0000-000000000001}"
  xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml">
  <ds:schemaRefs/>
</ds:datastoreItem>"""


@dataclass
class PatientData:
    """All fields the New Patient userform will collect."""
    first_name:      str
    last_name:       str
    date_of_birth:   date
    sex:             str            # "Male" | "Female" | "Other"
    address:         str = ""
    phone:           str = ""
    medicare_number: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _shade_cell(cell, fill_hex: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def _hide_table_borders(table) -> None:
    tblPr = table._tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        table._tbl.insert(0, tblPr)
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "none")
        borders.append(el)
    tblPr.append(borders)


def _inject_custom_xml(docx_path: Path) -> None:
    """Injects emr4:document-type=patient Custom XML Part so the taskpane
    auto-detects this as a patient file and activates patient mode."""
    tmp = docx_path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(docx_path, "r") as zin:
        existing = set(zin.namelist())
        rels_xml = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        if "rIdEMR4Custom" not in rels_xml:
            rels_xml = rels_xml.replace(
                "</Relationships>",
                f"  {_CUSTOM_XML_RELS_ENTRY}\n</Relationships>",
            )
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = (
                    rels_xml.encode()
                    if item.filename == "word/_rels/document.xml.rels"
                    else zin.read(item.filename)
                )
                zout.writestr(item, data)
            if "customXml/item1.xml" not in existing:
                zout.writestr("customXml/item1.xml", _CUSTOM_XML_CONTENT)
            if "customXml/itemProps1.xml" not in existing:
                zout.writestr("customXml/itemProps1.xml", _CUSTOM_XML_PROPS)
    shutil.move(str(tmp), str(docx_path))


# ── Core function ─────────────────────────────────────────────────────────────

def create_patient_docx(patient: PatientData, output_dir: Path = Path(".")) -> Path:
    """
    Generate an EMR4 patient .docx and return its path.

    This is the function a FastAPI /patients/{id}/create-file endpoint should call.
    The file is named  FIRSTNAME LASTNAME DD-MM-YYYY.docx  so the taskpane
    auto-detect logic (autoDetectPatient) can identify the patient from the filename.
    """
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    dob_str = patient.date_of_birth.strftime("%d-%m-%Y")
    age     = _age(patient.date_of_birth)
    name_uc = f"{patient.first_name.upper()} {patient.last_name.upper()}"

    # ── Demographics header ───────────────────────────────────────────────────
    # Replicates the grey shaded box in the reference (Billy / Margaret) files.
    table = doc.add_table(rows=1, cols=1)
    _hide_table_borders(table)
    cell = table.cell(0, 0)
    _shade_cell(cell, HEADER_GREY)

    def _header_line(text: str, first: bool = False) -> None:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.bold      = True
        run.font.color.rgb = EMR4_BLUE
        run.font.size      = Pt(11)

    _header_line(f"{name_uc}   dob {dob_str}   {age} years old   {patient.sex}", first=True)
    if patient.address:
        _header_line(patient.address)
    contact_parts = []
    if patient.phone:
        contact_parts.append(f"Phone: {patient.phone}")
    if patient.medicare_number:
        contact_parts.append(f"Medicare: {patient.medicare_number}")
    if contact_parts:
        _header_line("       ".join(contact_parts))

    doc.add_paragraph()  # spacer between header and first section

    # ── Section headings ──────────────────────────────────────────────────────
    for heading_text in SECTION_HEADINGS:
        h = doc.add_heading(heading_text, level=1)
        for run in h.runs:
            run.font.color.rgb = EMR4_BLUE
        doc.add_paragraph()  # blank line under each heading for GP to write into

    # ── Save & inject Custom XML Part ────────────────────────────────────────
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{name_uc} {dob_str}.docx"
    out_path = output_dir / filename
    doc.save(str(out_path))
    _inject_custom_xml(out_path)
    return out_path


# ── CLI ───────────────────────────────────────────────────────────────────────

def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    return input(f"  {label}{suffix}: ").strip() or default


def _parse_dob(s: str) -> date:
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unrecognised date: {s!r}  — use DD-MM-YYYY")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Create an EMR4 patient .docx")
    ap.add_argument("--first",    metavar="NAME",       help="First name")
    ap.add_argument("--last",     metavar="NAME",       help="Last name")
    ap.add_argument("--dob",      metavar="DD-MM-YYYY", help="Date of birth")
    ap.add_argument("--sex",      choices=["Male", "Female", "Other"])
    ap.add_argument("--address",  default=None,          help="Full address")
    ap.add_argument("--phone",    default=None,          help="Phone number")
    ap.add_argument("--medicare", default=None,          help="Medicare number")
    ap.add_argument("--out",      default=".",          metavar="DIR",
                    help="Output directory (default: current directory)")
    args = ap.parse_args()

    print("\nEMR4 — New Patient File Generator")
    print("-" * 36)

    # Required fields — prompt if not supplied via CLI
    first   = args.first or _prompt("First name")
    last    = args.last  or _prompt("Last name")
    dob_raw = args.dob   or _prompt("Date of birth (DD-MM-YYYY)")
    sex     = args.sex   or _prompt("Sex", "Female")

    # Optional fields — only prompt when running fully interactively (no CLI args at all)
    cli_mode = bool(args.first or args.last or args.dob or args.sex)
    address  = args.address  or ("" if cli_mode else _prompt("Address (optional)"))
    phone    = args.phone    or ("" if cli_mode else _prompt("Phone (optional)"))
    medicare = args.medicare or ("" if cli_mode else _prompt("Medicare number (optional)"))

    patient = PatientData(
        first_name      = first.strip(),
        last_name       = last.strip(),
        date_of_birth   = _parse_dob(dob_raw),
        sex             = sex,
        address         = address,
        phone           = phone,
        medicare_number = medicare,
    )

    out = create_patient_docx(patient, output_dir=Path(args.out))
    print(f"\n[OK] {out}")
