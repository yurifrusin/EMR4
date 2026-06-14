"""
Generate an EMR4 patient Word document (.docx) for a given patient.

The document follows Dr Shera's structure:
  Demographics → Care Plans/Recalls → Family Hx → Medical Hx → Social Hx
  → Current Drugs → Drug Reactions → Contemporaneous Notes → ...

Usage:
    .venv\Scripts\python create_patient_file.py "Margaret Thompson"
    .venv\Scripts\python create_patient_file.py --id <patient-uuid>
"""
import sys
import uuid
import argparse
from datetime import date, datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import lxml.etree as etree

from app.database import SessionLocal
from app.models.patients import Patient
from app.models.clinical import Allergy, Prescription


# ── Helpers ────────────────────────────────────────────────────────────────────

def calc_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def add_bookmark(paragraph, bookmark_name: str):
    """Add a Word bookmark to a paragraph so the add-in can navigate to it."""
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    tag = run._r
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(hash(bookmark_name) % 10000))
    start.set(qn("w:name"), bookmark_name)
    tag.insert(0, start)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(hash(bookmark_name) % 10000))
    tag.addnext(end)


def add_custom_xml_part(doc: Document, patient_id: str):
    """Embed the EMR4 Custom XML Part so the add-in knows this is a patient file."""
    # Build the XML
    nsmap = "xmlns:emr4=\"https://emr4.com.au/schemas/patient\""
    xml_str = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<emr4:root {nsmap}>'
        f'<emr4:document-type>patient</emr4:document-type>'
        f'<emr4:patient-id>{patient_id}</emr4:patient-id>'
        f'</emr4:root>'
    )

    # Add to the docx package
    part = doc.part
    pkg = part.package
    from docx.opc.part import Part
    from docx.opc.packuri import PackURI
    content_type = "application/xml"
    uri = PackURI(f"/customXml/item1.xml")

    # Check if already exists
    try:
        pkg.part_related_by("http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml")
        return
    except Exception:
        pass

    xml_part = Part(uri, content_type, xml_str.encode("utf-8"), pkg)
    part.relate_to(xml_part, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml")


def section_heading(doc: Document, title: str, bookmark: str = None) -> None:
    """Add a Heading 1 section marker matching the Billy Frusin style."""
    p = doc.add_heading(title, level=1)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    if bookmark:
        add_bookmark(p, bookmark)


def blank_content_paragraph(doc: Document, placeholder: str = "") -> None:
    p = doc.add_paragraph(placeholder)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)


# ── Document builder ───────────────────────────────────────────────────────────

