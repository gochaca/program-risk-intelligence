# Demo recording script

Target length: 4-5 minutes. Screen recording (QuickTime: File → New Screen Recording), terminal + browser tabs (GitHub, Jira, Gmail) — switch between them as noted. This script matches the finalized slide deck's examples exactly, so the video and the slides tell one consistent story.

## 1. The problem (25 sec, talking over the README)

**Tools:** GitHub (README) — or swap in the Problem/Solution slides from the deck if you'd rather open on those instead of scrolled GitHub text.

"Every week, I would collect status updates for 10-15 teams, each with multiple in flight projects. I would use this to create reports for leadership. I had three weekly challenges to overcome. 
1. reported risk was isolated of other projects and therefor unreliable
2. The real risk tends to live *between* the updates
3. Priority churn and re-prioritization caused confusion and missed deadlines."

I built this tool to catch all three automatically."

Show: `01-program-risk-intelligence/README.md` on GitHub, "The problem" section.

## 2. Live Moment 1 — the model overrides a self-reported "Low" (40 sec)

**Tools:** Terminal — Python (`classify.py`, run live via inline `python3 -c`).

"Here's a real case from the test data. Here, the team de-prioritized a ticket for a VP-requested homepage redesign, rated their own risk 'Low' — 'not urgent, fine to slip a sprint.'"

Show terminal, run:
```bash
cd ~/Projects/program-risk-intelligence/01-program-risk-intelligence
python3 -c "
import json
from classify import classify_update
d = json.load(open('data/eval_scenarios.json'))
item = next(u for u in d['updates'] if u['update_id'] == 'EVAL-4')
payload = {k: v for k, v in item.items() if not k.startswith('ground_truth') and k != 'purpose'}
print('TEAM SAID:', item['self_reported_risk'], '-', item['self_reported_rationale'])
result = classify_update(payload)
print('AI SAID:', result['classification'], '-', result['reason'])
"
```
Transition ## Now I would like to show you, in real-time, how the model uses facts to provide an updated rating based on analysis. 
"The team was transparent and the model didn't dispute the facts. It disputed whether 'Low' was the right word for a due date three days out with nothing scheduled to happen before it."

## 3. Live Moment 2 — cross-dependency detection, on a real Jira project (45 sec)

**Tools:** Browser — Jira Cloud (real tickets `CRH-4`, `CRH-5`, `CRH-9`, with the posted AI comments).

"This next one isn't test data — it's from a real Jira Cloud project I connected this tool to."

Switch to browser, show the real Jira tickets `CRH-4`, `CRH-5`, and `CRH-9` with the posted AI comments.

"Three tickets, three different teams, none of them mention each other. `CRH-9`'s vendor has gone silent for two weeks. `CRH-5` — Legal's own ticket — is actually *done*, just stuck waiting on a VP's sign-off, and she's traveling until Monday, after the due date. `CRH-4` is blocked because Legal hasn't delivered CCPA copy, flagged urgent, but nobody's actually chasing it. Read individually, three separate blocked tickets. 

Read together —" show the cross-source pattern finding (from the exec report or re-run `detect_patterns.py` live) "— they're all the same failure: work is stalled on an approval or a response, and nobody owns pushing it forward. That's the whole pitch: read every update together, not one at a time."

## 4. Two-altitude reporting (30 sec)

**Tools:** Browser (the two-altitude comparison graphic) — or Terminal + text editor if you'd rather run `generate_report.py` live and show the two output files directly.

Open the two-altitude comparison graphic, or run `python3 generate_report.py` live and show both output files.

"Same classified data, same pattern, two audiences. Team-level detail keeps every ticket and the raw self-report. The executive version strips that out entirely — leadership gets the program's final call, not the source material — and promotes the cross-source patterns to the top instead of burying them under 17 individual tickets."

## 5. Evaluation, honestly (35 sec)

**Tools:** Browser (evaluation scorecard graphic) — or GitHub (`data/evaluation_report.md`) if you'd rather show the raw file.

"I didn't just test this against the dataset I built the rubric with — that's circular. I built a second, adversarial set specifically to try to break it: anxious language over a fine rollout, calm boilerplate over a real risk, an inflated self-report over something already done, dramatic language about something already resolved."

Show the evaluation scorecard graphic or `data/evaluation_report.md`.

"100% on the regression set, 62% on the adversarial one — and that's the more honest number. All four tone-manipulation traps passed. The misses clustered on one specific boundary, including one real limitation I documented rather than hid."

## 6. Real-world validation (40 sec)

**Tools:** Gmail (Drafts folder) + Terminal (`launchctl list`).

"This isn't just a demo running against fixtures. It's connected to a live Jira project and a real Gmail account."

Show, in quick succession:
- Gmail Drafts folder with `[Status request]` drafts sitting unsent — "Draft-only, on purpose. There's no code path to send anything automatically — a human reviews and sends every email this tool ever produces."
- Terminal: `launchctl list | grep programriskintelligence` — "It's scheduled to run itself — Wednesday requests, Friday follow-ups, Friday reports — and it has a hard stop date built in. It doesn't run forever; it shuts itself off."

"Building this against real systems surfaced real bugs — a state file two modes were silently sharing, a miscounted non-response stat, a malformed API response. All documented in the README, not swept under the rug, because that's the same discipline the tool itself is built to enforce."

## 7. Close (20 sec)

**Tools:** GitHub (repo/commit history on screen as backdrop) — no specific action, just the spoken close.

"Whole thing's on GitHub, commit by commit, six milestones, real Jira, real Gmail, real bugs found and fixed in the open — [repo URL]. Claude did the classification and pattern-detection reasoning. I did the judgment calls on what 'risk' actually means, from having done this by hand."

---

## Once recorded

1. Upload wherever you're hosting it (Loom / YouTube unlisted / repo-attached video).
2. Send me the link and I'll drop it into the README's Demo section, the one-pager, and the follow-up email, and do the final commit + push.
