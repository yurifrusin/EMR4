(function initialiseYuriWalkthrough() {
  "use strict";

  const data = window.Stage3BData;
  const core = window.YuriWalkthroughCore;
  if (!data || !core) throw new Error("Yuri walkthrough contracts are unavailable");

  const byId = (id) => document.getElementById(id);
  const elements = {
    dialog: byId("acknowledgement-dialog"),
    acknowledgementForm: byId("acknowledgement-form"),
    acknowledgementCheck: byId("acknowledgement-check"),
    begin: byId("begin-walkthrough"),
    shell: byId("walkthrough-main"),
    taskList: byId("task-list"),
    progressCount: byId("progress-count"),
    progressFill: byId("progress-fill"),
    taskId: byId("task-id"),
    taskTitle: byId("task-title"),
    taskGoal: byId("task-goal"),
    taskAction: byId("task-action"),
    taskSuccess: byId("task-success"),
    hintBlock: byId("request-hint-block"),
    requestHint: byId("request-hint"),
    taskSaved: byId("task-saved"),
    taskForm: byId("task-review-form"),
    taskResult: byId("task-result"),
    taskOrientation: byId("task-orientation"),
    relativeValue: byId("relative-value"),
    ordinaryFallback: byId("ordinary-fallback"),
    issueFlags: byId("issue-flags"),
    taskNote: byId("task-note"),
    taskNoteCount: byId("task-note-count"),
    saveTask: byId("save-task"),
    previousTask: byId("previous-task"),
    taskStatus: byId("task-status"),
    finalForm: byId("final-review-form"),
    overallValue: byId("overall-value"),
    designPartnerReadiness: byId("design-partner-readiness"),
    foregroundWindow: byId("foreground-projection-window"),
    dateTurn: byId("date-first-page-turn"),
    bureauWorkflow: byId("bureau-workflow"),
    textBeforeVoice: byId("text-before-push-to-talk"),
    overallNote: byId("overall-note"),
    overallNoteCount: byId("overall-note-count"),
    finalStatus: byId("final-status"),
    reviewSummary: byId("review-summary"),
    download: byId("download-review"),
    discard: byId("discard-review"),
    downloadStatus: byId("download-status")
  };

  const state = {
    review: null,
    activeIndex: 0
  };

  const issueLabels = {
    entry_not_obvious: "I could not see where to begin",
    wording_too_technical: "Wording felt technical or legalistic",
    scope_unclear: "The patient, practitioner or time scope was unclear",
    diary_context_lost: "I lost my relationship to the ordinary Diary",
    date_orientation_unclear: "The date or time context was unclear",
    projection_less_helpful_than_grid: "The projection was less helpful than the grid",
    selection_or_proposal_unclear: "Selection, proposal or booking state was unclear",
    back_path_unclear: "The route back was unclear",
    visual_density: "The display felt too dense or busy",
    ordinary_diary_fallback_needed: "I needed the ordinary Diary to finish",
    task_not_supported: "The current interface did not support this naturally"
  };

  function taskIds() {
    return data.tasks.map((task) => task.id);
  }

  function currentTask() {
    return data.tasks[state.activeIndex];
  }

  function taskInstruction(task) {
    if (task.id === "S3B-01") {
      return "Open Reception One and inspect the first screen before issuing a request.";
    }
    if (task.id === "S3B-07") {
      return "Use Back from a focused projection, then close Reception One to reveal the ordinary Diary.";
    }
    return task.requestHint || "Complete the task in Reception One using the visible controls.";
  }

  function internalSuccessDescription(task) {
    const replacements = [
      ["The participant distinguishes", "You can distinguish"],
      ["The participant finds", "You can find"],
      ["The participant identifies", "You can identify"],
      ["The participant says", "You can tell that"],
      [
        "The interface and participant stop for clarification between Alex Shera and Alex Chen rather than assuming identity.",
        "The interface stops for clarification between Alex Shera and Alex Chen rather than assuming identity."
      ]
    ];
    return replacements.reduce(
      (text, [from, to]) => text.replace(from, to),
      task.success
    );
  }

  function existingTaskReview() {
    return state.review?.task_reviews.find((item) => item.task_id === currentTask().id);
  }

  function renderTaskList() {
    elements.taskList.replaceChildren();
    data.tasks.forEach((task, index) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      const recorded = state.review?.task_reviews.some((entry) => entry.task_id === task.id) === true;
      const number = document.createElement("span");
      const name = document.createElement("span");
      const done = document.createElement("span");
      button.type = "button";
      button.dataset.recorded = String(recorded);
      if (index === state.activeIndex) button.setAttribute("aria-current", "step");
      number.className = "task-number";
      number.textContent = String(index + 1).padStart(2, "0");
      name.className = "task-name";
      name.textContent = task.title;
      done.className = "task-done";
      done.textContent = recorded ? "✓" : "·";
      done.setAttribute("aria-label", recorded ? "Saved" : "Not saved");
      button.append(number, name, done);
      button.addEventListener("click", () => selectTask(index));
      item.append(button);
      elements.taskList.append(item);
    });
  }

  function updateProgress() {
    const recorded = state.review?.task_reviews.length || 0;
    elements.progressCount.textContent = `${recorded} / ${data.tasks.length}`;
    elements.progressFill.style.width = `${(recorded / data.tasks.length) * 100}%`;
    const summary = state.review
      ? core.summarize(state.review, data.tasks.length)
      : null;
    elements.reviewSummary.textContent = summary
      ? `${summary.tasks_recorded} of ${summary.tasks_available} task observations saved. No usability threshold is calculated.`
      : "No task observations recorded yet.";
  }

  function resetTaskFields() {
    const existing = existingTaskReview();
    elements.taskResult.value = existing?.result || "worked";
    elements.taskOrientation.value = existing?.orientation || "clear";
    elements.relativeValue.value = existing?.relative_value || "not_compared";
    elements.ordinaryFallback.checked = existing?.ordinary_diary_fallback_used === true;
    elements.taskNote.value = existing?.product_note || "";
    elements.taskNoteCount.textContent = String(elements.taskNote.value.length);
    [...elements.issueFlags.querySelectorAll("input")].forEach((input) => {
      input.checked = existing?.issue_flags.includes(input.value) === true;
    });
    elements.taskSaved.hidden = !existing;
    elements.taskStatus.textContent = "";
  }

  function renderTask() {
    const task = currentTask();
    elements.taskId.textContent = task.id;
    elements.taskTitle.textContent = task.title;
    elements.taskGoal.textContent = task.goal;
    elements.taskAction.textContent = taskInstruction(task);
    elements.taskSuccess.textContent = internalSuccessDescription(task);
    elements.hintBlock.hidden = !task.requestHint;
    elements.requestHint.textContent = task.requestHint || "";
    elements.previousTask.disabled = state.activeIndex === 0;
    elements.saveTask.textContent = state.activeIndex === data.tasks.length - 1
      ? "Save task"
      : "Save and continue";
    resetTaskFields();
    renderTaskList();
  }

  function selectTask(index) {
    if (!Number.isInteger(index) || index < 0 || index >= data.tasks.length) return;
    state.activeIndex = index;
    renderTask();
    elements.taskTitle.focus();
  }

  function buildIssueFlags() {
    core.ISSUE_FLAGS.forEach((flag) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      const text = document.createElement("span");
      input.type = "checkbox";
      input.value = flag;
      text.textContent = issueLabels[flag];
      label.append(input, text);
      elements.issueFlags.append(label);
    });
  }

  function beginWalkthrough(event) {
    event.preventDefault();
    try {
      state.review = core.createReview(elements.acknowledgementCheck.checked);
      elements.shell.classList.remove("is-locked");
      if (typeof elements.dialog.close === "function") elements.dialog.close();
      else elements.dialog.removeAttribute("open");
      renderTask();
      updateProgress();
      elements.taskTitle.focus();
    } catch (error) {
      elements.begin.disabled = true;
    }
  }

  function saveTaskReview(event) {
    event.preventDefault();
    try {
      const taskReview = core.normalizeTaskReview({
        task_id: currentTask().id,
        result: elements.taskResult.value,
        orientation: elements.taskOrientation.value,
        relative_value: elements.relativeValue.value,
        ordinary_diary_fallback_used: elements.ordinaryFallback.checked,
        issue_flags: [...elements.issueFlags.querySelectorAll("input:checked")].map(
          (input) => input.value
        ),
        product_note: elements.taskNote.value
      }, taskIds());
      core.upsertTaskReview(state.review, taskReview);
      elements.taskSaved.hidden = false;
      elements.taskStatus.textContent = `${currentTask().id} saved in this tab.`;
      renderTaskList();
      updateProgress();
      if (state.activeIndex < data.tasks.length - 1) {
        window.setTimeout(() => selectTask(state.activeIndex + 1), 160);
      } else {
        elements.finalForm.scrollIntoView({ behavior: "smooth", block: "start" });
        elements.overallValue.focus();
      }
    } catch (error) {
      elements.taskStatus.textContent = error.message;
    }
  }

  function saveFinalReview(event) {
    event.preventDefault();
    try {
      state.review.final_review = core.normalizeFinalReview({
        overall_value: elements.overallValue.value,
        design_partner_readiness: elements.designPartnerReadiness.value,
        foreground_projection_window: elements.foregroundWindow.value,
        date_first_page_turn: elements.dateTurn.value,
        bureau_workflow: elements.bureauWorkflow.value,
        text_before_push_to_talk: elements.textBeforeVoice.value,
        product_note: elements.overallNote.value
      });
      elements.finalStatus.textContent = "Overall review saved in this tab.";
      updateProgress();
    } catch (error) {
      elements.finalStatus.textContent = error.message;
    }
  }

  function downloadReview() {
    if (!state.review) return;
    const payload = core.buildExport(state.review, data.tasks.length);
    const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], {
      type: "application/json"
    });
    const href = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = href;
    link.download = `${state.review.review_id}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(href);
    elements.downloadStatus.textContent = "Review JSON downloaded. Send that file back to Codex when you are ready.";
  }

  function showAcknowledgement() {
    if (typeof elements.dialog.showModal === "function") {
      elements.dialog.showModal();
    } else {
      elements.dialog.setAttribute("open", "");
    }
  }

  buildIssueFlags();
  showAcknowledgement();
  elements.acknowledgementCheck.addEventListener("change", () => {
    elements.begin.disabled = !elements.acknowledgementCheck.checked;
  });
  elements.acknowledgementForm.addEventListener("submit", beginWalkthrough);
  elements.taskForm.addEventListener("submit", saveTaskReview);
  elements.previousTask.addEventListener("click", () => selectTask(state.activeIndex - 1));
  elements.taskNote.addEventListener("input", () => {
    elements.taskNoteCount.textContent = String(elements.taskNote.value.length);
  });
  elements.finalForm.addEventListener("submit", saveFinalReview);
  elements.overallNote.addEventListener("input", () => {
    elements.overallNoteCount.textContent = String(elements.overallNote.value.length);
  });
  elements.download.addEventListener("click", downloadReview);
  elements.discard.addEventListener("click", () => window.location.reload());
}());
