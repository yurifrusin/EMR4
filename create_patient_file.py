"""
Generate an EMR4 patient Word document (.docx) matching Dr Shera's formatting.

Fonts:    Century Schoolbook (body), Garamond Bold (headings)
Colours:  #0000FF blue (headings + demographics), black (body)
Header:   Centred, grey (#E6E6E6) shaded block — Name/DOB/Age/Sex, Address, Phone/Medicare

Usage:
    .venv\Scripts\python create_patient_file.py "Margaret Thompson"
    .venv\Scripts\python create_patient_file.py --id <patient-uuid>
"""
import io
import sys
import uuid
import argparse
import zipfile
from datetime import date, datetime

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.database import SessionLocal
from app.models.patients import Patient
from app.models.clinical import Allergy, Prescription


# ── Colours ───────────────────────────────────────────────────────────────────
BLUE    = RGBColor(0x00, 0x00, 0xFF)
RED     = RGBColor(0xC0, 0x00, 0x00)
GREY_BG = "E6E6E6"   # demographics shading fill


# ── Low-level XML helpers ─────────────────────────────────────────────────────

def _get_or_add_pPr(para):
    pPr = para._element.find(qn("w:pPr"))
    if pPr is None:
        pPr = OxmlElement("w:pPr")
        para._element.insert(0, pPr)
    return pPr


def set_para_shading(para, fill: str):
    pPr = _get_or_add_pPr(para)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  fill)
    pPr.append(shd)


def add_bookmark(para, name: str, bm_id: int):
    run = para.runs[0] if para.runs else para.add_run()
    r = run._r
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"),   str(bm_id))
    start.set(qn("w:name"), name)
    r.insert(0, start)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bm_id))
    r.addnext(end)


# ── Style setup ───────────────────────────────────────────────────────────────

def configure_styles(doc: Document):
    """Set Normal → Century Schoolbook 11pt, Heading 1 → Garamond Bold Blue 12pt."""
    nm = doc.styles["Normal"]
    nm.font.name = "Century Schoolbook"
    nm.font.size = Pt(11)

    h1 = doc.styles["Heading 1"]
    h1.font.name       = "Garamond"
    h1.font.bold       = True
    h1.font.size       = Pt(12)
    h1.font.color.rgb  = BLUE
    h1.paragraph_format.space_before = Pt(10)
    h1.paragraph_format.space_after  = Pt(2)
    # Remove any keep-with-next / outline-level clutter that Word adds
    h1.paragraph_format.keep_with_next = False


# ── Paragraph builders ────────────────────────────────────────────────────────

