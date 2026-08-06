# Milestone 5 — Evaluation Report

## Regression set (mock_status_updates.json) (17 items)

- Classification accuracy: **100%** (17/17)
- Signal-type accuracy: **88%** (15/17)
- False positives (predicted more severe than actual): **0**
- False negatives (predicted less severe than actual, i.e. missed real risk): **0**

No false positives or false negatives in this set.

**Signal-type misses (classification still correct, but the *why* differed):**

- `HND-146` — predicted `none`, expected `bottlenecked`
- `HND-146c` — predicted `bottlenecked`, expected `quiet`

## Adversarial set (eval_scenarios.json) (8 items)

- Classification accuracy: **62%** (5/8)
- Signal-type accuracy: **100%** (8/8)
- False positives (predicted more severe than actual): **1**
- False negatives (predicted less severe than actual, i.e. missed real risk): **2**

| Ticket | Purpose | Expected | Predicted | Outcome | AI reason |
|---|---|---|---|---|---|
| HND-816 | Subtle unowned_escalation -- a risk raised through a slow channel (email) with a moderate self-report, not framed as a crisis. | at_risk | blocked | false_positive | A contract risk was flagged to the General Counsel's office two weeks ago with no response, and a follow-up this week has also gone unanswered, leaving the escalation unowned by any decision-maker. With the due date just one week away (Nov 7), this lack of pickup threatens the deadline and progress cannot move forward without GC input. |
| HND-814 | Ambiguous blocked-vs-at_risk boundary -- a defensible near-miss either way, used to test whether errors here are treated differently from a miss against on_track. | blocked | at_risk | false_negative | The localization fix depends entirely on the translation vendor, who has given no confirmed delivery date despite being asked twice this week, and launch is only 4 days away. This is a stalled dependency that threatens the due date, though work hasn't fully stopped yet since the vendor is still engaged -- self-reported 'Medium' risk understates the urgency given the tight timeline. |
| HND-818 | Missing/null self-report plus an empty update on an already-overdue ticket -- data-handling edge case, not just a content-judgment one. | blocked | at_risk | false_negative | No update text was submitted at all, and the report date (Oct 31) is already a week past the due date (Oct 24), indicating a lapse in vendor reporting on a task that should be complete. This silence past the deadline warrants follow-up to confirm actual status. |

## Reading these results

The regression set (17 items) is the same dataset the rubric in the README was written against, so a high score there mostly confirms the rubric is internally consistent -- it's not a strong test on its own.

The adversarial set (8 items) is the more meaningful number: each item was purpose-built to bait a specific failure mode (see the `purpose` column above) rather than to be a realistic 'typical' update. A tool that scores well here is resisting the two failure modes that would make it useless in practice: crying wolf on things that are actually fine (false positive), and getting lulled by calm language or an over-cautious self-report into missing something real (false negative).