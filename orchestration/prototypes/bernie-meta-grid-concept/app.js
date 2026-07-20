(function () {
  "use strict";

  const fixtureBundle = window.META_GRID_FIXTURES;
  const projections = fixtureBundle.projections;
  const eventFixtures = fixtureBundle.event_fixtures;

  const elements = {
    requestForm: document.getElementById("request-form"),
    requestInput: document.getElementById("request-input"),
    backButton: document.getElementById("back-button"),
    overviewButton: document.getElementById("overview-button"),
    explainButton: document.getElementById("explain-button"),
    scopeSummary: document.getElementById("scope-summary"),
    scopeOmissions: document.getElementById("scope-omissions"),
    freshnessSummary: document.getElementById("freshness-summary"),
    stateHeader: document.querySelector(".state-header"),
    stateLabel: document.getElementById("state-label"),
    stateHeading: document.getElementById("state-heading"),
    stateExplanation: document.getElementById("state-explanation"),
    stateAnnouncer: document.getElementById("state-announcer"),
    projectionCanvas: document.getElementById("projection-canvas"),
    projectionContent: document.getElementById("projection-content"),
    projectionActions: document.getElementById("projection-actions"),
    evidencePanel: document.getElementById("evidence-panel"),
    evidenceFamily: document.getElementById("evidence-family"),
    evidenceTrigger: document.getElementById("evidence-trigger"),
    evidenceReason: document.getElementById("evidence-reason"),
    evidenceChanges: document.getElementById("evidence-changes"),
    evidenceMode: document.getElementById("evidence-mode"),
    evidenceBoundary: document.getElementById("evidence-boundary"),
    rootHistory: document.getElementById("root-history"),
    attentionLog: document.getElementById("attention-log")
  };

  const state = {
    current: null,
    trail: [],
    recentRoots: [],
    selectedItemId: null,
    deliveredEventIds: new Set(),
    maximumRevisionByAggregate: new Map(),
    attentionEntries: []
  };

  const stateCopy = {
    answer: {
      label: "Answer",
      heading: "Current Diary facts projected for this request",
      explanation: "This is a read-only view over authored synthetic current state."
    },
    overview: {
      label: "Overview",
      heading: "Ordinary Diary overview retained as a fallback",
      explanation: "The grid remains available when spatial context is the useful view."
    },
    clarification_required: {
      label: "Clarification needed",
      heading: "Choose the intended identity before any Diary view appears",
      explanation: "No person has been silently selected and no sensitive projection is displayed."
    },
    selection_only: {
      label: "Selection only — nothing booked",
      heading: "A slot is selected as staff input",
      explanation: "Selection is reversible presentation state. It has not reserved, proposed or created an appointment."
    },
    proposal_not_committed: {
      label: "Proposal — not committed",
      heading: "Review the exact intended appointment",
      explanation: "A real confirmation would use the existing backend command with fresh checks, idempotency, audit and receipt."
    },
    committed_change_notice: {
      label: "Committed-change notice",
      heading: "The current Diary view confirms a relevant change",
      explanation: "The event fixture signalled a change; the displayed appointment comes from a fresh synthetic read."
    },
    blocked: {
      label: "Blocked safely",
      heading: "This request cannot be projected safely",
      explanation: "Change the scope or clarify the request before continuing."
    }
  };

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function rootLabel(projection) {
    return projection.scope_summary;
  }

  function rememberCurrentRoot() {
    if (!state.current) {
      return;
    }
    const root = state.trail.length ? state.trail[0] : state.current;
    const entry = {
      projection: clone(root),
      label: rootLabel(root)
    };
    state.recentRoots = state.recentRoots.filter(
      (candidate) => candidate.projection.root_intent_id !== root.root_intent_id
    );
    state.recentRoots.unshift(entry);
    state.recentRoots = state.recentRoots.slice(0, 4);
  }

  function clearTransientState() {
    state.trail = [];
    state.selectedItemId = null;
    state.deliveredEventIds = new Set();
    state.maximumRevisionByAggregate = new Map();
    state.attentionEntries = [];
  }

  function startRoot(projectionKey, options) {
    const settings = options || {};
    rememberCurrentRoot();
    clearTransientState();
    state.current = clone(projections[projectionKey]);
    if (settings.transitionReason) {
      state.current.transition.reason = settings.transitionReason;
    }
    if (settings.eventFixture) {
      const event = settings.eventFixture;
      state.deliveredEventIds.add(event.event_id);
      state.maximumRevisionByAggregate.set("synthetic-appointment-margaret", event.aggregate_revision);
      state.attentionEntries.push(
        "Surfaced once — relevant committed fixture; fresh scoped read completed; attention=concise."
      );
    }
    render();
  }

  function restoreRecentRoot(index) {
    const entry = state.recentRoots[index];
    if (!entry) {
      return;
    }
    rememberCurrentRoot();
    clearTransientState();
    state.current = clone(entry.projection);
    state.current.projection_revision += 1;
    state.current.transition = {
      operation: "project",
      trigger: "history",
      reason: "User explicitly restored a previous root view; a future runtime would refresh its authorised read",
      changed_dimensions: ["root_intent", "projection_revision"]
    };
    render();
  }

  function pushChild(projection) {
    state.trail.push(clone(state.current));
    state.current = clone(projection);
    render();
  }

  function goBack() {
    if (!state.trail.length) {
      return;
    }
    state.current = state.trail.pop();
    state.selectedItemId = null;
    render();
    elements.projectionCanvas.focus();
  }

  function itemTime(item) {
    if (!item.starts_at) {
      return Number.MAX_SAFE_INTEGER;
    }
    return Date.parse(item.starts_at);
  }

  function sortedItems(items) {
    return [...items].sort((left, right) => {
      const difference = itemTime(left) - itemTime(right);
      return difference || left.item_id.localeCompare(right.item_id);
    });
  }

  function itemMeta(item) {
    return [item.practitioner_display, item.location_display, item.status]
      .filter(Boolean)
      .join(" · ");
  }

  function localTime24(instant, timeZone) {
    return new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
      timeZone
    }).format(new Date(instant));
  }

  function makeItemNode(item, className) {
    const article = document.createElement("article");
    article.className = className || "projection-item";
    if (item.changed) {
      article.classList.add("changed-item");
    }
    const heading = document.createElement("h3");
    heading.textContent = item.display;
    const meta = document.createElement("p");
    meta.className = "item-meta";
    meta.textContent = itemMeta(item);
    article.append(heading, meta);
    if (item.warnings && item.warnings.length) {
      const warning = document.createElement("p");
      warning.className = "item-warning";
      warning.textContent = item.warnings.join(" · ");
      article.append(warning);
    }
    return article;
  }

  function renderSimpleList(items, listClass, itemClass) {
    const list = document.createElement("ol");
    list.className = listClass;
    sortedItems(items).forEach((item) => {
      const li = document.createElement("li");
      li.append(makeItemNode(item, itemClass));
      list.append(li);
    });
    return list;
  }

  function renderSlots(projection) {
    const list = document.createElement("ol");
    list.className = "slot-list";
    sortedItems(projection.items).forEach((item) => {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "slot-button";
      button.dataset.itemId = item.item_id;
      button.setAttribute("aria-pressed", String(state.selectedItemId === item.item_id));
      const label = document.createElement("strong");
      label.textContent = item.display;
      const meta = document.createElement("span");
      meta.textContent = itemMeta(item);
      button.append(label, meta);
      button.addEventListener("click", (event) => {
        selectItem(item.item_id, event.detail === 0 ? "keyboard" : "touch");
      });
      li.append(button);
      if (item.warnings.length) {
        const warning = document.createElement("p");
        warning.className = "item-warning";
        warning.textContent = item.warnings.join(" · ");
        li.append(warning);
      }
      list.append(li);
    });
    return list;
  }

  function renderComparison(projection) {
    const wrapper = document.createElement("div");
    wrapper.className = "comparison-grid";
    const basis = document.createElement("p");
    basis.className = "comparison-basis";
    basis.textContent = "Shared basis: Tuesday 21 July · 8 am–12 pm · Brisbane Clinic · 30 minutes.";
    wrapper.append(basis);
    const groups = new Map();
    sortedItems(projection.items).forEach((item) => {
      const key = item.comparison_group || "Other";
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key).push(item);
    });
    groups.forEach((items, label) => {
      const lane = document.createElement("section");
      lane.className = "comparison-lane";
      const heading = document.createElement("h3");
      heading.textContent = label;
      lane.append(heading, renderSlots({...projection, items}));
      wrapper.append(lane);
    });
    return wrapper;
  }

  function renderClarification() {
    const wrapper = document.createElement("div");
    wrapper.className = "clarification-options";
    const prompt = document.createElement("p");
    prompt.textContent = "Did you mean the practitioner or the patient? Only minimum synthetic candidate information is shown.";
    const practitioner = document.createElement("button");
    practitioner.type = "button";
    practitioner.textContent = "Dr Alex Shera — practitioner";
    practitioner.addEventListener("click", () => startRoot("sheraFocus", {
      transitionReason: "Staff clarified that the practitioner was intended"
    }));
    const patient = document.createElement("button");
    patient.type = "button";
    patient.textContent = "Alex Carter — patient";
    patient.addEventListener("click", () => {
      const blocked = clone(projections.clarification);
      blocked.projection_id = "projection-alex-patient-not-authored";
      blocked.projection_revision += 1;
      blocked.state = "blocked";
      blocked.scope_summary = "Alex Carter · no authored appointment projection in this concept lab";
      blocked.omissions = ["No patient Diary facts displayed"];
      blocked.transition = {
        operation: "clarify",
        trigger: "touch",
        reason: "Identity was clarified, but no authorised authored projection exists",
        changed_dimensions: ["identity_resolution", "state"]
      };
      pushChild(blocked);
    });
    wrapper.append(prompt, practitioner, patient);
    return wrapper;
  }

  function renderProposal(projection) {
    const wrapper = document.createElement("div");
    wrapper.className = "proposal-review";
    const item = projection.items[0];
    const summary = document.createElement("strong");
    summary.textContent = item.display;
    const stateLine = document.createElement("p");
    stateLine.textContent = "Nothing has been booked. Backend revalidation and explicit staff confirmation are still required.";
    const confirm = document.createElement("button");
    confirm.type = "button";
    confirm.disabled = true;
    confirm.textContent = "Confirm in authoritative Diary — unavailable in concept lab";
    wrapper.append(summary, stateLine, confirm);
    return wrapper;
  }

  function renderCanvas(projection) {
    elements.projectionContent.replaceChildren();
    let content;
    switch (projection.family) {
      case "patient_timeline":
        content = renderSimpleList(projection.items, "timeline", "timeline-item");
        break;
      case "availability_slots":
        content = renderSlots(projection);
        break;
      case "aligned_comparison":
        content = renderComparison(projection);
        break;
      case "clarification":
        content = renderClarification();
        break;
      case "proposal_review":
        content = renderProposal(projection);
        break;
      case "ordinary_overview":
        content = renderSimpleList(projection.items, "overview-list", "overview-item");
        break;
      default:
        content = renderSimpleList(projection.items, "projection-list", "projection-item");
        break;
    }
    elements.projectionContent.append(content);
  }

  function makeAction(label, handler, variant) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    if (variant) {
      button.className = variant;
    }
    button.addEventListener("click", handler);
    return button;
  }

  function refineCurrent() {
    const refined = clone(state.current);
    state.trail.push(clone(state.current));
    refined.projection_id += "-refined";
    refined.projection_revision += 1;
    refined.parent_projection_id = state.current.projection_id;
    refined.transition = {
      operation: "refine",
      trigger: "touch",
      reason: "User narrowed the current view",
      changed_dimensions: []
    };
    if (refined.family === "focused_schedule_lane") {
      refined.scope.time_from = "14:00";
      refined.scope_summary = "Dr Shera · Friday 31 July 2026 · 2 pm–5 pm · Brisbane Clinic";
      refined.omissions = ["Other practitioners hidden", "Times before 2 pm hidden"];
      refined.items = refined.items.filter((item) => item.starts_at >= "2026-07-31T04:00:00Z");
      refined.transition.changed_dimensions = ["time_from"];
    } else if (refined.family === "patient_timeline") {
      refined.scope.practitioner_ids = ["synthetic-practitioner-shera"];
      refined.scope_summary = "Margaret Thompson · upcoming with Dr Shera · Brisbane Clinic · next 12 months";
      refined.omissions = ["Appointments with other practitioners hidden", "Cancelled and past appointments hidden"];
      refined.items = refined.items.filter((item) => item.practitioner_display.includes("Shera"));
      refined.transition.changed_dimensions = ["practitioner"];
    } else {
      refined.scope.result_limit = Math.min(refined.scope.result_limit, 5);
      refined.transition.changed_dimensions = ["result_limit"];
    }
    state.current = refined;
    render();
  }

  function selectItem(itemId, trigger) {
    const item = state.current.items.find((candidate) => candidate.item_id === itemId);
    if (!item || !item.selectable) {
      return;
    }
    const selected = clone(state.current);
    state.trail.push(clone(state.current));
    state.selectedItemId = itemId;
    selected.projection_id = `${selected.projection_id}-selection-${itemId}`;
    selected.projection_revision += 1;
    selected.parent_projection_id = state.current.projection_id;
    selected.state = "selection_only";
    selected.scope.date_from = item.date;
    selected.scope.date_to = item.date;
    selected.scope.time_from = localTime24(item.starts_at, selected.scope.timezone);
    selected.scope.time_to = localTime24(item.ends_at, selected.scope.timezone);
    selected.scope_summary = `Selected ${item.display} · ${item.practitioner_display} · ${item.location_display}`;
    selected.omissions = ["Selection has not reserved or created an appointment"];
    selected.transition = {
      operation: "select",
      trigger,
      reason: "Staff selected one authored synthetic candidate slot",
      changed_dimensions: ["selected_item", "state"]
    };
    selected.action_boundary.posture = "selection_only";
    state.current = selected;
    render();
  }

  function prepareProposal() {
    if (!state.selectedItemId) {
      return;
    }
    const proposal = clone(projections.proposal);
    proposal.parent_projection_id = state.current.projection_id;
    proposal.root_intent_id = state.current.root_intent_id;
    pushChild(proposal);
  }

  function renderActions(projection) {
    elements.projectionActions.replaceChildren();
    if (projection.state === "selection_only") {
      elements.projectionActions.append(
        makeAction("Use Margaret Thompson and review proposal", prepareProposal, "primary"),
        makeAction("Clear selection", goBack)
      );
      return;
    }
    if (["focused_schedule_lane", "patient_timeline"].includes(projection.family)) {
      elements.projectionActions.append(makeAction("Refine this view", refineCurrent));
    }
    if (projection.family === "patient_timeline" && state.trail.length) {
      elements.projectionActions.append(makeAction("Broaden to previous scope", goBack));
    }
    if (projection.family === "availability_slots") {
      const note = document.createElement("p");
      note.textContent = "Select a slot by touch or keyboard. Selection cannot book it.";
      elements.projectionActions.append(note);
    }
  }

  function renderEvidence(projection) {
    elements.evidenceFamily.textContent = projection.family;
    elements.evidenceTrigger.textContent = projection.transition.trigger;
    elements.evidenceReason.textContent = projection.transition.reason;
    elements.evidenceChanges.textContent = projection.transition.changed_dimensions.join(", ") || "none";
    elements.evidenceMode.textContent = projection.evidence_mode;
    elements.evidenceBoundary.textContent = `${projection.action_boundary.posture}; appointment_write_authority=false`;
  }

  function renderRootHistory() {
    elements.rootHistory.replaceChildren();
    if (!state.recentRoots.length) {
      const li = document.createElement("li");
      li.textContent = "No previous root view in this in-memory session.";
      elements.rootHistory.append(li);
      return;
    }
    state.recentRoots.forEach((entry, index) => {
      const li = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = entry.label;
      button.addEventListener("click", () => restoreRecentRoot(index));
      li.append(button);
      elements.rootHistory.append(li);
    });
  }

  function renderAttentionLog() {
    elements.attentionLog.replaceChildren();
    const entries = state.attentionEntries.length
      ? state.attentionEntries
      : ["No event fixture has been exercised in this root view."];
    entries.forEach((entry) => {
      const li = document.createElement("li");
      li.textContent = entry;
      elements.attentionLog.append(li);
    });
  }

  function render() {
    const projection = state.current;
    const copy = stateCopy[projection.state] || stateCopy.blocked;
    elements.scopeSummary.textContent = projection.scope_summary;
    elements.scopeOmissions.textContent = `Not shown: ${projection.omissions.join(" · ")}`;
    elements.freshnessSummary.textContent = `As of ${projection.freshness.observed_at} · ${projection.freshness.reason}`;
    elements.stateHeader.dataset.state = projection.state;
    elements.stateLabel.textContent = copy.label;
    elements.stateHeading.textContent = copy.heading;
    elements.stateExplanation.textContent = copy.explanation;
    elements.stateAnnouncer.textContent = `${copy.label}. ${projection.scope_summary}`;
    elements.backButton.disabled = state.trail.length === 0;
    renderCanvas(projection);
    renderActions(projection);
    renderEvidence(projection);
    renderRootHistory();
    renderAttentionLog();
  }

  function matchRequest(rawRequest) {
    const request = rawRequest.trim().toLowerCase();
    if ((request.includes("upcoming") || request.includes("future")) && request.includes("margaret")) {
      return "margaretTimeline";
    }
    if (request.includes("compare") && request.includes("shera") && request.includes("patel")) {
      return "comparison";
    }
    if ((request.includes("available") || request.includes("availability")) && request.includes("shera")) {
      return "availability";
    }
    if (request.includes("alex") && !request.includes("dr alex")) {
      return "clarification";
    }
    if (request.includes("shera") && (request.includes("afternoon") || request.includes("friday"))) {
      return "sheraFocus";
    }
    return null;
  }

  function handleRequest(event) {
    event.preventDefault();
    const projectionKey = matchRequest(elements.requestInput.value);
    if (projectionKey) {
      startRoot(projectionKey);
      elements.projectionCanvas.focus();
      return;
    }
    const blocked = clone(projections.clarification);
    blocked.projection_id = "projection-unsupported-request";
    blocked.root_intent_id = `intent-unsupported-${Date.now()}`;
    blocked.state = "blocked";
    blocked.scope_summary = "Request outside the authored concept grammar";
    blocked.omissions = ["No Diary data displayed", "No external model called"];
    blocked.transition.reason = "The local deterministic concept matcher did not recognise this request";
    rememberCurrentRoot();
    clearTransientState();
    state.current = blocked;
    render();
  }

  function runEventFixture(index) {
    const fixture = eventFixtures[index];
    if (!fixture) {
      return;
    }
    const aggregateKey = fixture.event_type.includes("appointment")
      ? "synthetic-appointment-margaret"
      : fixture.event_type;
    const maximumRevision = state.maximumRevisionByAggregate.get(aggregateKey) || 0;
    if (fixture.classification === "unrelated") {
      state.attentionEntries.push("Suppressed — unrelated committed roster fixture; attention=silent.");
    } else if (state.deliveredEventIds.has(fixture.event_id)) {
      state.attentionEntries.push("Suppressed — duplicate event identity; no second visible effect.");
    } else if (fixture.aggregate_revision < maximumRevision || fixture.classification === "stale_revision") {
      state.attentionEntries.push("Suppressed — older aggregate revision cannot replace current projection state.");
    } else if (fixture.classification === "relevant_committed") {
      startRoot("changeContext", {eventFixture: fixture});
      return;
    } else {
      state.attentionEntries.push("Suppressed — fixture did not satisfy the deterministic attention contract.");
    }
    state.maximumRevisionByAggregate.set(
      aggregateKey,
      Math.max(maximumRevision, fixture.aggregate_revision)
    );
    renderAttentionLog();
  }

  elements.requestForm.addEventListener("submit", handleRequest);
  elements.backButton.addEventListener("click", goBack);
  elements.overviewButton.addEventListener("click", () => startRoot("overview"));
  elements.explainButton.addEventListener("click", () => {
    const willShow = elements.evidencePanel.hidden;
    elements.evidencePanel.hidden = !willShow;
    elements.explainButton.setAttribute("aria-expanded", String(willShow));
    if (willShow) {
      elements.evidencePanel.querySelector("h2").focus?.();
    }
  });

  document.querySelectorAll("[data-projection]").forEach((button) => {
    button.addEventListener("click", () => startRoot(button.dataset.projection));
  });

  document.querySelectorAll("[data-event-index]").forEach((button) => {
    button.addEventListener("click", () => runEventFixture(Number(button.dataset.eventIndex)));
  });

  startRoot("overview");
})();
