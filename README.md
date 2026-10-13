# Frozen Section Sentinel Agent

A research-oriented prototype for auditing **synthetic** frozen-section workflow data. The repository contains an illustrative three-worker Python supervisor, a FastAPI service, a CLI/batch processor, and separate modules for frozen-to-permanent diagnosis comparison, margin-distance screening, and turnaround-time tracking.

**Safety:** No clinical validation has been demonstrated. Fixed demonstration thresholds are **not** CAP, AJCC, or ASCO/CAP clinical decision limits. The software must not guide diagnosis, margin clearance, re-excision, patient notification, or intraoperative treatment.

## Browser demonstration

Open [the browser application](web/index.html) directly, or serve the repository as static files (for example with `python -m http.server 8080` and then open `http://localhost:8080/`). The root `index.html` redirects to `web/`, making the site compatible with branch-root static hosting such as GitHub Pages **when Pages is enabled**.

The static application runs entirely in the browser with plain JavaScript and no backend, Pyodide, authentication, or third-party runtime dependency. It reproduces the **illustrative root worker branches**: primary value above 25, secondary value above 12 or explicit critical flag, and status descriptor keywords. These numbers are arbitrary demonstration cutoffs. They do not implement the margin/correlation/TAT Python modules.

Enter synthetic identifiers and numerical values, evaluate locally, and optionally export the displayed result to JSON. The interface does not transmit requests, store inputs between sessions, create HMAC signatures, or fabricate operational counters. Keep real patient or other personal information out of this prototype.

## Python CLI

Requires Python 3.9 or later. For development:

```bash
python -m pip install -e ".[server,test]"
python cli.py audit --task-id SYNTH-001 --target SYNTH-SPECIMEN --primary 28 --secondary 14 --status DISCORDANT
python cli.py batch --input sample.csv --output results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The root API exposes `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. The API expects the `SystemTaskPayload` fields `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `status_descriptor`, and `is_critical_flag`.

A **separate historical packaged interface** is retained for compatibility:

```bash
python -m frozen_section_sentinel_agent.cli audit --case-id SYNTH-001 --primary 28 --secondary 14 --status DISCORDANT
```

Its schema and thresholds differ from the root supervisor. Do not mix the two payload formats.

## Other modules

- `frozen_section_sentinel_agent/correlation.py`: text-heuristic frozen/permanent comparison. Different diagnostic descriptions with the same coarse malignancy flag are marked for review, not assumed concordant. This is **not** validated diagnostic NLP.
- `frozen_section_sentinel_agent/margin_agent.py`: exploratory distance categories and tumor-type lookup values. Its lookup table and 3 mm category boundary are **illustrative**, not procedure-specific surgical standards. Interpret all `requires_reexcision` fields as experimental flags only.
- `frozen_section_sentinel_agent/tat_monitor.py`: in-memory timers, user-specified SLA threshold (20 minutes by default), and descriptive turnaround statistics.
- `agents/base.py`: in-memory chained HMAC-SHA256 audit entries. The verification function recomputes each signature and checks chain continuity; entries are **not persisted** across restarts.

## Security and privacy

The root supervisor applies basic regular-expression screening for some directly identifying text, but this is **not comprehensive de-identification, HIPAA certification, or a guarantee of zero PHI**. Never submit real identifiers to this public demonstration or an unsecured API. The FastAPI server does not implement authentication, so bind to localhost unless independently protected.

Set `AUDIT_SECRET_KEY` to a securely generated secret when using the server; otherwise an ephemeral key is generated. The Docker Compose setup requires an explicit key:

```bash
export AUDIT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build
```

The audit ledger is per-process/in-memory; setting a persistent key does not persist the ledger. Do not expose the service publicly without appropriate transport security, authentication, access controls and institutional review.

## Testing

```bash
python -m pytest -q
node --check web/app.js
node --test tests/web_app.test.cjs
```

GitHub Actions runs Python 3.10–3.13 tests and Node 22 browser-rule tests. The browser uses standard HTML, CSS and ES2015+ JavaScript, targeting current desktop and mobile browsers. A continuous server connection is not required.

## Technology and license

Python, FastAPI, Pydantic, vanilla JavaScript, optional Docker, GitHub Actions. Licensed under [MIT](LICENSE).
