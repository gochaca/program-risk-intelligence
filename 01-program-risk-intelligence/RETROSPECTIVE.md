# Retrospective: Program Risk & Vendor Coordination Intelligence

Built solo, Aug 6 – Aug 13, 2026 (repo scaffold to recorded demo, ~1 week). Six milestones: mock classification → cross-source pattern detection → two-altitude reporting → evaluation → live Jira/Gmail integration → demo materials.

This document has two parts: what actually happened on this project (Part 1), and a generalized checklist to start the next one faster (Part 2).

---

## Part 1: What happened

### Timeline

| Date | Milestone |
|---|---|
| 2026-08-06 | Repo scaffolded, risk rubric defined, mock dataset written |
| 2026-08-06/07 | Classification build (M2), cross-source pattern detection (M3), two-altitude reporting (M4) |
| 2026-08-07 | Milestone 5 evaluation (adversarial set). Real Jira connected same day — two incidents same day (below) |
| 2026-08-08–10 | Gmail connected, real reply-detection, full live loop validated end-to-end |
| 2026-08-10 | launchd scheduling activated with a hard stop date |
| 2026-08-11–13 | Demo script written, presentation materials built, demo recorded |

### What went well

- **Mock-before-live discipline held up.** Every milestone (1–5) was built and proven against local fixtures before Milestone 6 ever touched a real account. When real Jira/Gmail integration did land, it was a swap of one interface implementation for another (`get_jira_client()` picking Real vs. Mock by whether credentials exist), not a rewrite. This is the single biggest thing that made a solo, week-long build tractable.
- **Adversarial evaluation caught what a same-rubric regression set couldn't.** 100% on the regression set (built with the rubric) vs. 62% on a second, deliberately adversarial set built to bait known failure modes (anxious tone over a fine rollout, calm tone over real risk, an inflated self-report, dramatic language about something already resolved). All four tone-manipulation traps passed — the real misses clustered on one specific classification boundary, which is a far more credible, specific finding than "it got 100%."
- **Draft-only and hard-stop-date were the right calls made early, not bolted on.** No code path to `send()` ever existed for email. `SCHEDULING_END_DATE` was in place before automation went live, not added after a scare. Both of these turned "an AI agent that emails real people and writes to a real project board on a schedule" from a genuinely risky feature into a safe one.
- **Real bugs got documented in the README as they were found, not hidden.** This turned into a legitimate part of the pitch ("real bugs found and fixed in the open") rather than something to be embarrassed about.

### Real bugs and incidents (chronological)

Documenting these in detail because the pattern in almost all of them is the same: **code that was correct for the one case it was tested against, wrong for a case that only showed up under real conditions.**

