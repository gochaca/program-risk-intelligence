# Demo recording script

Target length: 3-4 minutes. Screen recording (QuickTime: File → New Screen Recording), terminal + browser tab open side by side or full-screen switching between them.

## 1. The problem (30 sec, talking over your terminal/README)

"Every Friday I collect status updates from about 10 teams and vendors, 1-5 issues each, and turn it into a leadership report. The two hard parts: a team's own risk rating is unreliable in isolation, and the real risk often lives *between* updates, not inside one — two teams naming the same vendor as a blocker, three unrelated emergencies landing the same week. I built this to catch that automatically."

Show: `01-program-risk-intelligence/README.md` on GitHub, scrolled to "The problem" section.

## 2. The pipeline, live (90 sec)

Run in terminal, narrating each step:

```bash
cd ~/Projects/program-risk-intelligence/01-program-risk-intelligence
python3 classify.py
```
"This classifies each update — on track, at risk, or blocked — with a reason, and it's explicitly told not to just trust the self-reported rating." Let it run, point out the match-rate line at the end.

```bash
python3 detect_patterns.py
```
"This is the interesting part — it looks at the whole batch at once and finds things no single update reveals." Point out one pattern in the output, e.g. the BrightPath vendor pattern connecting two tickets.

```bash
python3 generate_report.py
```
"And this drafts both altitudes from the same data — team detail and an executive summary — with the exec version structurally stripped down, not just shortened."

## 3. The dashboard (60 sec)

Open the published dashboard artifact in browser.
- Point at the health snapshot stat bar.
- Click into "Executive View" — read one pattern card out loud, especially the systemic_theme one (five unrelated teams hit by competing objectives the same week).
- Switch to "Team Detail View" — find `HND-88`/`HND-89`, point out the "AI disagrees with self-reported rating" flag — this is the exact self-report-vs-reality gap the tool exists to catch.

## 4. Evaluation, honestly (45 sec)

"I didn't just test it against the dataset I built the rubric with — that's circular. I built a second, adversarial set specifically to try to trip it up: anxious language over a fine rollout, calm boilerplate over a real risk, an inflated self-report over something already done." Show `data/evaluation_report.md` on GitHub.

"It got 100% on the regression set, but only 62% on the adversarial one — and that's the more honest number. The good news: all four tone-manipulation traps passed. The misses all clustered on one specific boundary — blocked versus at-risk — including one real limitation I documented rather than hid."

## 5. Close (15 sec)

"Whole thing's on GitHub, commit-by-commit, five milestones, [repo URL]. Built with Claude doing the classification and pattern-detection work, me doing the judgment calls on what 'risk' actually means from having done this by hand."

---

## Once recorded

1. Upload wherever you're hosting it (Loom / YouTube unlisted / repo-attached video).
2. Send me the link and I'll drop it into the README's Demo section and do the final commit + push to close out Milestone 5.
