# Program Risk & Vendor Coordination Intelligence

**Status:** Milestone 4 — Two-altitude reporting ✅

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

## Classification build

[`classify.py`](./classify.py) calls the Claude API (`claude-sonnet-5`) to classify a single status update. Design decisions:

- **Rubric lives in the system prompt**, word-for-word matching the classification states and signal types defined above — the model isn't inventing its own risk taxonomy.
- **Structured output via forced tool use.** Rather than asking for JSON in free text and parsing it, the call uses `tool_choice` to force a `classify_status_update` tool call with an enum-constrained schema (`classification`, `signal`, `reason`). This makes output reliably parseable — no regex/JSON-repair needed.
- **Ground truth is stripped before the call.** Any `ground_truth_*` field is filtered out of the payload sent to the model — those exist purely for evaluation and would leak the answer.
- **The model is explicitly told not to defer to self-reported risk.** The rubric instructs it to read the update text and due date and form its own judgment, since the self-report-vs-reality gap (see `HND-88`/`HND-89` in the mock data) is exactly what this tool is supposed to catch.

Running `python classify.py` classifies all 17 mock updates and prints a predicted-vs-ground-truth match rate as a first sanity check. A full accuracy breakdown with false positive/negative analysis is Milestone 5.

**First test run: 17/17 (100%) classification match** against the author-labeled ground truth, including the two cases the rubric was specifically designed to catch:
- `HND-88` — self-rated "Medium" but due tomorrow and still blocked on a Legal dependency → correctly classified `blocked`.
- `HND-89` — Legal self-rated its own risk "Low," but that delay is what's blocking `HND-88` → correctly classified `at_risk` rather than trusting the Low self-report.

One signal-type judgment call worth noting for Milestone 5: on `HND-146c` the model chose `bottlenecked` where the ground truth was `quiet` — both are defensible for a vendor unresponsive for 9+ days (it's quiet *and* that silence is what's bottlenecking the work), so this isn't counted as a miss but is worth revisiting when the eval gets more rigorous.

Each run also writes `data/classified_updates.json` — the mock updates enriched with `ai_classification`, `ai_signal`, `ai_reason` — so downstream steps (pattern detection, reporting) don't need to re-classify every time.

### Setup

```bash
cd 01-program-risk-intelligence
pip3 install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY
python3 classify.py
```

## Cross-source pattern detection

A single update can only tell you about itself. [`detect_patterns.py`](./detect_patterns.py) takes the *whole batch* of classified updates in one call and looks for things that are only visible across multiple updates:

- **shared_dependency** — two+ updates from different teams point at the same root cause (same vendor, same upstream team), even without referencing each other's ticket numbers.
- **team_overload** — one team has multiple issues this week where the *combination* signals real strain (e.g. an incident pulling engineers off an otherwise on-track item for the same team).
- **dependency_chain** — one team's update explains why another team is stuck (the blocker named in ticket A is literally the subject of ticket B).
- **systemic_theme** — the same signal type shows up across enough unrelated teams to indicate a program-level problem, not a one-off (e.g. several teams independently hit by emergencies the same week).

Design decisions, consistent with the classification step: the patterns are also enum-constrained and forced via `tool_choice` (a `report_cross_source_patterns` tool), `ground_truth_*` fields are stripped from the batch before it's sent, and a pattern is only reported if it involves 2+ distinct tickets and would actually change what a program lead does that week — restating a single ticket's own already-known risk doesn't count.

Running `python3 detect_patterns.py` (auto-runs `classify.py` first if `classified_updates.json` doesn't exist yet) found **6 patterns** in the first run against the mock data, including two the dataset was deliberately built to contain:
- `HND-146c` + `HND-520` — the "unresponsive vendor" and the vendor's own "paused everything for an emergency" update are the same root cause, just visible from two different sides.
- `HND-88` + `HND-89` — CDP's blocker and Legal's own admission that taxonomy review got bumped are literally the same fact reported from two teams.

It also surfaced one not explicitly engineered into the dataset but genuinely present: a **systemic_theme** across `HND-146b`, `HND-520`, `HND-89`, `HND-611`, and `HND-95` — five unrelated teams all reporting `competing_objectives` the same week, which reads as a portfolio-level pattern (emergencies/executive asks displacing planned work) rather than five isolated incidents. That's the kind of thing a Friday report built ticket-by-ticket would likely miss.

```bash
python3 detect_patterns.py
```

## Two-altitude reporting

[`generate_report.py`](./generate_report.py) drafts the same weekly report at two altitudes from the same underlying data — team-level detail and an executive summary — using Claude to write the prose. Both are grounded strictly in the classified updates and patterns already produced by Milestones 2-3; the prompts explicitly forbid inventing facts not present in the data.

### What gets stripped for the exec view, and why

The two altitudes are not "the same prompt, asked to be shorter." The executive payload is a **structurally different, smaller dataset** built in code before the model ever sees it (`build_exec_payload` in `generate_report.py`):

| Dropped from exec view | Why |
|---|---|
| Every `on_track` ticket's detail | A clean ticket doesn't need a paragraph. Rolled up into a single count in the health snapshot instead. |
| `update_text` (the team's raw submission) | Leadership needs the program's final call, not the raw source material that produced it. |
| `self_reported_risk` / `self_reported_rationale` | The whole point of this tool is that the AI classification is the trustworthy signal, not the self-report — surfacing the raw self-report at exec altitude would just reintroduce the noise the tool exists to filter out. (It's kept at team altitude, where a reader benefits from seeing *where* the AI disagreed with a team's own rating.) |

What's **promoted** to the top at exec altitude: cross-source patterns, especially `systemic_theme` ones — a portfolio-level pattern is exactly what a ticket-by-ticket team report tends to bury, and it's exactly what leadership most needs to see first.

Both prompts are also given the health-snapshot counts (on_track/at_risk/blocked/total) **pre-computed in Python**, not left for the model to count from the ticket list — an early test run had the exec report miscount ("8 at risk, 3 blocked, plus 2 more blocked call-outs" — wrong arithmetic) while composing prose. A report leadership acts on can't have arithmetic errors, so the numbers are now facts handed to the model, not something it derives.

Running `python3 generate_report.py` (auto-runs the upstream steps if their output doesn't exist yet) writes `data/team_report.md` and `data/exec_report.md`. On the mock dataset, the exec report condensed all 11 at-risk/blocked tickets into 5 patterns with a final "Other At-Risk/Blocked Tickets: None" line — every risk this week was already explained by a cross-source pattern, which is itself a useful thing for a program lead to know.

```bash
python3 generate_report.py
```

## Repo structure

```
01-program-risk-intelligence/
├── README.md              # this file
├── classify.py            # risk classification (Milestone 2)
├── detect_patterns.py     # cross-source pattern detection (Milestone 3)
├── generate_report.py     # two-altitude reporting (Milestone 4)
├── requirements.txt
├── .env.example
└── data/
    ├── mock_status_updates.json
    ├── classified_updates.json  # generated by classify.py
    ├── patterns.json            # generated by detect_patterns.py
    ├── team_report.md           # generated by generate_report.py
    └── exec_report.md           # generated by generate_report.py
```

## Roadmap

- [x] Milestone 1 — Repo setup & requirements
- [x] Milestone 2 — Risk classification build (Claude API) — 17/17 match on first test run
- [x] Milestone 3 — Cross-source pattern detection — 6 patterns found on first run
- [x] Milestone 4 — Two-altitude reporting (team-level + executive)
- [ ] Milestone 5 — Evaluation, polish & demo