1. **Stray tool-call tag leakage** in classifier output text — a formatting/parsing bug caught early, fixed with a stripping helper reused everywhere Claude's output gets displayed.
2. **Jira API endpoint deprecation** — `GET /rest/api/3/search` returned `410 Gone`; Atlassian had moved to `POST /rest/api/3/search/jql`. Only found by actually hitting the real API — nothing in local testing could have caught this.
3. **Unassigned ticket, no contact email** — the real Jira project had one pre-existing ticket with no assignee. The orchestrator would have tried to email `None`. Fixed by explicitly skipping (and logging) roster items with no `contact_email`.
4. **`simulate` mode touched a real account.** `get_jira_client()` auto-selects Real vs. Mock from whatever's configured in the environment. Once real credentials were set, running `simulate` — intended as a safe local test — silently posted 11 nonsense comments to the real project. **Caught by inspecting the actual comments before assuming success**, not by any automated check. Fixed by making `simulate` always instantiate Mock clients directly, ignoring environment configuration entirely — a safe-test mode must be structurally incapable of touching production, not just unlikely to.
5. **Leaked `credentials.json`.** Added directly through GitHub's web UI, not through local git — which matters because `.gitignore` has zero effect on files added that way, and stops protecting a file entirely once it's ever tracked. Caught by GitHub's own secret-scanning warning. The exposed OAuth client was revoked and replaced immediately; the file was removed from the tree. The dead credential is still visible in old commit history (harmless, since it's revoked, but never purged — that needs a force-push and wasn't judged worth it).
6. **Non-response miscount.** A ticket classified as "no response" was tracked via `self_reported_risk is None` — but a genuine reply that just doesn't state an explicit risk level *also* has that field as `None`. A real reply and real silence were indistinguishable in that one count, even though classification itself was unaffected. Fixed by tracking "was a reply found" explicitly, not inferring it after the fact from an unrelated field.
7. **Shared state file between test and live modes.** `simulate` and the live phases wrote to the same `cycle_state.json`. Running `simulate` (to test an unrelated feature) silently overwrote the real `sent_at`/`awaiting_response`, causing the next real `report` run to search from the wrong date and miss a reply that had genuinely arrived. Fixed with a fully separate `cycle_state.simulate.json` — no shared file left for one mode to corrupt for the other.
8. **Incomplete malformed-response handling.** `detect_patterns.py`'s retry logic checked for one failure shape (the `patterns` key missing entirely) but not another (the key present, its items malformed strings instead of objects) — a `TypeError` the retry never caught. The fix wasn't "add another retry," it was validating the actual shape before trusting it. **Lesson: "add a retry" isn't the same as "handle the failure class."**
9. **Missing filter in a second code path.** `send_first_requests()` correctly skipped unassigned tickets; `collect_responses()` didn't apply the same filter, so the one pre-existing unassigned ticket got classified and commented on despite never being asked for an update. The fix was one line — the bug existed because the same rule had to be remembered in two places instead of one.
10. **Demo content drift from real data.** Twice during demo-script prep, a script/example silently reverted to reading local mock fixtures (`data/classified_updates.json`, the `HND-*` dataset) instead of the real, live-pulled output (`data/live_classified_updates.json`, `CRH-*`) — once for the pattern-detection command, once for the classification example. Both looked identical on the surface (same shapes, same field names) and would have shown fabricated content live on a recording without careful checking of *which file* was being read.
11. **Self-referential demo narrative.** An early cross-dependency example had "Legal not responding to Legal" — internally illogical once actually read aloud. Fixed by finding a real ticket with a genuinely different blocker (a traveling VP with no delegate) rather than patching the existing story.
12. **Ambiguous instructions read as two steps instead of one.** A "Tools: Terminal — Python (`classify.py`, run live via inline `python3 -c`)" line was read as "first run `classify.py`, then also run the shown command" — it was actually describing one action, not two. Worth a second pass reading your own instructions as a first-time reader would.

### Process lessons

- **Parallel editing (GitHub web UI + local) caused repeated push rejections.** Every time, the fix was the same: `git fetch`, inspect what changed (`git log main..origin/main`, `git show`), then `git pull --rebase` (stashing local uncommitted work first if needed). Never force-push. When both sides touched the same lines, the conflict had to be read and resolved by hand — auto-merge silently let some stray/duplicate content through untouched, which then needed a second pass to catch.
- **A first attempt at a "spacing/legibility" fix (bumping font sizes in an SVG diagram) treated the symptom, not the cause** — the actual problem was columns placed too close together for any reasonable label length. Worth diagnosing root cause before the first fix, not after the first fix turns out insufficient.
- **File-delivery-to-user mechanisms aren't 100% reliable** — a chat-attachment delivery failed silently from the user's side; copying the file directly into a known folder (`~/Downloads`) was the reliable fallback.
- **"Mock data" needs a visible name, not just a comment.** Confusion about whether output was real or fabricated came up twice in this project, over two different scripts. The fix both times was the same: real output and mock/test output need to live in files whose names alone tell you which is which (`live_*.json` vs. plain `*.json` was the eventual convention) — don't rely on remembering which script reads which file.

---

## Part 2: Reusable checklist for the next project

A generalized build order and artifact list, independent of what the next tool actually does.

