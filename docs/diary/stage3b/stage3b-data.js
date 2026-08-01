(function exposeStage3BData(root, factory) {
  const data = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = data;
  } else {
    root.Stage3BData = data;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function buildStage3BData() {
  "use strict";

  const productUrl = "http://127.0.0.1:3000/meta-grid-auth.html";
  const referenceDate = "2026-07-27";
  const referenceDateLabel = "Monday 27 July 2026";
  const tasks = [
    {
      id: "S3B-01",
      title: "Understand the current state",
      goal: "Open Reception One and decide whether the visible state is committed Diary truth, a selected time, or an unwritten proposal.",
      routeByArm: { A: "reception_one", B: "reception_one" },
      success: "The participant distinguishes committed Diary truth from selection and proposal states.",
      measures: ["state_comprehension", "correctness"]
    },
    {
      id: "S3B-02",
      title: "Patient appointment recall",
      goal: "Find every upcoming appointment for the synthetic patient Margaret Thompson.",
      requestHint: "Show Margaret Thompson's upcoming appointments.",
      routeByArm: { A: "reception_one", B: "ordinary_diary" },
      success: "The participant finds the authored-synthetic appointments and can return to the previous context.",
      measures: ["completion", "correctness", "reversibility", "elapsed_ms"]
    },
    {
      id: "S3B-03",
      title: "Practitioner afternoon",
      goal: "Inspect Dr Shera's bounded afternoon on Monday 27 July 2026.",
      requestHint: "Show Dr Shera today after 12 pm.",
      routeByArm: { A: "ordinary_diary", B: "reception_one" },
      success: "The participant identifies the bounded practitioner view without mistaking blank space for availability.",
      measures: ["completion", "correctness", "reversibility", "elapsed_ms"]
    },
    {
      id: "S3B-04",
      title: "Combined availability",
      goal: "Find a 30-minute option for Margaret Thompson with Dr Shera after 2 pm on Monday 27 July 2026.",
      requestHint: "Show the available slots with Dr Shera for a half-hour appointment with Margaret Thompson after 2 today.",
      routeByArm: { A: "reception_one", B: "ordinary_diary" },
      success: "The participant finds a current candidate without claiming that it is held or booked.",
      measures: ["completion", "correctness", "state_comprehension", "elapsed_ms"]
    },
    {
      id: "S3B-05",
      title: "Proposal boundary",
      goal: "Select a current time, prepare the proposal-review state, and explain what has and has not happened.",
      requestHint: "Use the selected time for Margaret Thompson.",
      routeByArm: { A: "reception_one", B: "reception_one" },
      success: "The participant says the proposal is not a booking and no appointment has been written.",
      measures: ["completion", "proposal_boundary", "state_comprehension"]
    },
    {
      id: "S3B-06",
      title: "Identity ambiguity",
      goal: "Ask for Alex's afternoon without a surname. Do not choose between the two authored-synthetic practitioners unless the interface supplies enough evidence.",
      requestHint: "Show Alex's afternoon today.",
      routeByArm: { A: "reception_one", B: "reception_one" },
      success: "The interface and participant stop for clarification between Alex Shera and Alex Chen rather than assuming identity.",
      measures: ["safe_ambiguity", "correctness"]
    },
    {
      id: "S3B-07",
      title: "Recover context and leave safely",
      goal: "From a focused projection, return to the previous context and then to the ordinary Diary.",
      routeByArm: { A: "reception_one", B: "reception_one" },
      success: "Back is reversible, and Ordinary Diary exits without creating or repeating an action.",
      measures: ["completion", "reversibility", "state_comprehension"]
    },
    {
      id: "S3B-08",
      title: "Afternoon appointment recall",
      goal: "Find the synthetic patient Billy Fursin's afternoon appointment on Monday 27 July 2026.",
      requestHint: "Show Billy Fursin's appointments today.",
      routeByArm: { A: "ordinary_diary", B: "reception_one" },
      success: "The participant identifies the 2:30 pm authored-synthetic appointment.",
      measures: ["completion", "correctness", "elapsed_ms"]
    }
  ];

  return Object.freeze({
    schema_version: "reception_one.stage3b.study_definition.v1",
    evidence_mode: "authored_synthetic",
    productUrl,
    referenceDate,
    referenceDateLabel,
    participantCodes: Object.freeze(["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08"]),
    practiceBuckets: Object.freeze(["practice-a", "practice-b"]),
    counterbalanceArms: Object.freeze(["A", "B"]),
    tasks: Object.freeze(tasks.map((task) => Object.freeze(task)))
  });
}));
