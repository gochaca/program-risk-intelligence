# Program Status Report — Team-Level Detail

## Health Snapshot
**On Track: 6 | At Risk: 7 | Blocked: 4 | Total: 17**

---

## Cross-Source Patterns (Act on These First)

### 1. Acme Cloud Infrastructure — one vendor capacity problem, three tickets at risk
**Tickets:** HND-310, HND-700, HND-311
Acme's staffing shortage caused a second cutover rehearsal slip (HND-310), an unanswered escalation to both Acme's account exec and our own VP (HND-700), and a silent Security Review update (HND-311) — all in the same week, all the same root cause.
**Action:** Escalate directly to Acme leadership this week for a consolidated resourcing commitment before 11/07. Stop treating these as three separate risks.

### 2. BrightPath firmware emergency is blocking CCPA dealer rollout
**Tickets:** HND-146c, HND-520
Dealer Systems (HND-146c) can't push CCPA copy live without BrightPath's release calendar confirmation. BrightPath's own update (HND-520) confirms all non-firmware requests, including this one, are paused with no ETA.
**Action:** Escalate to BrightPath now with a specific target date ask — don't wait on a request that's explicitly deprioritized on their end. CCPA due date is 10/31.

### 3. CDP is already blocked by Legal Ops' own deprioritization
**Tickets:** HND-88, HND-89
HND-88 (CDP) is blocked waiting on consent taxonomy confirmation, due **today (10/25)**. HND-89 (Legal Ops) confirms the review was pushed to next week due to competing work.
**Action:** Treat as an already-missed dependency, not just "at risk." Get Legal Ops to commit a hard date this week.

### 4. Legal Ops has no slack — three simultaneous asks
**Tickets:** HND-89, HND-146, HND-201
CCPA copy work plus an unplanned EU DSAR audit request are the stated reasons the consent taxonomy review slipped, directly feeding the HND-88 block above.
**Action:** Assess whether Legal Ops needs temporary support before more downstream teams stall.

### 5. Zero-buffer window across IAM and Mobile, 10/24–10/26
**Tickets:** HND-150, HND-611, HND-610
IAM pulled two engineers off SSO cert work (HND-610) to handle an unplanned partner incident (HND-611), leaving zero buffer. Mobile's security patch (HND-150) is also tight on 10/25, and separately delaying CCPA work (HND-146b).
**Action:** Treat this window as high-risk across both teams; check contingency staffing rather than trusting "still on track" self-reports if anything else breaks.

### 6. Program-wide: unplanned work is displacing planned work everywhere
**Tickets:** HND-146b, HND-89, HND-611, HND-520, HND-95
Five unrelated tickets across Mobile, Legal Ops, IAM, a vendor, and Marketing all show the same signal — emergencies bumping planned deliverables in the same week.
**Action:** Raise at leadership level as a capacity/prioritization issue, not five separate incidents. The volume indicates insufficient program-wide slack.

---

## Ticket Detail by Team

### Web Platform Team
**HND-146** — CCPA Regulatory Website Updates - October | Due 10/31
- **AI: at_risk** (signal: none) — Copy finalized 10/24; three-team implementation and validation only now starting, one week to deadline.
- Self-reported: **Medium** — matches AI directionally (no major gap), but rationale focuses only on validation tracking, not the timeline compression.

### Mobile App Engineering
**HND-146b** — CCPA Regulatory Website Updates - October | Due 10/31
- **AI: at_risk** (competing_objectives) — Security patch release train locked until 10/25; CCPA work starts after, targeting 10/30 — one day of buffer.
- Self-reported: **High** — team's own rating is *more* cautious than AI; no gap to flag, but worth honoring their urgency.

**HND-150** — Q4 Security Patch Release | Due 10/25
- **AI: on_track** (signal: none) — QA sign-off expected EOD 10/24, release on schedule, no open issues.
- Self-reported: **Low** — matches.

### Dealer Systems Integration
**HND-146c** — CCPA Regulatory Website Updates - October | Due 10/31
- **AI: blocked** (bottlenecked) — No response from BrightPath vendor since 10/15 request (9 days silence); cannot push copy live without their release calendar.
- Self-reported: **Medium** — **Gap:** team believes BrightPath will respond "early next week," but AI flags this as blocked given the silence and tight runway. See Pattern #2 — BrightPath is explicitly deprioritizing this.

