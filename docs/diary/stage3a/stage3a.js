(function initialiseStage3AStudy() {
  "use strict";

  const data = window.Stage3AData;
  const core = window.Stage3ACore;
  if (!data || !core) {
    throw new Error("Stage 3A authored fixture modules did not load");
  }

  const elements = {
    counterbalance: document.getElementById("counterbalance"),
    scenarioList: document.getElementById("scenario-list"),
    scenarioProgress: document.getElementById("scenario-progress"),
    activeTaskId: document.getElementById("active-task-id"),
    activeTaskTitle: document.getElementById("active-task-title"),
    activeTaskGoal: document.getElementById("active-task-goal"),
    routeOrder: document.getElementById("route-order"),
    routeTabs: Array.from(document.querySelectorAll(".route-tab")),
    conversationRoute: document.getElementById("conversation-route"),
    gridRoute: document.getElementById("grid-route"),
    attentionRoute: document.getElementById("attention-route"),
    conversationForm: document.getElementById("conversation-form"),
    conversationInput: document.getElementById("conversation-input"),
    promptHint: document.getElementById("prompt-hint"),
    answerRegion: document.getElementById("answer-region"),
    gridDate: document.getElementById("grid-date"),
    ordinaryGrid: document.getElementById("ordinary-grid"),
    gridDetail: document.getElementById("grid-detail"),
    attentionFixtures: document.getElementById("attention-fixtures"),
    attentionGuidance: document.getElementById("attention-guidance"),
    visibleNotices: document.getElementById("visible-notices"),
    filterResults: document.getElementById("filter-results"),
    resetAttention: document.getElementById("reset-attention"),
    projectionScope: document.getElementById("projection-scope"),
    projectionContent: document.getElementById("projection-content"),
    projectionBack: document.getElementById("projection-back"),
    projectionReset: document.getElementById("projection-reset"),
    taskOutcome: document.getElementById("task-outcome"),
    stateComprehension: document.getElementById("state-comprehension"),
    projectionRating: document.getElementById("projection-rating"),
    observationFlags: Array.from(document.querySelectorAll("#observation-flags input[type='checkbox']")),
    observationStatus: document.getElementById("observation-status"),
    recordObservation: document.getElementById("record-observation"),
    observationCount: document.getElementById("observation-count"),
    downloadObservations: document.getElementById("download-observations"),
    resetStudy: document.getElementById("reset-study")
  };

  const state = {
    sessionId: createSessionId(),
    activeScenarioIndex: -1,
    activeRoute: "conversation",
    routeOrder: [],
    routeVisits: {},
    taskStartedAt: null,
    clarificationCount: 0,
    projectionReturnCount: 0,
    currentProjection: null,
    projectionStack: [],
    observations: [],
    recordedScenarioIds: new Set(),
    attentionState: core.createAttentionState(),
    attentionDecisions: [],
    attentionFixtureIds: [],
    gridDatesVisited: new Set()
  };

  function createSessionId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return `stage3a-${window.crypto.randomUUID()}`;
    }
    return `stage3a-${Math.round(performance.timeOrigin)}-${Math.round(performance.now())}`;
  }

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = text;
    return element;
  }

  function formatDate(isoDate) {
    const date = new Date(`${isoDate}T00:00:00+10:00`);
    return new Intl.DateTimeFormat("en-AU", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
      timeZone: data.practice.timezone
    }).format(date);
  }

  function formatTime(value) {
    const [hourText, minute] = value.split(":");
    const hour = Number(hourText);
    const suffix = hour >= 12 ? "pm" : "am";
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minute} ${suffix}`;
  }

  function scenario() {
    return state.activeScenarioIndex >= 0 ? data.scenarios[state.activeScenarioIndex] : null;
  }

  function renderScenarioList() {
    elements.scenarioList.replaceChildren();
    data.scenarios.forEach((item, index) => {
      const listItem = node("li");
      const button = node("button", "scenario-button");
      button.type = "button";
      button.dataset.scenarioId = item.id;
      button.setAttribute("aria-label", `Start ${item.id}: ${item.title}`);
      if (index === state.activeScenarioIndex) button.classList.add("is-active");
      if (state.recordedScenarioIds.has(item.id)) button.classList.add("is-recorded");
      button.append(
        node("span", "scenario-code", item.id.replace("S3A-", "")),
        node("span", "scenario-name", item.title),
        node("span", "scenario-status", state.recordedScenarioIds.has(item.id) ? "✓" : "·")
      );
      button.addEventListener("click", () => startScenario(index));
      listItem.append(button);
      elements.scenarioList.append(listItem);
    });
    elements.scenarioProgress.textContent = `${state.recordedScenarioIds.size} / ${data.scenarios.length}`;
  }

  function startScenario(index) {
    state.activeScenarioIndex = index;
    const active = scenario();
    state.routeOrder = core.routeOrderFor(active, index, elements.counterbalance.value);
    state.routeVisits = {};
    state.clarificationCount = 0;
    state.projectionReturnCount = 0;
    state.attentionDecisions = [];
    state.attentionFixtureIds = [];
    state.gridDatesVisited = new Set();
    elements.taskOutcome.value = "not_recorded";
    elements.stateComprehension.value = "not_recorded";
    elements.projectionRating.value = "not_recorded";
    elements.observationFlags.forEach((flag) => { flag.checked = false; });
    elements.observationStatus.textContent = "";

    elements.activeTaskId.textContent = active.id;
    elements.activeTaskTitle.textContent = active.title;
    elements.activeTaskGoal.textContent = active.goal;
    elements.routeOrder.textContent = `Order: ${state.routeOrder.join(" → ")}`;
    elements.promptHint.textContent = `Suggested authored request: “${active.hint}”`;
    elements.conversationInput.placeholder = active.hint;
    elements.conversationInput.value = "";
    elements.answerRegion.replaceChildren(emptyState("No answer yet", "Type the suggested request or your own equivalent wording."));
    resetProjection();
    resetAttention();
    configureRouteTabs(active);
    if (active.gridDate) elements.gridDate.value = active.gridDate;
    renderGrid();
    renderAttentionGuidance(active);
    switchRoute(state.routeOrder[0]);
    state.taskStartedAt = performance.now();
    renderScenarioList();
  }

  function configureRouteTabs(active) {
    elements.routeTabs.forEach((tab) => {
      const allowed = active ? active.routes.includes(tab.dataset.route) : tab.dataset.route === "conversation";
      tab.disabled = !allowed;
      tab.setAttribute("aria-disabled", String(!allowed));
    });
  }

  function renderAttentionGuidance(active) {
    if (!active || !Array.isArray(active.attentionSteps)) {
      elements.attentionGuidance.textContent = "This scenario does not use event fixtures.";
      return;
    }
    const labels = active.attentionSteps.map((fixtureId) => {
      const event = data.events.find((item) => item.fixture_id === fixtureId);
      return event ? event.label : fixtureId;
    });
    elements.attentionGuidance.textContent = `Required order: ${labels.join(" → ")}. Buttons unlock one step at a time.`;
  }

  function emptyState(title, detail) {
    const container = node("div", "empty-state");
    container.append(node("strong", "", title), node("span", "", detail));
    return container;
  }

  function switchRoute(route) {
    const active = scenario();
    const allowed = active ? active.routes.includes(route) : route === "conversation";
    if (!allowed) return;
    state.activeRoute = route;
    state.routeVisits[route] = (state.routeVisits[route] || 0) + 1;
    elements.routeTabs.forEach((tab) => {
      const selected = tab.dataset.route === route;
      tab.classList.toggle("is-active", selected);
      tab.setAttribute("aria-selected", String(selected));
    });
    elements.conversationRoute.classList.toggle("hidden", route !== "conversation");
    elements.gridRoute.classList.toggle("hidden", route !== "grid");
    elements.attentionRoute.classList.toggle("hidden", route !== "attention");
    if (route === "conversation") elements.conversationInput.focus();
    if (route === "grid") {
      state.gridDatesVisited.add(elements.gridDate.value);
      renderGrid();
    }
  }

  function renderAnswer(result) {
    const card = node("article", `answer-card is-${result.kind}`);
    const stateLabel = {
      answer: "Answer · authored synthetic read",
      clarification: "Clarification required",
      proposal: "Proposal · not written",
      blocked: "Blocked safely · no write",
      boundary: "Separate authoritative check"
    }[result.kind] || result.kind;
    card.append(node("span", "state-label", stateLabel), node("p", "", result.message));

    if (Array.isArray(result.candidates)) {
      const list = node("ul", "candidate-list");
      result.candidates.forEach((candidate) => list.append(node("li", "candidate-item", candidate)));
      card.append(list);
    }
    elements.answerRegion.replaceChildren(card);

    if (result.kind === "clarification") state.clarificationCount += 1;
    if (result.projection) renderProjection(result.projection, true);
  }

  function projectionItem(item) {
    const card = node("li", "projection-item");
    if (item.patient) {
      card.append(
        node("strong", "", `${item.patient} · ${formatTime(item.startsAt)}–${formatTime(item.endsAt)}`),
        node("span", "", `${formatDate(item.date)} · ${item.practitioner}`),
        node("span", "", `${item.location} · ${item.status.toLowerCase()}`)
      );
      return card;
    }
    if (item.date && item.startsAt) {
      card.append(
        node("strong", "", `${formatTime(item.startsAt)}–${formatTime(item.endsAt)}`),
        node("span", "", `${formatDate(item.date)} · available synthetic slot`)
      );
      return card;
    }
    if (item.summary) {
      card.append(node("strong", "", item.summary), node("span", "", `As of ${item.asOf}`));
      return card;
    }
    card.append(node("span", "", "Synthetic projection item"));
    return card;
  }

  function renderProjection(projection, pushCurrent) {
    if (pushCurrent && state.currentProjection) state.projectionStack.push(state.currentProjection);
    state.currentProjection = projection;
    elements.projectionScope.textContent = `Scope: ${projection.scope}`;
    const content = node("div");
    const meta = node("p", "projection-meta", `Projection ${projection.id} · authored synthetic fixture · reversible`);
    const list = node("ul", "projection-list");
    (projection.items || []).forEach((item) => list.append(projectionItem(item)));
    content.append(meta, list);
    elements.projectionContent.replaceChildren(content);
    elements.projectionBack.disabled = state.projectionStack.length === 0;
  }

  function resetProjection() {
    state.currentProjection = null;
    state.projectionStack = [];
    elements.projectionScope.textContent = "Scope: synthetic practice overview";
    elements.projectionContent.replaceChildren(emptyState(
      "Overview retained",
      "A supported request or relevant event can refigure this area without changing Diary truth."
    ));
    elements.projectionBack.disabled = true;
  }

  function returnProjection() {
    if (!state.projectionStack.length) return;
    const prior = state.projectionStack.pop();
    state.projectionReturnCount += 1;
    renderProjection(prior, false);
    elements.projectionBack.disabled = state.projectionStack.length === 0;
  }

  function initialiseGridDates() {
    const dates = [...new Set(data.appointments.map((item) => item.date))].sort();
    dates.forEach((date) => {
      const option = node("option", "", formatDate(date));
      option.value = date;
      elements.gridDate.append(option);
    });
    elements.gridDate.value = "2026-07-31";
    renderGrid();
  }

  function renderGrid() {
    const selectedDate = elements.gridDate.value;
    const dayAppointments = data.appointments.filter((item) => item.date === selectedDate);
    const dayAvailability = data.availability.filter((item) => item.date === selectedDate);
    const times = [...new Set([
      ...dayAppointments.map((item) => item.startsAt),
      ...dayAvailability.map((item) => item.startsAt)
    ])].sort();
    const rows = times.length ? times : ["09:00", "10:00", "11:00", "14:00", "15:00"];
    elements.ordinaryGrid.replaceChildren();
    elements.ordinaryGrid.append(node("div", "grid-cell grid-header", "Time"));
    data.practitioners.forEach((practitioner) => {
      elements.ordinaryGrid.append(node("div", "grid-cell grid-header", practitioner.column));
    });

    rows.forEach((time) => {
      elements.ordinaryGrid.append(node("div", "grid-cell grid-time", formatTime(time)));
      data.practitioners.forEach((practitioner) => {
        const cell = node("div", "grid-cell");
        const appointment = dayAppointments.find((item) => item.startsAt === time && item.practitionerId === practitioner.id);
        if (appointment) {
          const patient = data.patients.find((item) => item.id === appointment.patientId);
          const button = node("button", "grid-appointment", `${patient.displayName} · ${formatTime(appointment.startsAt)}`);
          button.type = "button";
          button.addEventListener("click", () => showGridDetail(appointment));
          cell.append(button);
        } else {
          const available = dayAvailability.find((item) => item.startsAt === time && item.practitionerId === practitioner.id);
          if (available) {
            cell.append(node("span", "grid-availability", `Available · ${formatTime(available.startsAt)}–${formatTime(available.endsAt)}`));
          }
        }
        elements.ordinaryGrid.append(cell);
      });
    });
    const dateInstruction = scenario()?.id === "S3A-11"
      ? " Use the date selector to inspect each authored upcoming date."
      : "";
    elements.gridDetail.textContent = `Showing the authored synthetic grid for ${formatDate(selectedDate)}.${dateInstruction}`;
  }

  function showGridDetail(appointment) {
    const patient = data.patients.find((item) => item.id === appointment.patientId);
    const practitioner = data.practitioners.find((item) => item.id === appointment.practitionerId);
    elements.gridDetail.textContent = `${patient.displayName} · ${formatTime(appointment.startsAt)}–${formatTime(appointment.endsAt)} · ${practitioner.displayName} · ${appointment.status.toLowerCase()}.`;
  }

  function renderAttentionFixtures() {
    elements.attentionFixtures.replaceChildren();
    const active = scenario();
    const steps = active && Array.isArray(active.attentionSteps) ? active.attentionSteps : [];
    const nextFixtureId = steps[state.attentionFixtureIds.length] || null;
    data.events.forEach((event, index) => {
      const button = node("button", "fixture-button");
      button.type = "button";
      const completed = state.attentionFixtureIds.includes(event.fixture_id);
      button.disabled = event.fixture_id !== nextFixtureId;
      button.classList.toggle("is-completed", completed);
      button.setAttribute("aria-describedby", "attention-guidance");
      button.append(node("span", "", event.label), node("small", "", `${event.event_type} · fixture ${index + 1}`));
      button.addEventListener("click", () => runAttentionFixture(event));
      elements.attentionFixtures.append(button);
    });
  }

  function runAttentionFixture(event) {
    const decision = core.evaluateAttentionEvent(
      event,
      state.attentionState,
      { practiceId: data.practice.id },
      data
    );
    state.attentionDecisions.push({
      fixture_id: event.fixture_id,
      event_id: decision.eventId,
      event_type: decision.eventType,
      attention: decision.attention,
      visible: decision.visible,
      reason_code: decision.reasonCode
    });
    state.attentionFixtureIds.push(event.fixture_id);

    const filterCard = node("article", "filter-card");
    filterCard.append(
      node("strong", "", decision.visible ? "Surfaced once" : "Suppressed"),
      node("span", "", `${decision.reasonCode} · attention=${decision.attention} · fixture evidence`)
    );
    elements.filterResults.querySelector(".empty-copy")?.remove();
    elements.filterResults.prepend(filterCard);

    if (decision.visible) {
      const notice = node("article", "notice-card");
      notice.append(
        node("span", "state-label", "Concise notice · committed fixture"),
        node("strong", "", decision.message),
        node("span", "", "Why: related to the retained synthetic patient task and confirmed by a fresh scoped synthetic read.")
      );
      const showButton = node("button", "secondary-button", "Show current context");
      showButton.type = "button";
      showButton.addEventListener("click", () => renderProjection(decision.projection, true));
      notice.append(showButton);
      elements.visibleNotices.querySelector(".empty-copy")?.remove();
      elements.visibleNotices.prepend(notice);
    }
    renderAttentionFixtures();
  }

  function resetAttention() {
    state.attentionState = core.createAttentionState();
    state.attentionDecisions = [];
    state.attentionFixtureIds = [];
    elements.visibleNotices.replaceChildren(node("p", "empty-copy", "No notice has been surfaced."));
    elements.filterResults.replaceChildren(node("p", "empty-copy", "Run a fixture to inspect its deterministic decision."));
    renderAttentionFixtures();
  }

  function observationBlockReason(active) {
    const missingRoutes = active.routes.filter((route) => !state.routeVisits[route]);
    if (missingRoutes.length) {
      return `Visit the remaining required route${missingRoutes.length === 1 ? "" : "s"}: ${missingRoutes.join(", ")}.`;
    }

    if (Array.isArray(active.attentionSteps)) {
      const completed = state.attentionFixtureIds.join("|");
      const required = active.attentionSteps.join("|");
      if (completed !== required) {
        return "Complete the displayed event-fixture sequence before recording.";
      }
    }

    if (["S3A-12", "S3A-14"].includes(active.id) && state.currentProjection?.type !== "event_context") {
      return "Click Show current context before recording this event-attention scenario.";
    }

    if (active.id === "S3A-13" && state.attentionDecisions.some((decision) => decision.visible)) {
      return "S3A-13 cannot be recorded because a suppression fixture created a visible notice.";
    }

    if (active.id === "S3A-11") {
      const requiredDates = [...new Set(
        data.appointments
          .filter((item) => item.patientId === "patient-margaret-thompson")
          .map((item) => item.date)
      )];
      const missingDates = requiredDates.filter((date) => !state.gridDatesVisited.has(date));
      if (missingDates.length) {
        return "Use the grid date selector to inspect every authored Margaret Thompson appointment date before recording.";
      }
    }

    return null;
  }

  function recordObservation() {
    const active = scenario();
    if (!active) {
      elements.activeTaskGoal.textContent = "Choose a scenario before recording an outcome.";
      return;
    }
    const blockReason = observationBlockReason(active);
    if (blockReason) {
      elements.observationStatus.textContent = blockReason;
      return;
    }
    const elapsedMs = state.taskStartedAt === null ? null : Math.round(performance.now() - state.taskStartedAt);
    const observation = {
      schema_version: "bernie.stage3a.structured-observation.v2",
      study_session_id: state.sessionId,
      recorded_at: new Date().toISOString(),
      scenario_id: active.id,
      counterbalance: elements.counterbalance.value,
      route_order: state.routeOrder.slice(),
      route_visits: { ...state.routeVisits },
      elapsed_ms: elapsedMs,
      task_outcome: elements.taskOutcome.value,
      state_comprehension: elements.stateComprehension.value,
      projection_usefulness: elements.projectionRating.value,
      clarification_count: state.clarificationCount,
      return_to_context_count: state.projectionReturnCount,
      projection_id: state.currentProjection ? state.currentProjection.id : null,
      grid_dates_visited: [...state.gridDatesVisited].sort(),
      event_decisions: state.attentionDecisions.slice(),
      observation_flags: elements.observationFlags
        .filter((flag) => flag.checked)
        .map((flag) => flag.value)
    };
    const existingIndex = state.observations.findIndex((item) => item.scenario_id === active.id);
    if (existingIndex >= 0) {
      state.observations[existingIndex] = observation;
    } else {
      state.observations.push(observation);
    }
    state.recordedScenarioIds.add(active.id);
    elements.observationStatus.textContent = existingIndex >= 0
      ? `${active.id} structured outcome updated.`
      : `${active.id} structured outcome recorded.`;
    updateObservationReadback();
    renderScenarioList();
  }

  function updateObservationReadback() {
    const count = state.observations.length;
    elements.observationCount.textContent = `${count} ${count === 1 ? "record" : "records"}`;
  }

  function downloadObservations() {
    const payload = {
      schema_version: "bernie.stage3a.study-export.v2",
      evidence_mode: "authored_synthetic_fixture_browser",
      participant_scope: "yuri_only",
      reference_date: data.referenceDate,
      contains_prompt_or_transcript_text: false,
      observations: state.observations
    };
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: "application/json" });
    const href = URL.createObjectURL(blob);
    const link = node("a");
    link.href = href;
    link.download = `bernie-stage3a-${state.sessionId}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(href);
  }

  function clearStudy() {
    state.sessionId = createSessionId();
    state.activeScenarioIndex = -1;
    state.routeOrder = [];
    state.routeVisits = {};
    state.taskStartedAt = null;
    state.clarificationCount = 0;
    state.projectionReturnCount = 0;
    state.observations = [];
    state.recordedScenarioIds = new Set();
    state.attentionDecisions = [];
    state.attentionFixtureIds = [];
    state.gridDatesVisited = new Set();
    elements.activeTaskId.textContent = "Choose a scenario";
    elements.activeTaskTitle.textContent = "The active task will appear here";
    elements.activeTaskGoal.textContent = "Select any scenario from the left. The study records structured outcomes, never your typed words.";
    elements.routeOrder.textContent = "No route assigned";
    elements.promptHint.textContent = "Start a scenario to see its suggested synthetic request.";
    elements.conversationInput.value = "";
    elements.observationFlags.forEach((flag) => { flag.checked = false; });
    elements.observationStatus.textContent = "";
    elements.answerRegion.replaceChildren(emptyState("No answer yet", "Bernie will label an answer, clarification, proposal, or block explicitly."));
    resetProjection();
    resetAttention();
    updateObservationReadback();
    renderScenarioList();
    configureRouteTabs(null);
    renderAttentionGuidance(null);
    switchRoute("conversation");
  }

  elements.routeTabs.forEach((tab) => tab.addEventListener("click", () => switchRoute(tab.dataset.route)));
  elements.conversationForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const active = scenario();
    if (!active) {
      renderAnswer({ kind: "clarification", message: "Choose a Stage 3A scenario first." });
      return;
    }
    const typedRequest = elements.conversationInput.value;
    const result = core.interpretTask(active.id, typedRequest, data);
    elements.conversationInput.value = "";
    renderAnswer(result);
  });
  elements.counterbalance.addEventListener("change", () => {
    if (state.activeScenarioIndex >= 0) startScenario(state.activeScenarioIndex);
  });
  elements.gridDate.addEventListener("change", () => {
    if (state.activeRoute === "grid") state.gridDatesVisited.add(elements.gridDate.value);
    renderGrid();
  });
  elements.resetAttention.addEventListener("click", () => {
    resetAttention();
    if (state.currentProjection?.type === "event_context") resetProjection();
  });
  elements.projectionBack.addEventListener("click", returnProjection);
  elements.projectionReset.addEventListener("click", resetProjection);
  elements.recordObservation.addEventListener("click", recordObservation);
  elements.downloadObservations.addEventListener("click", downloadObservations);
  elements.resetStudy.addEventListener("click", clearStudy);

  renderScenarioList();
  initialiseGridDates();
  configureRouteTabs(null);
  renderAttentionGuidance(null);
  renderAttentionFixtures();
  updateObservationReadback();
}());