def demo_line(doc: Document, text: str):
    """Centred, grey-shaded, blue Century Schoolbook — the demographics header style."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_para_shading(p, GREY_BG)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(0)
    run = p.add_run(text)
    run.font.name      = "Century Schoolbook"
    run.font.bold      = True
    run.font.color.rgb = BLUE
    run.font.size      = Pt(11)
    return p


def section_heading(doc: Document, title: str):
    p = doc.add_heading(title, level=1)
    for run in p.runs:
        run.font.name      = "Garamond"
        run.font.bold      = True
        run.font.color.rgb = BLUE
    return p


def body_para(doc: Document, text: str = ""):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(3)
    for run in p.runs:
        run.font.name = "Century Schoolbook"
    return p


def calc_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# ── Document builder ──────────────────────────────────────────────────────────

def build_patient_document(patient: Patient, allergies: list, medications: list) -> Document:
    doc = Document()
    configure_styles(doc)

    # Page margins — match the original's feel
    for section in doc.sections:
        section.top_margin    = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin   = Inches(0.9)
        section.right_margin  = Inches(0.9)

    age     = calc_age(patient.date_of_birth)
    dob_str = patient.date_of_birth.strftime("%d-%m-%Y")
    now_str = datetime.now().strftime("%d-%m-%Y")
    time_str = datetime.now().strftime("%I:%M %p").lstrip("0")

    sex = patient.sex or ""
    addr_parts = [patient.address_line1, patient.address_suburb,
                  patient.address_state, patient.address_postcode]
    addr = "  ".join(p for p in addr_parts if p) or "Address not recorded"
    phone    = patient.phone_mobile or patient.phone_home or "Phone not recorded"
    medicare = patient.medicare_number or "Medicare not recorded"

    # ── Grey demographics header (3 lines, centred) ────────────────────────────
    demo_line(doc,
        f"{patient.first_name.upper()} {patient.last_name.upper()}"
        f"   dob {dob_str}    {age} years old    {sex}")
    demo_line(doc, addr)
    demo_line(doc, f"Phone: {phone}        Medicare: {medicare}")

    # Spacer after header
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after  = Pt(0)

    # ── Care Plans, Health Assessments, Recalls ────────────────────────────────
    section_heading(doc, "Care Plans, Health Assessments and Recalls")
    body_para(doc)

    # ── Family History ─────────────────────────────────────────────────────────
    section_heading(doc, "Family History")
    body_para(doc)

    # ── Medical History ────────────────────────────────────────────────────────
    section_heading(doc, "Medical History")
    body_para(doc)

    # ── Social History ─────────────────────────────────────────────────────────
    section_heading(doc, "Social History")
    body_para(doc, "Private Health Insurance: ")

    # ── Current Drugs ──────────────────────────────────────────────────────────
    section_heading(doc, "Current Drugs")
    if medications:
        for med in medications:
            dosage = f"  —  {med.dosage_text}" if getattr(med, "dosage_text", None) else ""
            body_para(doc, f"{med.drug_name}{dosage}")
    else:
        body_para(doc)

    # ── Drug Reactions ─────────────────────────────────────────────────────────
    section_heading(doc, "Drug Reactions")
    if allergies:
        for a in allergies:
            life_threat = "life" in (a.severity or "").lower()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after  = Pt(3)
            run = p.add_run(
                f"{a.substance}  —  {a.reaction or a.severity or ''}"
                + ("  ⚠ LIFE-THREATENING" if life_threat else "")
            )
            run.font.name      = "Century Schoolbook"
            run.font.size      = Pt(11)
            run.font.color.rgb = RED if life_threat else RGBColor(0, 0, 0)
            run.bold           = life_threat
    else:
        body_para(doc, "No known drug reactions.")

    # ── Contemporaneous Notes ──────────────────────────────────────────────────
    section_heading(doc, "Contemporaneous Notes")

    # Ready-to-type dated header — bookmark used by the add-in F2-equivalent
    p = doc.add_paragraph()
    add_bookmark(p, "latest_consult_entry", 1)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(
        f"{now_str}  {patient.first_name} {patient.last_name}  {time_str}  {age} years old."
    )
    run.font.name = "Century Schoolbook"
    run.font.size = Pt(11)
    run.bold      = True

    for _ in range(6):
        body_para(doc)

    # ── Vaccinations ───────────────────────────────────────────────────────────
    section_heading(doc, "Vaccinations")
    body_para(doc)

    # ── Specialist Reports ────────────────────────────────────────────────────
    section_heading(doc, "Specialist Reports")
    body_para(doc)

    # ── Diagnostic Imaging ────────────────────────────────────────────────────
    section_heading(doc, "Diagnostic Imaging")
    body_para(doc)

    # ── Pathology Results ─────────────────────────────────────────────────────
    section_heading(doc, "Pathology Results")
    body_para(doc)

    # ── ECG Records ───────────────────────────────────────────────────────────
    section_heading(doc, "ECG Records")
    body_para(doc)

    # ── Prescription Records ──────────────────────────────────────────────────
    section_heading(doc, "Prescription Records")
    body_para(doc)

    # ── Correspondence ────────────────────────────────────────────────────────
    section_heading(doc, "Correspondence")
    body_para(doc)

    # ── Management Articles ───────────────────────────────────────────────────
    section_heading(doc, "Management Articles")
    body_para(doc)

    return doc


# ── Add-in auto-load embedding ────────────────────────────────────────────────

# Manifest add-in ID (must match manifest.xml <Id>)
ADDIN_ID = "38e3c046-c982-4e1f-bf8b-24e04e6c9f94"
ADDIN_VERSION = "1.0.0.0"

_WEB_EXT_XML = f"""\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<we:webextension
  xmlns:we="http://schemas.microsoft.com/office/webextensions/webextension/2010/11"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  id="{{2D0A3B6C-4E5F-7890-ABCD-EF1234567890}}">
  <we:reference id="{ADDIN_ID}" version="{ADDIN_VERSION}"
    store="developer" storeType="Developer"/>
  <we:alternateReferences/>
  <we:properties>
    <we:property name="Office.AutoShowTaskpaneWithDocument" value="true"/>
  </we:properties>
  <we:bindings/>
  <we:snapshot xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
</we:webextension>
"""

_TASKPANES_XML = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wetp:taskpanes
  xmlns:wetp="http://schemas.microsoft.com/office/webextensions/taskpanes/2010/11">
  <wetp:taskpane dockstate="right" visibility="1" width="350" row="4">
    <wetp:webextensionref
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
      r:id="rId_webext1"/>
  </wetp:taskpane>
</wetp:taskpanes>
"""