**HND-77** — Regional Dealer Onboarding - Batch 4 | Due 10/22
- **AI: on_track** (signal: none) — Completed ahead of schedule, ticket closing.
- Self-reported: **Low** — matches.

### Data Privacy & Legal Ops
**HND-201** — CCPA Regulatory Website Updates - October | Due 10/20
- **AI: on_track** (signal: none) — Copy finalized and distributed on time; monitoring downstream only.
- Self-reported: **Low** — matches.

**HND-89** — Consent Taxonomy Review | Due 10/31
- **AI: at_risk** (competing_objectives) — Review pushed to next week; bandwidth consumed by CCPA copy and an unplanned EU DSAR audit request.
- Self-reported: **Low** — **Gap:** team rates this low risk to their own due date, but AI flags real deadline threat given zero progress this week and downstream dependency (HND-88) already breaching.

### Acme Cloud Infrastructure (Vendor)
**HND-310** — Data Center Cloud Migration - Cutover | Due 11/07
- **AI: at_risk** (bottlenecked) — Second rehearsal reschedule in three weeks (now 11/03), leaving only 4 days of buffer before cutover.
- Self-reported: **Medium** — **Gap:** vendor still expects to hit 11/07; AI flags the repeated-slippage pattern as a credible threat despite vendor confidence.

**HND-311** — Data Center Cloud Migration - Security Review | Due 10/31
- **AI: at_risk** (quiet) — No update this week; last substantive status (10/17) is stale "on track" with due date one week out.
- Self-reported: **Not submitted** — no self-report to compare; silence itself is the signal.

**HND-700** — Data Center Cloud Migration - Escalation | Due 10/24
- **AI: blocked** (unowned_escalation) — Escalation to Acme account exec and internal VP on 10/21 has gone unanswered; due date arrived today with no resolution.
- Self-reported: **High** — matches AI's severity assessment.

### Regional Marketing - NA
**HND-402** — Holiday Campaign Creative | Due 11/14
- **AI: on_track** (signal: none) — In standard final legal review, no blockers, three weeks of runway.
- Self-reported: **Low** — matches.

**HND-95** — Competitor-Response Campaign (Unplanned) | Due 10/31
- **AI: at_risk** (competing_objectives) — Unplanned CMO-driven campaign now fast-tracked ahead of planned holiday work (HND-402); sequencing not finalized, one week to deadline.
- Self-reported: **Medium** — **Gap:** team is confident both can be delivered; AI flags real timeline threat given unresolved sequencing.

### Regional Marketing - EMEA
**HND-403** — Holiday Campaign Creative - Localization | Due 11/14
- **AI: on_track** (signal: none) — Translation issue in 3 of 12 markets being actively fixed, resolution expected 10/28, well ahead of launch.
- Self-reported: **Low** — matches.

### BrightPath QA Services (Vendor)
**HND-520** — Dealer Portal Release Calendar | Due 10/24
- **AI: blocked** (competing_objectives) — All work paused, no ETA, due to team being fully diverted to an emergency firmware defect escalated by Honda.
- Self-reported: **High** — matches AI's severity. See Pattern #2 — this is the direct cause of HND-146c's block.

### Customer Data Platform (CDP) Team
**HND-88** — Consent Signal Integration | Due 10/25 (**tomorrow**)
- **AI: blocked** (bottlenecked) — Same status as last week; waiting on Legal Ops to confirm consent taxonomy; no forward movement.
- Self-reported: **Medium** — **Gap:** team frames this as "not our dependency" and rates Medium; AI flags as blocked given the imminent due date and zero progress. See Pattern #3.

### Enterprise Identity & Access Management
**HND-610** — SSO Certificate Renewal | Due 10/26
- **AI: on_track** (signal: none) — Staging test passed 10/22, production deploy scheduled 10/25, ahead of due date.
- Self-reported: **Low** — matches.

**HND-611** — Partner Integration Incident Response | Due 10/24
- **AI: at_risk** (competing_objectives) — Unplanned partner integration break pulled two engineers off SSO work, leaving zero buffer for 10/25 SSO deploy.
- Self-reported: **Medium** — matches AI directionally; no major gap, but note zero buffer means any further slip breaks HND-610 too.