### Build order

1. **Write the definition before the code.** What are you classifying/deciding/generating, and what does each output category actually mean? This project's README led with "The problem" and "What 'at risk' means here" before any code — that rubric is what the evaluation set gets built against later, so getting it right early saves rework.
2. **Hand-author a mock dataset with known ground truth**, including a few genuinely ambiguous or edge-case items on purpose, not just clean examples.
3. **Build the core AI capability against the mock data only.** Forced tool-use / structured output over freeform text parsing, if the model needs to return anything beyond prose.
4. **Add the cross-record/aggregate layer**, if applicable — the insight that only exists at the "batch" level, not visible from any single record.
5. **Add multi-audience output**, if applicable — same underlying data, different altitude/detail level for different readers.
6. **Build the evaluation harness before claiming any accuracy number.** Two sets, not one:
   - a regression set (can share DNA with the rubric — mainly a sanity check, expect it to score high)
   - an **adversarial set built specifically to bait known failure modes** of whatever the tool does (tone vs. substance, trusting a stated label vs. checking it, recency/severity confusion) — this is the number that actually means something
   - explicit false-positive / false-negative breakdown, oriented toward whichever error direction is actually dangerous for the tool's purpose
7. **Design the Real/Mock interface before writing either implementation** — same method signatures, one function that auto-selects based on credential presence, so the orchestrator code never has to know or care which it's talking to.
8. **Decide the safety rails before connecting anything real**, not after:
   - Is there any code path that sends/writes/deletes without a human in the loop? If the tool shouldn't have one, make sure it structurally can't (not just "doesn't currently").
   - Does a "safe test mode" share any state or credentials with the live path? If yes, that's a future incident — separate them now.
   - If anything runs unattended/scheduled, does it have a hard stop condition, or does it run forever by default?
9. **Set up `.gitignore` before the first credential file is ever created**, not after. Remember it only protects local git operations — a file added through a web UI, or already tracked once, is not protected by it at all.
10. **Connect one real account/system at a time, validate end-to-end, then the next.** Expect API surprises (deprecated endpoints, missing fields, auth quirks) that no amount of mock testing would have caught.
11. **Document real bugs/incidents as they happen**, in the README or an equivalent, including what caught them and the actual fix — not just "fixed a bug." This becomes part of the credibility of the project, not a liability.
12. **Build the demo last, from real output wherever possible.** Prefer live-pulled real data over the original mock/eval fixtures for anything shown on screen; if a script can read either mock or real data depending on which file path is passed, name the files so the distinction is impossible to miss (e.g. `live_` prefix), and double check *before* recording which one any given command actually reads.

### Artifact checklist

- [ ] Problem/rubric definition (README section, written first)
- [ ] Mock dataset with authored ground truth + edge cases
- [ ] Core classification/generation script, tested against mock data
- [ ] Cross-record aggregate analysis (if the domain has one)
- [ ] Multi-audience report generation (if the domain has one)
- [ ] Evaluation script: regression set + adversarial set + false-positive/negative breakdown
- [ ] Real/Mock dual-implementation interface for every external system touched
- [ ] `.gitignore` covering every credential file, set up before first credential exists
- [ ] Explicit safety rails documented: what the tool will never do automatically, and why
- [ ] Scheduling/automation with a hard stop condition, if unattended
- [ ] README section documenting real bugs/incidents found integrating with live systems
- [ ] Demo script: real data, one unambiguous command per beat, tools named per section
- [ ] One-pager / follow-up materials (only after the demo itself is solid)

### Questions worth asking before starting the next one

- What's the equivalent of this project's "real reply from a real person" — i.e., what's the piece of real, external, unpredictable input that the mock dataset can't fully substitute for, and how early can that get connected?
- What's the dangerous error direction for this tool specifically (false positive vs. false negative), and does the evaluation set actually stress that direction?
- What would "draft-only" or its equivalent look like here — is there a safe default posture (propose, don't act) before earning the right to act automatically?
