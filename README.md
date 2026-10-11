# ModelGate

[![CI](https://github.com/your-username/modelgate/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/modelgate/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Multi-LLM A/B routing & HITL escalation engine.**

Deterministic traffic splitting across competing models, statistical decisions
on when to ship, and a human-in-the-loop review queue for the ambiguous cases.
The payoff: a calibration loop that measures **how many human labels an LLM
judge needs before it agrees with humans**.

> **The finding:** *N labels → X% agreement.* *(filled in at Phase 7)*

---

## What it does

🔹 **Multi-LLM A/B routing.** Hash-based assignment routes traffic to competing
models reproducibly. Every outcome — response, latency, cost — is stored for
fair statistical comparison.

🔹 **Statistical decision + HITL escalation.** A two-proportion z-test decides
`PROMOTE` / `REJECT` / `CONTINUE` / `ESCALATE`. Ambiguous experiments become
review items; humans label them `A` / `B` / `Tie` / `Unsure` in a Streamlit
queue.

🔹 **Judge calibration loop.** An LLM judge grades the same items humans
labeled. Agreement (rate + Cohen's kappa) is plotted against label count.
The result is the headline number.

---

## Why this matters

Teams increasingly replace expensive human review with LLM judges. Almost none
measure *how much human supervision the judge itself needs* before it can be
trusted. ModelGate answers that empirically and produces a number you can act
on:

- **10 labels → 90% agreement**: ship the judge, humans become optional.
- **200 labels → 75% agreement**: the judge is a suggestion engine, humans still decide.
- **The curve never rises**: the judge is measuring something different from what humans care about.

All three outcomes are useful. None are faked.

---

## Status

Active development. Phase-by-phase build with "done when" checklists.

- ✅ Phase 0 — Skeleton & contracts
- ⬜ Phase 1 — Deterministic experiment runner
- ⬜ Phase 2 — FastAPI surface
- ⬜ Phase 3 — Decision engine (stats + significance)
- ⬜ Phase 4 — HITL review queue + Streamlit UI
- ⬜ Phase 5 — LLM judge + calibration loop
- ⬜ Phase 6 — CI quality gate
- ⬜ Phase 7 — The finding

---

## Stack

- **FastAPI** — HTTP surface
- **Pydantic v2** — domain models
- **SQLite** — persistence (stdlib `sqlite3`)
- **Streamlit** — HITL review UI and calibration dashboard
- **OpenAI-compatible SDK** — provider adapter for variants and judge
- **pytest**, **ruff** — tests and lint

---

## Architecture

*Coming in Phase 0, Step 0.6 — a real image, not Mermaid.*

---

## Quickstart

*Coming in Phase 2, Step 2.6.*

---

## The finding

*Coming in Phase 7, Step 7.2 — this section will contain the calibration curve
image and the headline number.*

---

## Testing

*Coming in Phase 2, Step 2.5.*

---

## License

MIT