# EMR4 Centaur — Clinical Philosophy and Design Ethos

## The Problem This System Was Born From

Dr Alex Shera ran a busy general practice. His previous practice management software stored clinical information in databases and displayed it in forms, tabs, and dropdown menus. The hypothesis behind that design was that structured data is easier to search, report on, and audit. Dr Shera found it clinically dangerous.

His observation was precise: **a busy GP will not click two extra tabs to retrieve information that could change a diagnosis or prevent a drug interaction.** The friction of a click is not trivial when you are listening to a patient, maintaining eye contact, taking a history, and forming a differential — all simultaneously. Information that is one click away is, in clinical practice, information that is frequently missed.

He chose Microsoft Word instead. Not because he was a technologist, but because he was a clinician who had thought carefully about the nature of cognition during a consultation.

---

## Dr Shera's Principle: The Full Alphabet

Dr Shera often said that to describe an illness you needed all 26 letters of the English alphabet — and more. What he meant was that clinical medicine is irreducibly narrative. The nuance of a patient's history, the way they describe their symptoms, the context of their social circumstances, the trajectory of a chronic disease across years — none of this compresses cleanly into form fields or coded values without losing something clinically important.

Word processing software, with its continuous, scrollable, free-form text, preserved that narrative. A doctor could write exactly what they observed, in the order it seemed important, using their own clinical vocabulary.

This is the reason EMR4 retains the Word document as its primary clinical canvas.

---

## The Document Architecture

The Billy Frusin patient file (the reference template from the old system) reveals a deliberate information hierarchy:

```
[Patient Demographics]           ← always visible at top
Care Plans, Health Assessments, Recalls
Family History
Medical History
Social History                   ← cultural background, private insurance
Current Drugs
Drug Reactions                   ← CRITICAL: adverse drug reactions
Contemporaneous Notes            ← THE GP WRITES HERE
Vaccinations
Specialist Reports
Diagnostic Imaging
Pathology Results
ECG Records
Prescription Records
Correspondence
Management Articles
```

The intent of this ordering was that by the time a doctor's eye reached the Contemporaneous Notes section — the blank space where they would begin typing — they had already scanned:

- What drugs the patient is on
- What substances they react to
- The medical, family, and social context

This happened passively, through the natural act of opening and scrolling the document, without requiring any deliberate navigation. The GP absorbed clinical context as a side-effect of finding the right place to write.

### The Problem That Developed

As Medicare billing incentives pushed GPs to initiate more Care Plans and Health Assessments, these billings — which required detailed documentation — grew longer and were entered at the top of the file. Over time, the Contemporaneous Notes section was pushed further down the document, off the initial screen view. The GP had to scroll past several pages of care plan documentation before reaching the section where they actually wrote clinical notes.

Dr Shera disliked this acutely. He was also, privately, concerned that the prominence of care plan documentation reflected a billing culture he was uncomfortable with — where the administrative overhead of billing-related paperwork was crowding out the clinical narrative.

### The F2 Macro

When opening a patient file, the GP would press F2. A Word macro would fire, inserting a dated consultation header at the cursor position in Contemporaneous Notes:

```
16-11-2021 Billy Frusin  12 PM 6 years old.
```

This was the GP's cue to begin writing. The date, patient name, time, and age were automatic — the doctor's mental energy was reserved for listening and thinking, not for administrative typing.

---

## How EMR4 Centaur Evolves This Philosophy

EMR4 does not abandon Dr Shera's philosophy. It extends it.

### 1. The Document Remains Central

The Word document is still the primary clinical record. The GP writes in it. The text is the truth. The database is a structured reflection of what the text contains, not the other way around.

### 2. The Taskpane is a Peripheral Awareness Layer

The EMR4 taskpane (Command Center) does not replace the document. It runs alongside it as a persistent awareness layer, always showing:

- **Drug Reactions / Allergies** — prominently, with danger highlighting for life-threatening reactions
- **Current Medications** — immediately visible without opening any tab
- **AI-suggested diagnoses** — live, updated as the GP writes, showing SNOMED-coded differentials

This directly addresses Dr Shera's concern about information being "a click away." In EMR4, the patient's allergies and current drugs are *always visible* in the sidebar, even while the GP is typing in the document. The GP does not need to remember to check.

### 3. The F2 Equivalent — Consult Header Injection

The taskpane provides a keyboard shortcut (Ctrl+Alt+N) that functions identically to the old F2 macro: it finds the Contemporaneous Notes section of the open patient document and inserts a dated header:

```
14-06-2026  Margaret Thompson  10:30 AM  73 years old.
```

The GP then types immediately below it.

### 4. AI as Scribe, Not Replacement

The audio scribe function records the consultation and transcribes it using Gemini, then extracts MBS item numbers, SNOMED diagnoses, and prescription items. This is offered as a suggestion, not an instruction. The GP reviews, corrects, and approves. The AI reduces administrative burden; the GP retains clinical authority.

Pop-up alerts for adverse drug reactions — generated by the AI when a new prescription is being considered — complement rather than replace the manual Drug Reactions section in the document. The human-readable narrative in the document remains.

### 5. The Living Diary (Phase 2)

The appointment-linked Living Diary document (hosted on SharePoint) extends the narrative approach to appointment management. When a GP opens a patient's appointment, they open a document — not a form. They see the context, write notes, and the system handles the structured data extraction.

---

## Design Principles for All Developers

1. **Information should be passively visible, not actively retrieved.** If something is clinically important, it should be on screen when the document opens, not behind a tab.

2. **The narrative is the record.** Structured data (MBS codes, SNOMED terms, prescription rows) is extracted from the narrative, not entered instead of it.

3. **The GP's attention is the scarcest resource.** Every extra click, scroll, or cognitive switch is a risk. Design for the doctor who is looking at the patient, not the screen.

4. **The document opens at the right place.** When a patient file opens, the cursor and scroll position should be at Contemporaneous Notes, with the most recent entry visible. The GP should be able to begin writing within seconds of opening the file.

5. **Billing administration must not crowd clinical narrative.** Care Plans, Health Assessments, and other billing documents belong in a separate section or document, not interleaved with clinical notes.

6. **Word Online, not desktop Word, is the primary target.** This allows free-floating Command Center windows on second monitors (via `displayDialogAsync`), microphone access without iframe permission restrictions, and native SharePoint co-authoring for the Living Diary.

---

## The Name: Centaur

The name reflects the intended relationship between AI and clinician. A centaur is neither horse nor human — it is a hybrid that combines the physical power of one with the cognition of the other. In clinical AI, the term has been used to describe the human-AI collaboration that outperforms either alone.

EMR4 Centaur is not AI replacing a doctor. It is a doctor, augmented.

---

*This document should be read by every developer, designer, or AI agent working on this system. The technical decisions follow from the clinical philosophy described here.*
