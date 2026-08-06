# Weekly Program Status — Team-Level Detail

## Health Snapshot
**On Track: 6 | At Risk: 7 | Blocked: 4 | Total: 17**

---

## Cross-Source Patterns (Act on These First)

### 1. BrightPath vendor prioritization is blocking dealer-facing CCPA copy
**Tickets:** HND-146c, HND-520
BrightPath has explicitly paused the dealer portal release calendar request (pending since 10/15) to handle a Honda-escalated firmware defect, with no ETA. This isn't a lost request — it's a deliberate deprioritization.
**Action:** Escalate directly to BrightPath leadership today; don't wait for a reply. Build a fallback plan for dealer-site CCPA copy in case BrightPath doesn't unpause before 10/31.

### 2. HND-88 will miss its 10/25 due date — the blocker is already confirmed delayed
**Tickets:** HND-88, HND-89
CDP Team is waiting on Legal Ops to confirm consent taxonomy (due 10/25). Legal Ops has already said taxonomy review is pushed to "next week" due to competing CCPA and EU DSAR work.
**Action:** Reset HND-88's due date now — the current date is not achievable. Decide whether EU DSAR work or CCPA copy should yield to unblock taxonomy review sooner.

### 3. CCPA website update is one initiative with three single points of failure, all hitting 10/31
**Tickets:** HND-146, HND-146b, HND-146c, HND-201
Legal's copy is done, but Mobile is blocked until 10/25 (security patch train), Dealer Systems is blocked on BrightPath, and Web Platform's status is unreported.
**Action:** Track as one consolidated risk, not four tickets. Get a status check from Web Platform immediately — it's the only team without a stated blocker or start confirmation.

### 4. IAM has zero buffer left on SSO cert renewal
**Tickets:** HND-610, HND-611
Two engineers were pulled off the on-track SSO renewal to handle an unplanned partner integration outage. Deploy is "likely still fine" for 10/25 but with no slack if the incident drags on.
**Action:** Check in with IAM before the 10/25 deploy window; consider temporary resourcing support rather than assuming this holds.

### 5. Program-wide pattern: unplanned/executive work is displacing planned commitments
**Tickets:** HND-146b, HND-520, HND-89, HND-611, HND-95
Five unrelated teams (Mobile, BrightPath, Legal, IAM, Marketing) all report planned work being bumped by emergencies or executive asks this week — same signal, different workstreams.
**Action:** Raise at the portfolio level. Review the intake/escalation process for "urgent" requests — this is compressing timelines simultaneously across regulatory, infrastructure, and marketing.

### 6. Acme Cloud Infrastructure is a single vendor-health issue, not three separate risks
**Tickets:** HND-310, HND-311, HND-700
Second rehearsal reschedule (staffing shortage), a missed status update on a security review due in a week, and an unanswered executive escalation about the slippage — all from the same vendor, same migration.
**Action:** Force a response from Acme leadership this week. Treat as one vendor-health escalation, not three independent tickets.

---

## Ticket Detail by Team

### Web Platform Team
**HND-146** — CCPA Regulatory Website Updates - October | Due 2025-10-31
- **AI: at_risk** (signal: none) — Legal copy just finalized/distributed; implementation across three teams just starting with only one week of runway.
- Reason: Tight timeline for validating implementation across multiple sites/teams poses credible risk.
- Self-reported: **Medium** (matches AI direction; no major gap, though self-report framed as tracking task rather than schedule risk).

### Mobile App Engineering
**HND-146b** — CCPA Regulatory Website Updates - October | Due 2025-10-31
- **AI: at_risk** (signal: competing_objectives) — Q4 security patch locked the release train through 10/25; CCPA work hasn't started, targeting 10/30 with one day of buffer.
- Reason: Any slippage in patch release or implementation threatens the deadline.
- Self-reported: **High** — team's own risk is *higher* than AI's at_risk call. **Gap: self-reported risk exceeds AI classification** — worth weighting toward the team's view here given they know the release train constraints firsthand.

**HND-150** — Q4 Security Patch Release | Due 2025-10-25
- **AI: on_track** (signal: none) — QA sign-off expected same day, release on schedule, no open blockers.
- Reason: No issues reported.
- Self-reported: **Low** (matches).

### Dealer Systems Integration
**HND-146c** — CCPA Regulatory Website Updates - October | Due 2025-10-31
- **AI: blocked** (signal: bottlenecked) — No response from BrightPath since 10/15 request (9+ days); fully stalled on external dependency with 7 days left.
- Reason: Cannot push CCPA copy live without vendor's release calendar confirmation.
- Self-reported: **Medium** — **Gap: team underrates this as Medium while AI calls it Blocked**; team is assuming BrightPath responds "early next week," but HND-520 confirms BrightPath has paused this indefinitely. Escalate now.

**HND-77** — Regional Dealer Onboarding - Batch 4 | Due 2025-10-22
- **AI: on_track** (signal: none) — Completed ahead of schedule, ticket closing.
- Reason: No outstanding risks or dependencies.
- Self-reported: **Low** (matches).

