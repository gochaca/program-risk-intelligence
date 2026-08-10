# Program Risk & Vendor Coordination Intelligence

**Status:** Milestone 6: Complete: Live vendor coordination (full loop validated end-to-end against real Jira + Gmail)

My custom designed and built tool that sends update requests and ingests updates from multiple teams (internal and external), classifies risk with a stated reason, flags patterns across teams, and auto-drafts an analysis in a weekly status report and executive summary [Program Risk and Vendor Coordination Intelligence Weekly Status](https://claude.ai/code/artifact/4ce4c387-19b0-4474-aa89-f1066131bba4)

## The problem

Every week, I would have to track down status updates for more than team teams. Internal teams do not respond, external teams are traveling and won't be back until Monday, all while we have a dozen active issues requiring updates. It was frustrating, tedious and most importantly, unreliable. Once the updates were received, I would get the status updates I could, and update Jira: 

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

## Evaluation

[`evaluate.py`](./evaluate.py) runs two separate test sets and scores each with the same metric: classification accuracy, signal-type accuracy, and an explicit false positive / false negative breakdown (severity ordered `on_track < at_risk < blocked`; a false positive predicts *more* severe than truth, a false negative predicts *less* severe — the more dangerous direction, since missing a real risk is the whole failure mode this tool exists to prevent).

- **Regression set** — the original 17 mock updates. Useful as a sanity check, but a high score here mostly proves the rubric is internally consistent with itself, since the dataset and the rubric were built together.
- **Adversarial set** ([`data/eval_scenarios.json`](./data/eval_scenarios.json), 8 items) — built specifically for this milestone, and specifically *not* to be realistic "typical" updates. Each one baits a distinct failure mode: an anxious-sounding update describing a fully successful rollout (false-positive bait), three weeks of content-free "all good" boilerplate on a due-tomorrow item (false-negative bait), a team's own High self-report on an item that's actually fully signed off (does the tool blindly trust an inflated self-report?), dramatic incident language about something already resolved in the past, a quietly-worded deprioritization with no "emergency" framing, an escalation raised through a slow channel (email) rather than dramatically, a genuinely ambiguous blocked-vs-at_risk case, and a missing/null update on an already-overdue ticket (a data-handling edge case, not just a judgment one).

### Results (first run)

| Set | Classification accuracy | Signal accuracy | False positives | False negatives |
|---|---|---|---|---|
| Regression (17) | 100% (17/17) | 88% (15/17) | 0 | 0 |
| Adversarial (8) | 62% (5/8) | 100% (8/8) | 1 | 2 |

The adversarial number is the one that matters. The four cases built purely to bait tone-based errors — anxious-but-fine, calm-but-risky, inflated-self-report-but-fine, dramatic-but-resolved — **all classified correctly**. That's the core claim of this tool actually holding up: it isn't just pattern-matching on alarmed language or trusting a team's own rating.

The three misses all cluster on one specific boundary — blocked vs. at_risk — not on tone-manipulation:
- One (the deliberately ambiguous case) was expected to be a near-miss either way.
- One (`HND-816`, a slow-channel escalation) the model called `blocked` where I'd called `at_risk` — arguably the model's call is defensible too, given two unanswered follow-ups to General Counsel.
- One (`HND-818`, an empty update on an already-week-overdue ticket) is a genuine, worth-fixing miss: the model called it `at_risk` when total silence past an already-missed due date should read as `blocked`. This is a real limitation, not a close call — worth tightening the rubric's language around "overdue + no response" in a future iteration.

Full per-item results, including reasons given for every miss: [`data/evaluation_report.md`](./data/evaluation_report.md).

```bash
python3 evaluate.py
```

## Live vendor coordination (Milestone 6)

Milestones 1-5 run entirely on a static mock dataset. This milestone closes the loop: pull this week's open tickets from Jira, email each owner asking for a status update, follow up only with whoever hasn't replied, then feed whatever came back into the same classify → detect_patterns → generate_report pipeline and write the result back to Jira as a comment.

**Cadence:** first request Wednesday, follow-up Friday morning (non-responders only), report + Jira write-back once replies are in.

### Architecture: Mock and Real behind the same interface

[`jira_client.py`](./jira_client.py) and [`gmail_client.py`](./gmail_client.py) each ship two implementations of the same two methods (`get_roster()`/`post_comment()` for Jira, `create_draft()` for Gmail):

- **Mock** — reads/writes local JSON fixtures (`data/team_roster.json`, `data/mock_drafts.json`, `data/mock_jira_comments.json`). No network calls, no credentials, safe to run any time.
- **Real** — actual Jira Cloud REST API v3 and Gmail API calls.

`get_jira_client()` / `get_gmail_client()` pick Real vs. Mock automatically based on whether live credentials are configured, so [`weekly_cycle.py`](./weekly_cycle.py) — the orchestrator — never has to know which one it's talking to. This is the same mock-before-live discipline as Milestones 1-5, applied one level up: build and prove the workflow against fixtures, then swap the data source.

### Draft-only, on purpose

The Gmail client only ever calls `users().drafts().create()`. There is no code path to `users().messages().send()` anywhere in this codebase. Every email this tool produces — first request or follow-up — sits in the account's Drafts folder until a human reads it and clicks send. This was a deliberate choice, not a technical limitation: a tool that emails real colleagues on a schedule with zero human review is a much bigger blast radius than one that drafts and waits.

### Real people don't fill in templates

Rather than require a rigid reply format and regex-parse it, [`email_parser.py`](./email_parser.py) uses the same forced-tool-use pattern as `classify.py` to have Claude read a freeform reply and extract the update text and self-reported risk (`null` if the sender didn't actually state one — the parser is told explicitly not to invent a rating). The mock inbox ([`data/mock_inbox.json`](./data/mock_inbox.json)) is written as natural, unstructured email replies specifically to exercise this, not a clean template.

### Silence is still data

A ticket that gets no reply to either request doesn't get dropped — it becomes an explicit "no response to two requests this week" record and goes through classification like everything else, consistent with the `quiet`/`unowned_escalation` signals already in the rubric. In the first simulated run, the one non-responding ticket (`HND-311`, matching its behavior all the way back in the Milestone 1 mock data) correctly classified as `blocked`.

### Running the simulation

```bash
python3 weekly_cycle.py simulate
```

Runs all three phases back-to-back against `data/team_roster.json` and `data/mock_inbox.json`: drafts 10 first-request emails, follows up with only the 3 non-responders, collects and parses replies, classifies, detects patterns, generates both report altitudes, and logs 10 "Jira comments" — all locally, no live accounts touched. Output: `data/live_classified_updates.json`, `live_patterns.json`, `live_team_report.md`, `live_exec_report.md`, `mock_drafts.json`, `mock_jira_comments.json`.

First simulated run: 0 tickets on track, 6 at_risk, 4 blocked (this roster is a deliberately risk-heavy subset carried over from the Milestone 1 mock data, not a representative "normal" week), and the exec report correctly rolled all 10 into 5 cross-source patterns with no leftover isolated tickets.

### Connecting real accounts

**Jira — connected and validated.** Set `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_ROSTER_JQL`, and `JIRA_TEAM_SOURCE` in `.env`. Tested end-to-end against a real Jira Cloud test project (`CRH`): created 10 test tickets (one per team, labeled by team since a single shared project has no per-team project name to key off of), assigned them, then ran `get_roster()` and `post_comment()` against them for real. Two real bugs turned up in the process and got fixed:

- **`GET /rest/api/3/search` is deprecated** — Atlassian retired it in favor of `POST /rest/api/3/search/jql`, returning `410 Gone` on the old endpoint. `RealJiraClient.get_roster()` now uses the current one.
- **Tickets with no assignee have no email to send to.** The real project had one pre-existing ticket with no assignee; the orchestrator would have tried to draft an email to `None`. `send_first_requests()` now skips (and logs) any roster item with no `contact_email` rather than failing or drafting a broken email.

`JIRA_TEAM_SOURCE=label` reads the first label on a ticket as its "team" — set `JIRA_TEAM_SOURCE=component` instead if your project uses components for that.

**Gmail — connected and validated.** Create a Google Cloud OAuth client (Desktop app type), save it as `credentials.json` in this directory (git-ignored), add yourself as a **Test user** on the OAuth consent screen (unverified apps only work for accounts explicitly listed there — the first attempt here failed with `Error 403: access_denied` until that was done), then run `python3 gmail_client.py` once to complete the one-time browser consent flow. Requires `pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib` (kept out of `requirements.txt` since mock/simulate mode doesn't need them).

Tested end-to-end against a real Gmail account: `create_draft()` confirmed (10 real drafts created from the live Jira roster, verified via the API to have the correct subject/recipient/body and to be sitting unsent), and `find_reply()` confirmed against a real reply from a second test address (`ai.chaca69420@gmail.com`) — see "Full live loop, validated" below.

### Real reply-detection

`send_followups()` and the `report` phase's `collect_responses()` used to have a hard live-mode limitation: they couldn't tell who had actually replied, so `followup` would have emailed everyone regardless, and `report` would have treated every ticket as a non-response. That's fixed now:

- `send_first_requests()` records when it ran, in `data/cycle_state.json` (`sent_at`).
- `RealGmailClient.find_reply(jira_ticket, since_date)` searches the inbox (`gmail.readonly` scope, added alongside the existing `gmail.compose` scope) for a message whose subject contains the ticket ID, received since that date, not from the account owner — and returns its plain-text body if found. The ticket ID is quoted in the search query, since Gmail's query parser treats a bare hyphen as a NOT operator (`CRH-2` unquoted would search for "CRH" and NOT "2").
- In live mode, `send_followups()` checks `find_reply()` for every ticket still awaiting a response and drops anyone who's already replied instead of following up regardless; `collect_responses()` checks it for every roster ticket to build the actual update record, falling back to the same "no response" record as before only when nothing's found.
- `MockGmailClient` gained a matching `find_reply()` for interface consistency (backed by an optional `simulated_replies` dict passed at construction), but `simulate` mode keeps using its own existing mock-inbox logic rather than this — that logic is already tested and phase-aware (first-request vs. follow-up timing), and there was no reason to touch a working path.

Unit-tested (the mock path and the MIME-body-extraction helper), and now validated against a real match too (see below) — not just the search mechanism in isolation.

### Full live loop, validated

With a second test address (`ai.chaca69420@gmail.com`) sending a real reply to one ticket (`CRH-2`, subject line including `(CRH-2)` per the search format `find_reply()` expects), the entire loop ran for real:

1. `find_reply('CRH-2', ...)` found the message and returned its plain-text body.
2. `email_parser.parse_reply_to_update()` turned "*Copy has been implemented across all pages. No blockers on our end, should be done by Wednesday.*" into a structured update — correctly inferred `self_reported_risk: Low` from "no blockers" even though the reply never stated a risk level explicitly.
3. `python3 weekly_cycle.py report` ran the full pipeline against live Jira + live Gmail: `CRH-2` classified `on_track`; the other 9 tickets (genuinely silent, since nobody else was going to reply to a solo test project) classified based on actual "no response" records; cross-source pattern detection correctly recognized 8 unrelated tickets all showing the identical "two unanswered requests" symptom as one systemic pattern worth investigating, rather than listing them as 8 coincidental problems; both report altitudes generated; classifications posted back to the real tickets as comments.

One real bug turned up in this run: `collect_responses()` didn't apply the same "skip tickets with no assignee" rule that `send_first_requests()` uses, so `CRH-1` (the one pre-existing, unassigned ticket) got classified `blocked` and commented on even though it was never actually asked for an update. Fixed by applying the same `contact_email` filter in `collect_responses()` — a ticket the tool never asked shouldn't get judged for not answering. The erroneous comment was deleted from the real ticket afterward.

### Two real incidents today, and the fixes

**Incident 1 — `simulate` touched a real account.** While testing the real Jira connection, `python3 weekly_cycle.py simulate` was run to regenerate the mock demo artifacts — but at the time, `simulate` used `get_jira_client()`, which auto-selects Real vs. Mock based on whatever's configured in the environment. Since real Jira credentials were now set, `simulate` silently ran against the **real** `CRH` project instead of the mock fixtures, and posted 11 nonsense "no response" comments (built from the old 2025 mock inbox, which has nothing matching real `CRH-xxx` keys) onto real tickets.

Caught by inspecting the actual comments before assuming success, and fixed properly rather than papered over: `simulate` now always instantiates `MockJiraClient()`/`MockGmailClient()` directly, regardless of what's configured — a mode whose entire purpose is a safe local test must not be able to touch a real account just because credentials happen to be present. The 11 bad comments were deleted via the API afterward.

**Incident 2 — a real `credentials.json` got committed to the repo root.** Found via GitHub's own secret-scanning warning. The file wasn't added through any local git operation on this project — the path (`credentials.json` at the repo root, not `01-program-risk-intelligence/credentials.json`) and the commit pattern (`Create`, then two `Update`s) point to it being added directly through GitHub's website. That matters because **`.gitignore` has zero effect on files created that way** — it only stops local git tooling from picking up new files, and it stops protecting a file entirely once that file is ever tracked. The exposed OAuth client was revoked and replaced immediately; the file was removed from the current tree (`git rm`) once the rotation was confirmed. The dead credential still exists in the old commit history — harmless now that it's revoked, but history hasn't been rewritten to remove it, since that needs a force-push and wasn't asked for.

Documenting both here rather than quietly fixing them, since "here's what broke and how it got caught and fixed" is exactly the kind of thing worth being honest about in a project whose whole pitch is catching risk before it becomes a blocker.

### The first real unattended run

The Friday 3pm `report` job fired on its own for the first time on 2026-08-07 — the very first scheduled occurrence after activation — with no one watching. `logs/report.log` shows it ran cleanly: collected updates, classified, posted comments to real Jira tickets. That run happened to land *before* the `CRH-2` test reply was sent that same day, so it correctly saw zero replies at that moment — not a bug, just real-time state at whatever instant a scheduled job fires.

Investigating that, though, turned up a real bug: `collect_responses()`'s non-response count was based on `self_reported_risk is None`, but a genuine reply that just doesn't state an explicit risk level (e.g. "copy's done, no blockers" with no Low/Medium/High) *also* has `self_reported_risk: None` — so a real reply and a genuine silence were indistinguishable in that count, even though the classification itself was always correct. Fixed by tracking whether a reply was actually found, explicitly, rather than inferring it after the fact from an unrelated field.

### Jira comments now include the actual reply, not just the AI's take

`post_classifications_to_jira()` used to post only the AI's classification and reasoning — never what the person actually wrote. Now every comment includes the real reply text verbatim (or "No reply received..." when genuinely silent) alongside the AI's classification, so anyone reading the Jira ticket sees the source material, not just a conclusion drawn from it.

The raw reply is carried as a separate `raw_reply` field, deliberately kept out of every Claude call (`classify_update`, `detect_patterns`, `generate_team_report`, `generate_exec_report`) via a small `_without_raw_reply()` strip at each call site — same discipline as stripping `ground_truth_*` fields elsewhere in this codebase. It's just for the Jira comment, and for anyone reading `live_classified_updates.json` directly.

Validating this against the real Jira project surfaced one more real bug, in the same family as the earlier `simulate`-touched-a-real-account incident: `simulate` mode and the live phases were sharing a single `cycle_state.json`. Running `simulate` (as part of testing this feature) silently overwrote the real `sent_at`/`awaiting_response` with the mock fixture's values, so the next real `report` run searched from the wrong date and reported `CRH-2` as a non-response even though the reply genuinely existed. Fixed by giving `simulate` its own `cycle_state.simulate.json`, entirely separate from the live state file — there's no longer a shared file for one mode to corrupt for the other. Re-validated afterward: the real Jira comment above (`ON_TRACK`, quoting the real reply) is from that corrected run.

### Scheduling

[`launchd/`](./launchd/) has three macOS launchd agent definitions, one per phase, following the cadence set earlier: first-request Wednesday 9am, followup Friday 8am, report Friday 3pm (leaving hours for Friday-morning follow-up replies to land before the report generates). launchd rather than cron, since it's the native, more reliable scheduler on macOS.

"Followup at 8am" doesn't mean everyone gets emailed again at 8am — the phase runs then, but `find_reply()` (see above) checks who's actually replied first and only drafts a follow-up for the ones who haven't. Someone who replied Wednesday afternoon never gets a redundant nudge.

Each plist runs `python3 weekly_cycle.py <phase>` with an absolute path and explicit `WorkingDirectory`, so it works the same whether triggered by a human or by launchd. Output goes to `logs/<phase>.log` / `logs/<phase>.err.log` (git-ignored).

```bash
cd 01-program-risk-intelligence/launchd
./install_scheduling.sh    # installs and activates all three jobs
./uninstall_scheduling.sh  # stops and removes them
```

**Active.** Installed via `install_scheduling.sh` and confirmed registered (`launchctl list | grep programriskintelligence`). This now runs completely unattended — no chat session, no confirmation per run: real emails get drafted, real Jira comments get posted, on a schedule. That's a meaningfully bigger blast radius than anything else in this project (everything before this needed a human to type a command), which is exactly why it stayed off until deliberately turned on, and why it has a built-in stop condition rather than running forever (below).

### A hard stop, not indefinite

launchd's `StartCalendarInterval` is built for pure recurrence, like cron — there's no year field, no native way to say "run weekly, but only until a date." So the cutoff is enforced in the script itself: `SCHEDULING_END_DATE` in `.env` (currently `2026-08-14`, a Friday, so that week's full cycle still completes). Every live-mode run checks this first, via `_past_scheduling_cutoff()`. Once today is past that date:

- The run does no real work (no emails drafted, no Jira writes).
- It automatically runs `uninstall_scheduling.sh`, deregistering all three launchd jobs — so they stop existing entirely, not just silently no-op forever.

The comparison is inclusive (`_is_past_cutoff()`, unit-tested separately from the uninstall side effect so the logic could be verified without risking an accidental real uninstall of the jobs that were just activated): the end date itself still runs normally, only days after it are blocked. Leave `SCHEDULING_END_DATE` unset to run indefinitely instead.

### Known limitations, stated honestly

- **Only one real responder tested.** The full loop is validated with one real reply (`CRH-2`); multi-team dynamics (several different real people replying with genuinely different content) haven't been tested since this is still a solo test project.
- **Scheduling is built but not activated** — see above.

## Repo structure

```
01-program-risk-intelligence/
├── README.md                # this file
├── classify.py               # risk classification (Milestone 2)
├── detect_patterns.py        # cross-source pattern detection (Milestone 3)
├── generate_report.py        # two-altitude reporting (Milestone 4)
├── evaluate.py                # evaluation & false positive/negative analysis (Milestone 5)
├── email_templates.py         # first-request / follow-up email copy (Milestone 6)
├── email_parser.py            # freeform reply -> structured update, via Claude (Milestone 6)
├── jira_client.py              # Mock + Real Jira Cloud REST API client (Milestone 6)
├── gmail_client.py             # Mock + Real Gmail API client, draft-only (Milestone 6)
├── weekly_cycle.py             # orchestrator: Wed request -> Fri followup -> report (Milestone 6)
├── requirements.txt
├── .env.example
├── launchd/                     # scheduling: 3 launchd agents + install/uninstall scripts (Milestone 6)
├── logs/                        # launchd job output (git-ignored, .gitkeep only)
└── data/
    ├── mock_status_updates.json
    ├── eval_scenarios.json       # adversarial test set (Milestone 5)
    ├── team_roster.json           # mock Jira roster (Milestone 6)
    ├── mock_inbox.json            # simulated email replies (Milestone 6)
    ├── classified_updates.json   # generated by classify.py
    ├── patterns.json              # generated by detect_patterns.py
    ├── team_report.md             # generated by generate_report.py
    ├── exec_report.md             # generated by generate_report.py
    ├── evaluation_report.md       # generated by evaluate.py
    ├── live_classified_updates.json  # generated by weekly_cycle.py
    ├── live_patterns.json            # generated by weekly_cycle.py
    ├── live_team_report.md           # generated by weekly_cycle.py
    ├── live_exec_report.md           # generated by weekly_cycle.py
    ├── mock_drafts.json               # generated by weekly_cycle.py (MockGmailClient)
    └── mock_jira_comments.json        # generated by weekly_cycle.py (MockJiraClient)
```

## Demo

_Recording pending — script at [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md). Link goes here once it's up._

## Roadmap

- [x] Milestone 1 — Repo setup & requirements
- [x] Milestone 2 — Risk classification build (Claude API) — 17/17 match on first test run
- [x] Milestone 3 — Cross-source pattern detection — 6 patterns found on first run
- [x] Milestone 4 — Two-altitude reporting (team-level + executive)
- [x] Milestone 5a — Evaluation & polish — regression 100%, adversarial 62% (0 false positives, 2 false negatives, all detailed above)
- [ ] Milestone 5b — Record and link demo
- [x] Milestone 6a — Live vendor coordination design: Jira + Gmail clients, email templates/parsing, Wed/Fri orchestrator — tested end-to-end against mock fixtures
- [x] Milestone 6b — Connect real Jira test project (`CRH`) — validated `get_roster()`/`post_comment()` against 10 real tickets; fixed a deprecated-endpoint bug and a simulate-mode safety bug found in the process
- [x] Milestone 6c — Connect real Gmail account — OAuth flow completed (needed adding the account as a Test user first, or Google returns `Error 403: access_denied`); `create_draft()` and inbox search both validated with 10 real drafts
- [x] Milestone 6d — Build and validate real reply-detection end to end — a second test address (`ai.chaca69420@gmail.com`) replied for real, `find_reply()` found it, the parser extracted a structured update from it, and `python3 weekly_cycle.py report` classified it correctly (`on_track`) alongside 9 genuine non-responses, with cross-source patterns and both report altitudes generated from real data and posted back to real Jira tickets
- [x] Milestone 6e — Build and activate scheduling (`launchd/`, 3 agents: Wed 9am / Fri 8am / Fri 3pm) with install/uninstall scripts and a `SCHEDULING_END_DATE` cutoff so it stops (and self-uninstalls) after 2026-08-14 instead of running indefinitely — active now, confirmed registered with launchd
