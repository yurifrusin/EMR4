(function initialiseStage3B() {
  "use strict";
  const data = window.Stage3BData;
  const core = window.Stage3BCore;
  if (!data || !core) throw new Error("Stage 3B study contracts are unavailable");

  const byId = (id) => document.getElementById(id);
  const elements = {
    consentPanel: byId("consent-panel"),
    workspace: byId("workspace"),
    participantCode: byId("participant-code"),
    practiceBucket: byId("practice-bucket"),
    arm: byId("counterbalance-arm"),
    consentChecks: [...document.querySelectorAll("[data-consent]")],
    startSession: byId("start-session"),
    consentStatus: byId("consent-status"),
    sessionLabel: byId("session-label"),
    sessionArm: byId("session-arm"),
    recordCount: byId("record-count"),
    openProduct: byId("open-product"),
    taskList: byId("task-list"),
    activeRouteChip: byId("active-route-chip"),
    taskId: byId("task-id"),
    taskRoute: byId("task-route"),
    taskTitle: byId("task-title"),
    taskGoal: byId("task-goal"),
    routeInstruction: byId("route-instruction"),
    taskSuccess: byId("task-success"),
    requestHintBlock: byId("request-hint-block"),
    requestHint: byId("request-hint"),
    startTask: byId("start-task"),
    markVisit: byId("mark-product-visit"),
    timerOutput: byId("timer-output"),
    observationForm: byId("observation-form"),
    taskOutcome: byId("task-outcome"),
    correctness: byId("correctness"),
    stateComprehension: byId("state-comprehension"),
    confidence: byId("confidence"),
    assistanceCount: byId("assistance-count"),
    safeAmbiguity: byId("safe-ambiguity"),
    proposalBoundary: byId("proposal-boundary"),
    ordinaryFallback: byId("ordinary-fallback"),
    issueFlags: byId("issue-flags"),
    observationStatus: byId("observation-status"),
    nextTask: byId("next-task"),
    scoreSummary: byId("score-summary"),
    downloadExport: byId("download-export"),
    resetSession: byId("reset-session")
  };
  const state = {
    session: null,
    activeIndex: 0,
    taskStartedAt: null,
    timerId: null,
    routeVisits: { reception_one: false, ordinary_diary: false }
  };

  function addOptions(select, values, placeholder) {
    if (placeholder) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = placeholder;
      select.append(option);
    }
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.append(option);
    });
  }

  function routeLabel(route) {
    return route === "reception_one" ? "Reception One" : "Ordinary Diary";
  }

  function routeInstruction(route) {
    return route === "reception_one"
      ? "Open Reception One. Use its request field, focused projection, touch controls and Back path. Ordinary Diary remains an allowed safety escape."
      : `Choose Ordinary Diary, set the date to ${data.referenceDateLabel}, and complete the task from the conventional Diary surface. Do not use Reception One unless you need a safety fallback.`;
  }

  function currentTask() {
    return data.tasks[state.activeIndex];
  }

  function currentRoute() {
    return core.assignedRoute(currentTask(), state.session.counterbalance_arm);
  }

  function elapsedMs() {
    return state.taskStartedAt === null ? 0 : Math.round(performance.now() - state.taskStartedAt);
  }

  function stopTimer() {
    if (state.timerId !== null) window.clearInterval(state.timerId);
    state.timerId = null;
  }

  function updateTimer() {
    if (state.taskStartedAt === null) {
      elements.timerOutput.textContent = "Not started";
      return;
    }
    elements.timerOutput.textContent = `${(elapsedMs() / 1000).toFixed(1)} seconds`;
  }

  function resetOutcomeFields(task) {
    const existing = state.session.observations.find((item) => item.task_id === task.id);
    elements.taskOutcome.value = existing?.task_outcome || "completed";
    elements.correctness.value = existing?.correctness || "correct";
    elements.stateComprehension.value = existing?.state_comprehension || "clear";
    elements.confidence.value = existing?.confidence || "high";
    elements.assistanceCount.value = String(existing?.assistance_count || 0);
    elements.safeAmbiguity.value = existing?.safe_ambiguity
      || (task.id === "S3B-06" ? "safe_clarification" : "not_applicable");
    elements.proposalBoundary.value = existing?.proposal_boundary
      || (task.id === "S3B-05" ? "understood_not_committed" : "not_applicable");
    elements.ordinaryFallback.checked = existing?.ordinary_diary_fallback === true;
    [...elements.issueFlags.querySelectorAll("input")].forEach((input) => {
      input.checked = existing?.issue_flags.includes(input.value) === true;
    });
  }

  function renderTaskList() {
    elements.taskList.replaceChildren();
    data.tasks.forEach((task, index) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      const recorded = state.session.observations.some((entry) => entry.task_id === task.id);
      button.type = "button";
      button.dataset.recorded = String(recorded);
      if (index === state.activeIndex) button.setAttribute("aria-current", "step");
      button.innerHTML = `<span class="task-number">${task.id}</span><span class="task-name">${task.title}</span><span class="task-done" aria-label="${recorded ? "Recorded" : "Not recorded"}">${recorded ? "✓" : "·"}</span>`;
      button.addEventListener("click", () => selectTask(index));
      item.append(button);
      elements.taskList.append(item);
    });
  }

  function renderTask() {
    const task = currentTask();
    const route = currentRoute();
    elements.taskId.textContent = task.id;
    elements.taskTitle.textContent = task.title;
    elements.taskGoal.textContent = task.goal;
    elements.taskSuccess.textContent = task.success;
    elements.taskRoute.textContent = routeLabel(route);
    elements.activeRouteChip.textContent = routeLabel(route);
    elements.routeInstruction.textContent = routeInstruction(route);
    elements.requestHintBlock.hidden = !task.requestHint;
    elements.requestHint.textContent = task.requestHint || "";
    elements.observationStatus.textContent = "";
    state.taskStartedAt = null;
    state.routeVisits = { reception_one: false, ordinary_diary: false };
    stopTimer();
    updateTimer();
    resetOutcomeFields(task);
    renderTaskList();
  }

  function selectTask(index) {
    if (!Number.isInteger(index) || index < 0 || index >= data.tasks.length) return;
    state.activeIndex = index;
    renderTask();
    elements.taskTitle.focus?.();
  }

  function buildIssueFlags() {
    const labels = {
      could_not_find_entry: "Could not find where to begin",
      route_not_obvious: "Assigned route was not obvious",
      scope_not_understood: "Scope was not understood",
      blank_space_mistaken_for_availability: "Blank space mistaken for availability",
      selection_mistaken_for_booking: "Selection mistaken for booking",
      proposal_mistaken_for_booking: "Proposal mistaken for booking",
      identity_assumed: "Identity assumed",
      back_path_not_found: "Back path not found",
      ordinary_diary_escape_not_found: "Ordinary Diary escape not found",
      facilitator_intervention: "Facilitator intervened",
      participant_stopped: "Participant stopped"
    };
    core.ISSUE_FLAGS.forEach((flag) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = flag;
      label.append(input, document.createTextNode(labels[flag]));
      elements.issueFlags.append(label);
    });
  }

  function scoreSummary() {
    const score = core.scoreObservations(state.session.observations);
    const thresholdValues = Object.values(score.thresholds);
    const measured = thresholdValues.filter((item) => item.status !== "not_measured").length;
    const passed = thresholdValues.filter((item) => item.status === "passed").length;
    const safety = score.safety_gate.status === "failed"
      ? `${score.safety_gate.failure_count} safety failure(s)`
      : "no recorded safety failure";
    elements.scoreSummary.textContent = `${state.session.observations.length} task record(s); ${passed}/${measured} measured thresholds currently pass; ${safety}. Automated readiness is not participant evidence.`;
  }

  function startSession() {
    try {
      state.session = core.createSession({
        participant_code: elements.participantCode.value,
        practice_bucket: elements.practiceBucket.value,
        counterbalance_arm: elements.arm.value,
        consent_voluntary: elements.consentChecks.find((item) => item.dataset.consent === "voluntary").checked,
        consent_synthetic: elements.consentChecks.find((item) => item.dataset.consent === "synthetic").checked,
        consent_no_recording: elements.consentChecks.find((item) => item.dataset.consent === "recording").checked,
        consent_no_write: elements.consentChecks.find((item) => item.dataset.consent === "write").checked
      }, data);
      elements.consentPanel.hidden = true;
      elements.workspace.hidden = false;
      elements.sessionLabel.textContent = state.session.participant_code;
      elements.sessionArm.textContent = state.session.counterbalance_arm;
      elements.consentStatus.textContent = "";
      state.activeIndex = 0;
      renderTask();
      scoreSummary();
    } catch (error) {
      elements.consentStatus.textContent = error.message;
    }
  }

  function openProduct() {
    state.routeVisits[currentRoute()] = true;
    elements.observationStatus.textContent = `${routeLabel(currentRoute())} opened in the local authored-synthetic runtime.`;
  }

  function recordObservation(event) {
    event.preventDefault();
    if (state.taskStartedAt === null) {
      elements.observationStatus.textContent = "Start the task timer before recording.";
      return;
    }
    try {
      stopTimer();
      const observation = core.normalizeObservation({
        route_visits: state.routeVisits,
        elapsed_ms: elapsedMs(),
        task_outcome: elements.taskOutcome.value,
        correctness: elements.correctness.value,
        state_comprehension: elements.stateComprehension.value,
        confidence: elements.confidence.value,
        assistance_count: Number(elements.assistanceCount.value),
        ordinary_diary_fallback: elements.ordinaryFallback.checked,
        safe_ambiguity: elements.safeAmbiguity.value,
        proposal_boundary: elements.proposalBoundary.value,
        issue_flags: [...elements.issueFlags.querySelectorAll("input:checked")].map((item) => item.value)
      }, state.session, currentTask());
      core.upsertObservation(state.session, observation);
      elements.observationStatus.textContent = `${currentTask().id} recorded without free text.`;
      elements.recordCount.textContent = `${state.session.observations.length} / ${data.tasks.length}`;
      renderTaskList();
      scoreSummary();
    } catch (error) {
      elements.observationStatus.textContent = error.message;
    }
  }

  function nextTask() {
    selectTask(Math.min(state.activeIndex + 1, data.tasks.length - 1));
  }

  function downloadExport() {
    const payload = core.buildExport(state.session);
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = `${state.session.session_id}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(href);
    elements.observationStatus.textContent = "Structured JSON downloaded. No prompt, transcript or free text was included.";
  }

  function resetSession() {
    stopTimer();
    state.session = null;
    state.activeIndex = 0;
    state.taskStartedAt = null;
    state.routeVisits = { reception_one: false, ordinary_diary: false };
    elements.workspace.hidden = true;
    elements.consentPanel.hidden = false;
    elements.consentChecks.forEach((item) => { item.checked = false; });
    elements.consentStatus.textContent = "In-memory session destroyed.";
  }

  addOptions(elements.participantCode, data.participantCodes, "Choose code");
  addOptions(elements.practiceBucket, data.practiceBuckets, "Choose bucket");
  addOptions(elements.arm, data.counterbalanceArms, "Choose arm");
  elements.openProduct.href = data.productUrl;
  buildIssueFlags();
  elements.startSession.addEventListener("click", startSession);
  elements.openProduct.addEventListener("click", openProduct);
  elements.startTask.addEventListener("click", () => {
    state.taskStartedAt = performance.now();
    stopTimer();
    state.timerId = window.setInterval(updateTimer, 100);
    updateTimer();
    elements.observationStatus.textContent = "Timer started.";
  });
  elements.markVisit.addEventListener("click", () => {
    state.routeVisits[currentRoute()] = true;
    elements.observationStatus.textContent = `${routeLabel(currentRoute())} visit marked.`;
  });
  elements.observationForm.addEventListener("submit", recordObservation);
  elements.nextTask.addEventListener("click", nextTask);
  elements.downloadExport.addEventListener("click", downloadExport);
  elements.resetSession.addEventListener("click", resetSession);
}());