### Data Privacy & Legal Ops
**HND-201** — CCPA Regulatory Website Updates - October | Due 2025-10-20
- **AI: on_track** (signal: none) — Copy finalized/distributed on time; only passive monitoring remains.
- Reason: Deliverable complete.
- Self-reported: **Low** (matches).

**HND-89** — Consent Taxonomy Review | Due 2025-10-31
- **AI: at_risk** (signal: competing_objectives) — Review pushed to "next week" due to CCPA copy work and an unplanned EU DSAR audit request; less than a week of buffer remains.
- Reason: Competing unplanned work directly threatens on-time completion.
- Self-reported: **Low** — **Gap: team calls this Low risk to their own 10/31 date, but AI flags at_risk** given the delay is already confirmed and buffer is thin. This directly drives the HND-88 blocker (see Pattern #2).

### Acme Cloud Infrastructure (Vendor)
**HND-310** — Data Center Cloud Migration - Cutover | Due 2025-11-07
- **AI: at_risk** (signal: bottlenecked) — Second rehearsal reschedule in three weeks (now 11/03) due to Acme staffing shortage; only 4 days buffer before cutover.
- Reason: Pattern of slippage plus minimal slack threatens due date.
- Self-reported: **Medium** — **Gap: team remains confident ("still expect to hit 11/07") while AI flags the compounding delay pattern as understated risk.**

**HND-311** — Data Center Cloud Migration - Security Review | Due 2025-10-31
- **AI: at_risk** (signal: quiet) — No update this week; only a repeated "on track" from 10/17, with due date one week out.
- Reason: Lack of fresh information from vendor warrants follow-up.
- Self-reported: **Not submitted** — **Gap: no current self-assessment provided at all; last known status is stale.** Needs direct follow-up.

**HND-700** — Data Center Cloud Migration - Escalation | Due 2025-10-24
- **AI: blocked** (signal: unowned_escalation) — Escalation to Acme account exec and internal VP on 10/21 has drawn no response from either side as of today.
- Reason: Progress cannot move without executive intervention; escalation currently unowned.
- Self-reported: **High** (matches AI severity direction — no gap, but confirms urgency).

### Regional Marketing - NA
**HND-402** — Holiday Campaign Creative | Due 2025-11-14
- **AI: on_track** (signal: none) — In final legal review, standard step, no blockers, ~3 weeks remaining.
- Reason: Nothing suggests threat to deadline.
- Self-reported: **Low** (matches).

**HND-95** — Competitor-Response Campaign (Unplanned) | Due 2025-10-31
- **AI: at_risk** (signal: competing_objectives) — New CMO-driven campaign inserted ahead of HND-402 holiday work; sequencing not finalized with one week to go.
- Reason: Creates real risk to HND-402's timeline despite team confidence.
- Self-reported: **Medium** — **Gap: team is confident it can deliver both, but AI flags risk given sequencing is still unresolved.**

### Regional Marketing - EMEA
**HND-403** — Holiday Campaign Creative - Localization | Due 2025-11-14
- **AI: on_track** (signal: none) — Translation issue affects only 3 of 12 markets, fix expected 10/28, over two weeks of buffer remain.
- Reason: Scoped, actively managed issue.
- Self-reported: **Low** (matches).

### BrightPath QA Services (Vendor)
**HND-520** — Dealer Portal Release Calendar | Due 2025-10-24
- **AI: blocked** (signal: competing_objectives) — Team has paused all other work, including this deliverable, to handle a Honda-escalated firmware defect; no ETA.
- Reason: Progress fully stopped; won't resume until the emergency resolves.
- Self-reported: **High** (matches AI severity — confirms firmware defect is taking full priority).

### Customer Data Platform (CDP) Team
**HND-88** — Consent Signal Integration | Due 2025-10-25
- **AI: blocked** (signal: bottlenecked) — Same status as last week; waiting on Legal Ops taxonomy confirmation; due date is tomorrow with no forward movement possible.
- Reason: No indication of escalation to unblock Legal.
- Self-reported: **Medium** — **Gap: team frames this as "not our problem" (dependency is Legal's), but AI flags Blocked given the due date is essentially at hand with zero escalation path visible.**

### Enterprise Identity & Access Management
**HND-610** — SSO Certificate Renewal | Due 2025-10-26
- **AI: on_track** (signal: none) — Staging test passed 10/22, production deploy scheduled 10/25, one day ahead of due date.
- Reason: No dependencies or blockers noted.
- Self-reported: **Low** (matches).

**HND-611** — Partner Integration Incident Response | Due 2025-10-24
- **AI: at_risk** (signal: competing_objectives) — Unplanned production incident pulled two engineers off SSO work; 10/25 deploy now has zero buffer.
- Reason: Further disruption could push SSO past deadline.
- Self-reported: **Medium** (roughly matches AI direction — "contained so far, but resourcing is thin" aligns with at_risk framing).