/* Deterministic, browser-only demonstration of the root agents/workers.py rules.
   Not a validated clinical decision-support system. No network requests or storage. */
"use strict";

(function () {
  const STATUS_WORDS = /DISCORDANT|ANOMALY|MUTANT|VIOLATION|FAIL|REJECT/i;
  const IDENTIFIER_PATTERN = /\b(?:MRN)[#: -]*\d{4,10}\b|\b\d{3}-\d{2}-\d{4}\b|\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/i;

  function validate(input) {
    for (const name of ["task_id", "target_identifier"]) {
      if (typeof input[name] !== "string" || !input[name].trim() || input[name].length > 128 || /[\x00-\x1f\x7f]/.test(input[name])) {
        throw new Error(name + " must be 1–128 printable characters.");
      }
      if (IDENTIFIER_PATTERN.test(input[name])) {
        throw new Error("Use synthetic identifiers only; a recognizable personal identifier was detected.");
      }
    }
    if (typeof input.status_descriptor !== "string" || input.status_descriptor.length > 64 || /[\x00-\x1f\x7f]/.test(input.status_descriptor)) {
      throw new Error("Status descriptor must contain at most 64 printable characters.");
    }
    if (IDENTIFIER_PATTERN.test(input.status_descriptor)) {
      throw new Error("Use synthetic descriptors only.");
    }
    for (const name of ["primary_metric", "secondary_metric"]) {
      if (typeof input[name] !== "number" || !Number.isFinite(input[name]) || Math.abs(input[name]) > 1e9) {
        throw new Error(name + " must be a finite number between −1e9 and 1e9.");
      }
    }
    if (typeof input.is_critical_flag !== "boolean") {
      throw new Error("Critical flag must be a boolean.");
    }
    return input;
  }

  function evaluate(payload) {
    validate(payload);
    const alerts = [];
    function add(origin_worker, urgency, summary, technical_details, actionable_remediation) {
      alerts.push({ origin_worker, urgency, summary, technical_details, actionable_remediation });
    }
    if (payload.primary_metric > 25) {
      add("InvariantQCWorker", "ELEVATED_RISK", "Illustrative primary threshold exceeded",
        "Primary metric " + payload.primary_metric + " exceeds demonstration cutoff 25.",
        "Review the input and use a validated, context-specific protocol.");
    }
    if (payload.is_critical_flag || payload.secondary_metric > 12) {
      add("SafetyEscalationWorker", payload.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
        "Escalation flag or illustrative secondary threshold triggered",
        "Critical flag: " + payload.is_critical_flag + "; secondary metric: " + payload.secondary_metric + " (demonstration cutoff 12).",
        "Confirm the flag and follow institutional escalation procedures, if applicable.");
    }
    if (STATUS_WORDS.test(payload.status_descriptor)) {
      add("ProtocolConformanceWorker", "ELEVATED_RISK", "Descriptor review flag",
        "Descriptor contains a demonstration anomaly/discordance keyword.",
        "Review the description and supporting pathology data.");
    }
    const critical = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
    const overall = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
    return {
      mode: "LOCAL_DEMONSTRATION",
      rule_set: "Illustrative thresholds only; not validated for patient care",
      task_id: payload.task_id.trim(),
      target_identifier: payload.target_identifier.trim(),
      overall_urgency: overall,
      integrity_status: critical ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
      total_alerts: alerts.length,
      critical_alerts_count: critical,
      alerts,
      disclaimer: "Not for clinical diagnosis, margin clearance, operative decisions, or patient safety monitoring."
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { validate, evaluate };
  }

  if (typeof document !== "undefined") {
    const form = document.getElementById("auditForm");
    const output = document.getElementById("result");
    const feedback = document.getElementById("feedback");
    const counter = document.getElementById("processed");
    const exportButton = document.getElementById("export");
    let processed = 0;
    let lastResult = null;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      feedback.textContent = "";
      try {
        const input = {
          task_id: document.getElementById("task_id").value,
          target_identifier: document.getElementById("target_identifier").value,
          primary_metric: Number(document.getElementById("primary_metric").value),
          secondary_metric: Number(document.getElementById("secondary_metric").value),
          status_descriptor: document.getElementById("status_descriptor").value,
          is_critical_flag: document.getElementById("is_critical_flag").checked
        };
        for (const name of ["primary_metric", "secondary_metric"]) {
          if (document.getElementById(name).value.trim() === "") {
            throw new Error(name + " is required.");
          }
        }
        lastResult = evaluate(input);
        output.textContent = JSON.stringify(lastResult, null, 2);
        counter.textContent = String(++processed);
        exportButton.disabled = false;
        feedback.textContent = "Evaluation complete — local demonstration only.";
      } catch (error) {
        lastResult = null;
        exportButton.disabled = true;
        output.textContent = "No result. Correct the highlighted input conditions and retry.";
        feedback.textContent = error.message;
      }
    });

    exportButton.addEventListener("click", function () {
      if (!lastResult) return;
      const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "frozen-sentinel-demo.json";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    });
  }
})();
