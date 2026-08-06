# Program Risk & Vendor Coordination Intelligence

**Status:** Milestone 1 — Repo setup & requirements ✅

An AI tool that ingests status updates from multiple teams and vendors, classifies risk with a stated reason, flags patterns across teams that a single update wouldn't reveal, and auto-drafts the kind of status report I used to write by hand every Friday.

## The problem

Every Friday, I collect status updates from ~10 teams (a mix of internal teams and external vendors), covering 1-5 active issues each, and turn them into a leadership status report. Each update looks roughly like this:

| Field | Example |
|---|---|
| Initiative | CCPA Regulatory Website Updates – October |
| Jira Ticket | `HND-146` |
| Due Date | 10/31 |
| Update | Legal has finalized copy and distributed it to Team A, B, C. Teams will begin updating websites and communications to reflect the new language. |
| Self-reported risk | Medium |
| Rationale | Need to keep track of each site and validate the language has been implemented as required. |

Two things make this hard to do well by hand, every week, at scale:

1. **Self-reported risk is unreliable in isolation.** A team can honestly rate its own risk "Low" while it is quietly blocking someone else's "High." A due date "tomorrow" with an unresolved dependency reads very differently than the same words with three weeks of runway — but the dropdown doesn't capture that.
2. **The real risk often lives *between* updates, not inside one.** Two teams independently naming the same vendor as a blocker, or three separate emergencies all landing on the same team in the same week, is invisible if you only ever read updates one at a time.
3. **Emergencies constantly reorder priorities.** Urgent, unplanned work routinely supersedes what was previously "on track," and that reprioritization needs to surface immediately, not get buried until next Friday.

This tool is built to catch what I caught by manually cross-referencing 30-50 updates a week — earlier, and more consistently.

## What "at risk" means here

Risk classification here is not just the team's self-reported Low/Medium/High. Each update is classified into one of three states, with a **reason code** drawn from four signal types — the same signals I actually watch for when reading these updates:

### Classification states

| State | Meaning |
|---|---|
| **On Track** | No credible threat to the due date. Any risk mentioned is proactively managed with a clear plan and doesn't require escalation. |
| **At Risk** | One or more signals below are present and could threaten the due date without intervention, but the workstream is still moving. |
| **Blocked** | Progress has actually stopped — waiting on a person, team, vendor, or decision outside the reporting team's control, with no forward movement possible until it's resolved. |

### Signal types (the "why")

These are the patterns that, in my experience, precede a missed date or an escalation — regardless of what the self-reported dropdown says:

1. **Quiet / Unresponsive** — A workstream goes quiet: no update submitted, or an update that just repeats last week's status verbatim with no new information. Silence is a signal, not a null value.
2. **Bottlenecked / Not Prioritized** — Work is stalled behind a dependency, review, or decision that isn't moving — often visible as "waiting on X" appearing two weeks in a row.
3. **Competing Objectives** — An urgent, unplanned item (an emergency, an executive ask, a production incident) has superseded the reported work, pulling people or priority away from it.
4. **Unowned Escalation** — A real risk has been raised (sometimes even self-rated High) but no leader or decision-maker has picked it up or moved on it — the risk is named but nobody owns unblocking it.

A single update can carry more than one signal. Self-reported risk is kept as an input feature, not the answer — the model is expected to sometimes *disagree* with it (e.g., a team rates itself "Medium" the same week its due date is tomorrow and it's still blocked on another team).

## Design principle: cross-source over single-source

Because the real risk is often only visible across updates, the mock dataset (below) is deliberately built with **connected threads** — the same vendor named as a blocker by two different teams, the same due-date chain spanning four tickets, the same team hit by two unrelated emergencies in one week — so that later milestones (cross-source pattern detection) have real signal to find, not just isolated rows.

## Mock dataset

[`data/mock_status_updates.json`](./data/mock_status_updates.json) — 17 status updates, one Friday reporting cycle (2025-10-24), across 10 teams (6 internal, 4 external vendors), modeled on the real format and scenario above.

Each entry includes:
- The fields a team actually submits: `team`, `jira_ticket`, `initiative`, `category`, `due_date`, `report_date`, `update_text`, `self_reported_risk`, `self_reported_rationale`.
- `ground_truth_classification` and `ground_truth_signal` — **author-labeled for evaluation only** (Milestone 5). These are not passed to the classifier; they're the answer key used to measure whether the AI's classification matches what I'd have flagged manually.

Coverage by signal type (each appears at least twice, several updates carry more than one):

- **Quiet / Unresponsive** — `HND-146c` (vendor unresponsive 9+ days), `HND-311` (no update submitted)
- **Bottlenecked / Not Prioritized** — `HND-310` (repeated vendor reschedule), `HND-88`/`HND-89` (dependency chain, due date imminent)
- **Competing Objectives** — `HND-150`-adjacent `HND-146b` (release freeze), `HND-520` (vendor emergency), `HND-611` (partner outage pulls engineers), `HND-95` (CMO fast-track request)
- **Unowned Escalation** — `HND-700` (risk raised to two leaders, no response)

Also included: the CCPA initiative as a 4-ticket chain (`HND-146`, `HND-146b`, `HND-146c`, `HND-201`) spanning three teams plus Legal, and a case (`HND-89`) where the blocking team self-rates its own risk "Low" while blocking another team's "Medium"-rated, due-tomorrow ticket — the exact self-report-vs-reality gap this tool exists to catch.

## Repo structure

```
01-program-risk-intelligence/
├── README.md              # this file
└── data/
    └── mock_status_updates.json
```

(Milestone 2 will add the classification script and its own README section.)

## Roadmap

- [x] Milestone 1 — Repo setup & requirements
- [ ] Milestone 2 — Risk classification build (Claude API)
- [ ] Milestone 3 — Cross-source pattern detection
- [ ] Milestone 4 — Two-altitude reporting (team-level + executive)
- [ ] Milestone 5 — Evaluation, polish & demo