_CT_WEBEXT   = "application/vnd.ms-office.webextension+xml"
_CT_TASKPANE = "application/vnd.ms-office.webextensiontaskpanes+xml"
_REL_TASKPANE = "http://schemas.microsoft.com/office/2011/relationships/webextensiontaskpanes"
_REL_WEBEXT   = "http://schemas.microsoft.com/office/2011/relationships/webextension"


def embed_addin(filename: str) -> None:
    """
    Inject webExtension + taskpanes parts into the saved .docx so that
    Word (desktop and Online) auto-opens the EMR Centaur taskpane.
    """
    # Read the existing zip into memory
    with open(filename, "rb") as f:
        original = f.read()

    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(original), "r") as zin, \
         zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:

        existing_names = set(zin.namelist())

        for item in zin.infolist():
            data = zin.read(item.filename)

            # ── [Content_Types].xml — add two Override entries ─────────────
            if item.filename == "[Content_Types].xml":
                data = data.decode("utf-8")
                insert = ""
                if "/word/webExtensions/webExtension1.xml" not in data:
                    insert += (
                        f'<Override PartName="/word/webExtensions/webExtension1.xml"'
                        f' ContentType="{_CT_WEBEXT}"/>'
                    )
                if "/word/webExtensions/taskpanes.xml" not in data:
                    insert += (
                        f'<Override PartName="/word/webExtensions/taskpanes.xml"'
                        f' ContentType="{_CT_TASKPANE}"/>'
                    )
                if insert:
                    data = data.replace("</Types>", insert + "</Types>")
                data = data.encode("utf-8")

            # ── word/_rels/document.xml.rels — add taskpanes relationship ──
            elif item.filename == "word/_rels/document.xml.rels":
                data = data.decode("utf-8")
                if _REL_TASKPANE not in data:
                    rel = (
                        f'<Relationship Id="rId_taskpanes"'
                        f' Type="{_REL_TASKPANE}"'
                        f' Target="webExtensions/taskpanes.xml"/>'
                    )
                    data = data.replace("</Relationships>", rel + "</Relationships>")
                data = data.encode("utf-8")

            zout.writestr(item, data)

        # ── Add the two new parts ──────────────────────────────────────────
        if "word/webExtensions/webExtension1.xml" not in existing_names:
            zout.writestr("word/webExtensions/webExtension1.xml",
                          _WEB_EXT_XML.encode("utf-8"))

        if "word/webExtensions/taskpanes.xml" not in existing_names:
            zout.writestr("word/webExtensions/taskpanes.xml",
                          _TASKPANES_XML.encode("utf-8"))

        # ── taskpanes needs its own _rels to point at webExtension1 ────────
        tp_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId_webext1" Type="{_REL_WEBEXT}"'
            f' Target="webExtension1.xml"/>'
            '</Relationships>'
        )
        if "word/webExtensions/_rels/taskpanes.xml.rels" not in existing_names:
            zout.writestr("word/webExtensions/_rels/taskpanes.xml.rels",
                          tp_rels.encode("utf-8"))

    with open(filename, "wb") as f:
        f.write(buf.getvalue())


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate EMR4 patient file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("name", nargs="?", help="Patient name (partial match)")
    group.add_argument("--id", dest="patient_id", help="Patient UUID")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.patient_id:
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(args.patient_id)).first()
        else:
            from sqlalchemy import or_
            q = db.query(Patient)
            for part in args.name.split():
                q = q.filter(or_(
                    Patient.first_name.ilike(f"%{part}%"),
                    Patient.last_name.ilike(f"%{part}%"),
                ))
            patient = q.first()

        if not patient:
            print("Patient not found.", file=sys.stderr)
            sys.exit(1)

        print(f"Generating file for: {patient.first_name} {patient.last_name}")

        allergies = db.query(Allergy).filter(Allergy.patient_id == patient.id).all()
        meds      = db.query(Prescription).filter(
            Prescription.patient_id == patient.id,
            Prescription.is_active == True,
        ).all()

        doc = build_patient_document(patient, allergies, meds)

        dob      = patient.date_of_birth.strftime("%d-%m-%Y")
        filename = f"{patient.first_name.upper()} {patient.last_name.upper()} {dob}.docx"
        doc.save(filename)
        embed_addin(filename)
        print(f"Saved: {filename}")
        print(f"  Allergies: {len(allergies)}  |  Medications: {len(meds)}")
        print(f"  Add-in embedded: EMR Centaur will auto-open with this document")

    finally:
        db.close()


if __name__ == "__main__":
    main()