def build_patient_document(patient: Patient, allergies: list, medications: list) -> Document:
    doc = Document()

    # Page margins — slightly narrower to maximise content area
    for section in doc.sections:
        section.top_margin    = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin   = Inches(0.9)
        section.right_margin  = Inches(0.9)

    age = calc_age(patient.date_of_birth)
    dob_str = patient.date_of_birth.strftime("%d-%m-%Y")
    now_str = datetime.now().strftime("%d-%m-%Y")

    # ── Demographics block ─────────────────────────────────────────────────────
    demo = doc.add_paragraph()
    demo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = demo.add_run(
        f"{patient.first_name.upper()} {patient.last_name.upper()}   "
        f"dob {dob_str}    {age} years old    {patient.sex or ''}"
    )
    run.bold = True
    run.font.size = Pt(13)

    addr_parts = [
        patient.address_line1,
        patient.address_suburb,
        patient.address_state,
        patient.address_postcode,
    ]
    addr = "  ".join(p for p in addr_parts if p)
    doc.add_paragraph(addr or "Address not recorded").paragraph_format.space_after = Pt(2)

    phone = patient.phone_mobile or patient.phone_home or "Phone not recorded"
    medicare = patient.medicare_number or "Medicare not recorded"
    doc.add_paragraph(f"Phone: {phone}    Medicare: {medicare}").paragraph_format.space_after = Pt(6)

    doc.add_paragraph()  # spacer

    # ── Care Plans, Health Assessments, Recalls ────────────────────────────────
    section_heading(doc, "Care Plans, Health Assessments and Recalls", "section_careplans")
    blank_content_paragraph(doc)

    # ── Family History ─────────────────────────────────────────────────────────
    section_heading(doc, "Family History", "section_family_history")
    blank_content_paragraph(doc)

    # ── Medical History ────────────────────────────────────────────────────────
    section_heading(doc, "Medical History", "section_medical_history")
    blank_content_paragraph(doc)

    # ── Social History ─────────────────────────────────────────────────────────
    section_heading(doc, "Social History", "section_social_history")
    blank_content_paragraph(doc, "Private Health Insurance: ")

    # ── Current Drugs ──────────────────────────────────────────────────────────
    section_heading(doc, "Current Drugs", "section_current_drugs")
    if medications:
        for med in medications:
            dosage = f"  —  {med.dosage_text}" if getattr(med, "dosage_text", None) else ""
            blank_content_paragraph(doc, f"{med.drug_name}{dosage}")
    else:
        blank_content_paragraph(doc)

    # ── Drug Reactions ─────────────────────────────────────────────────────────
    section_heading(doc, "Drug Reactions", "section_drug_reactions")
    if allergies:
        for a in allergies:
            severity_marker = "  ⚠ LIFE-THREATENING" if "life" in (a.severity or "").lower() else ""
            p = doc.add_paragraph()
            run = p.add_run(f"{a.substance}  —  {a.reaction or ''}{severity_marker}")
            if severity_marker:
                run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
                run.bold = True
            p.paragraph_format.space_after = Pt(4)
    else:
        blank_content_paragraph(doc, "No known drug reactions.")

    # ── Contemporaneous Notes ──────────────────────────────────────────────────
    section_heading(doc, "Contemporaneous Notes", "section_contemporaneous_notes")

    # Seed with a ready-to-use header for today's consult
    p = doc.add_paragraph()
    run = p.add_run(
        f"{now_str}  {patient.first_name} {patient.last_name}  {datetime.now().strftime('%I:%M %p')}  {age} years old."
    )
    run.bold = True
    run.font.size = Pt(11)
    add_bookmark(p, "latest_consult_entry")

    # Blank lines for writing
    for _ in range(6):
        doc.add_paragraph()

    # ── Vaccinations ───────────────────────────────────────────────────────────
    section_heading(doc, "Vaccinations", "section_vaccinations")
    blank_content_paragraph(doc)

    # ── Specialist Reports ────────────────────────────────────────────────────
    section_heading(doc, "Specialist Reports", "section_specialist_reports")
    blank_content_paragraph(doc)

    # ── Diagnostic Imaging ────────────────────────────────────────────────────
    section_heading(doc, "Diagnostic Imaging", "section_diagnostic_imaging")
    blank_content_paragraph(doc)

    # ── Pathology Results ─────────────────────────────────────────────────────
    section_heading(doc, "Pathology Results", "section_pathology_results")
    blank_content_paragraph(doc)

    # ── ECG Records ───────────────────────────────────────────────────────────
    section_heading(doc, "ECG Records", "section_ecg_records")
    blank_content_paragraph(doc)

    # ── Prescription Records ──────────────────────────────────────────────────
    section_heading(doc, "Prescription Records", "section_prescription_records")
    blank_content_paragraph(doc)

    # ── Correspondence ────────────────────────────────────────────────────────
    section_heading(doc, "Correspondence", "section_correspondence")
    blank_content_paragraph(doc)

    # ── Management Articles ───────────────────────────────────────────────────
    section_heading(doc, "Management Articles", "section_management_articles")
    blank_content_paragraph(doc)

    return doc


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
            name_parts = args.name.split()
            from sqlalchemy import or_
            q = db.query(Patient)
            for part in name_parts:
                q = q.filter(
                    or_(
                        Patient.first_name.ilike(f"%{part}%"),
                        Patient.last_name.ilike(f"%{part}%"),
                    )
                )
            patient = q.first()

        if not patient:
            print("Patient not found.", file=sys.stderr)
            sys.exit(1)

        print(f"Generating file for: {patient.first_name} {patient.last_name}")

        allergies  = db.query(Allergy).filter(Allergy.patient_id == patient.id).all()
        meds = db.query(Prescription).filter(
            Prescription.patient_id == patient.id,
            Prescription.is_active == True,
        ).all()

        doc = build_patient_document(patient, allergies, meds)

        dob = patient.date_of_birth.strftime("%d-%m-%Y")
        filename = f"{patient.first_name.upper()} {patient.last_name.upper()} {dob}.docx"
        doc.save(filename)
        print(f"Saved: {filename}")
        print(f"  Allergies included: {len(allergies)}")
        print(f"  Medications included: {len(meds)}")
        print(f"  Sections: Demographics, Family/Medical/Social History, Current Drugs,")
        print(f"            Drug Reactions, Contemporaneous Notes, Vaccinations,")
        print(f"            Specialist Reports, Imaging, Pathology, ECG, Rx, Correspondence")

    finally:
        db.close()


if __name__ == "__main__":
    main()
