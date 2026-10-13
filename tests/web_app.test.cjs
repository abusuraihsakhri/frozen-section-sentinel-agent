"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { validate, evaluate } = require("../web/app.js");

const normal = {
  task_id: "TASK-001", target_identifier: "SYNTH-001",
  primary_metric: 10, secondary_metric: 5, status_descriptor: "NOMINAL",
  is_critical_flag: false
};

test("routine demo returns no alerts", () => {
  const result = evaluate(normal);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.equal(result.mode, "LOCAL_DEMONSTRATION");
  assert.equal(result.audit_hash, undefined);
});

test("all three illustrative workers trigger when expected", () => {
  const result = evaluate({ ...normal, primary_metric: 30, secondary_metric: 20,
    status_descriptor: "DISCORDANT", is_critical_flag: true });
  assert.equal(result.total_alerts, 3);
  assert.equal(result.critical_alerts_count, 1);
  assert.equal(result.overall_urgency, "CRITICAL_STAT_PANIC");
});

test("threshold boundaries are exclusive", () => {
  const result = evaluate({ ...normal, primary_metric: 25, secondary_metric: 12 });
  assert.equal(result.total_alerts, 0);
});

test("numeric errors and synthetic ID guard are enforced", () => {
  assert.throws(() => validate({ ...normal, primary_metric: Number.NaN }));
  assert.throws(() => validate({ ...normal, task_id: "MRN-994827" }));
  assert.throws(() => validate({ ...normal, target_identifier: "" }));
  assert.throws(() => validate({ ...normal, is_critical_flag: "false" }));
});
