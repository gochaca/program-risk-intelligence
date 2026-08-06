# Weekly Program Status Report — Team-Level Detail

## 1. Health Snapshot
**10 total tickets — 0 on track, 6 at risk, 4 blocked.**

Zero tickets are on track this week. Every single item needs attention.

---

## 2. Cross-Source Patterns (Act on These First)

**Pattern 1 — BrightPath is the shared root cause for two blocked/at-risk tickets**
- Tickets: `HND-146c`, `HND-520`
- Dealer Systems has been waiting since 10/15 for BrightPath to confirm its release calendar. BrightPath's own report confirms why: it's been fully consumed since Monday by an escalated Honda firmware defect, with **no ETA** to return to dealer portal work.
- **Action:** Escalate directly to BrightPath leadership (not the working contact) for a firm ETA or reprioritization commitment. The CCPA dealer-facing site update is blocked on this today, 10/31 — the deadline.

**Pattern 2 — Legal is a single point of failure across three regulatory initiatives**
- Tickets: `HND-89`, `HND-88`, `HND-146`
- Legal only just finalized CCPA copy (~10/22), compressing the Web Platform timeline (`HND-146`). Legal's own team (`HND-89`) slipped its consent taxonomy review because it got pulled onto CCPA copy work plus an unplanned DSAR audit. Meanwhile CDP (`HND-88`) is blocked past its 10/25 due date waiting on that same taxonomy confirmation from Legal.
- **Action:** Engage Legal's manager directly to sequence/prioritize their workload (taxonomy confirmation vs. CCPA copy). One team's overload is cascading into multiple missed or compressed deadlines.

**Pattern 3 — Program-wide pattern: unplanned emergencies are silently displacing committed work**
- Tickets: `HND-89`, `HND-95`, `HND-520`, `HND-611`
- Four unrelated teams (Legal Ops, Regional Marketing, BrightPath, Enterprise IAM) all report the same `competing_objectives` signal this week — DSAR audit, CMO-driven competitor campaign, Honda firmware escalation, and a partner integration prod incident, respectively, all bumping planned work.
- **Action:** Raise this at the portfolio level. Push for a formal intake/triage process for unplanned work so committed deadlines stop eroding week over week without visibility.

**Pattern 4 — Acme Cloud Infrastructure looks like a vendor-wide staffing shortfall, not two isolated issues**
- Tickets: `HND-310`, `HND-311`
- The cutover rehearsal has slipped twice in three weeks due to staffing shortages, and the same vendor has gone completely unresponsive on the security review due today.
- **Action:** Treat as one vendor capacity escalation. Request a resourcing plan or executive-level check-in with Acme before the 11/7 cutover — both symptoms trace to the same shortfall.

**Pattern 5 — All three CCPA website tickets share one root cause: late Legal sign-off**
- Tickets: `HND-146`, `HND-146b`, `HND-146c`
- Web Platform, Mobile, and Dealer Systems all trace their compressed/blocked timelines back to Legal's late copy delivery (~10/22), compounded by team-specific constraints (release train lock, BrightPath non-response).
- **Action:** Don't manage these as three separate at-risk items — recognize the systemic timeline compression and consider whether 10/31 needs a formal risk acceptance or extension given all three downstream teams are affected identically.

---

## 3. Ticket Detail by Team

### Web Platform Team
**`HND-146`** — CCPA Regulatory Website Updates - October — Due **2025-10-31**
- **AI: at_risk / bottlenecked** — Report date is the due date itself; website updates are only "starting this week" after Legal finalized copy late. No buffer remains.
- Self-reported risk: **Medium** (aligned with AI — no gap).

### Mobile App Engineering
**`HND-146b`** — CCPA Regulatory Website Updates - October — Due **2025-10-31**
- **AI: at_risk / bottlenecked** — Implementation stalled behind the Q4 security patch release train lock until 10/25; team is now targeting completion on the 30th with zero buffer before the deadline.
- Self-reported risk: **High** — ⚠️ **Gap:** team rates this higher (High) than the AI classification (at_risk). Their own account of zero buffer supports the more severe self-assessment; treat as urgent.

### Dealer Systems Integration
**`HND-146c`** — CCPA Regulatory Website Updates - October — Due **2025-10-31**
- **AI: blocked / bottlenecked** — Request sent to BrightPath on 10/15 with no response since; CCPA copy cannot be pushed without BrightPath's release calendar confirmation.
- Self-reported risk: **Medium** — ⚠️ **Gap:** team rates this as Medium ("hopeful" pending BrightPath response), but AI classifies as fully **blocked** given zero response and the deadline is today. Escalate per Pattern 1 above.

### Data Privacy & Legal Ops
**`HND-89`** — Consent Taxonomy Review — Due **2025-10-31**
- **AI: at_risk / competing_objectives** — Team pulled onto CCPA copy work and an unplanned DSAR audit; taxonomy review has slipped to next week — but today is the actual due date.
- Self-reported risk: **Low** — ⚠️ **Gap:** team's rationale assumes buffer to the 31st, but the 31st **is** today. This self-assessment is out of date; the risk is materially higher than reported.

### Acme Cloud Infrastructure (vendor)
**`HND-310`** — Data Center Cloud Migration - Cutover — Due **2025-11-07**
- **AI: at_risk / bottlenecked** — Cutover rehearsal has slipped twice in three weeks (10/29 → 11/3) due to staffing shortages, leaving only 4 days of buffer before the 11/7 cutover.
- Self-reported risk: **Medium** (aligned with AI — no gap, though vendor's confidence in the 11/7 date is not well substantiated).

**`HND-311`** — Data Center Cloud Migration - Security Review — Due **2025-10-31**
- **AI: blocked / unowned_escalation** — No response to two outreach attempts this week; due date is today with no forward movement possible.
- Self-reported risk: **None provided** — note the absence itself: no risk rating was submitted for a ticket that is blocked on its due date.

### Regional Marketing - NA
**`HND-95`** — Competitor-Response Campaign (Unplanned) — Due **2025-10-31**
- **AI: at_risk / competing_objectives** — CMO's office injected an unplanned campaign that must be sequenced against the holiday campaign; sequencing plan not yet locked in for a deadline that is today.
- Self-reported risk: **Medium** (aligned with AI — no gap).

### BrightPath QA Services (vendor)
**`HND-520`** — Dealer Portal Release Calendar — Due **2025-10-24** (already past due)
- **AI: blocked / competing_objectives** — Vendor fully consumed by an escalated Honda firmware defect since Monday; no ETA to resume dealer portal work; due date already passed.
- Self-reported risk: **High** (broadly consistent with AI's severity — both indicate a serious stall; no material gap).

### Customer Data Platform (CDP) Team
**`HND-88`** — Consent Signal Integration — Due **2025-10-25** (already past due)
- **AI: blocked / unowned_escalation** — Status unchanged from last week; still waiting on Legal to confirm consent taxonomy, with no forward movement and no evidence of escalation to force Legal to act.
- Self-reported risk: **Medium** — ⚠️ **Gap:** team frames this as a manageable dependency with rising "nervousness," but the due date has already passed with zero movement — AI's **blocked** classification is the more accurate read. Needs active escalation, not passive waiting.

### Enterprise Identity & Access Management
**`HND-611`** — Partner Integration Incident Response — Due **2025-10-24** (already past due)
- **AI: at_risk / competing_objectives** — Unplanned partner integration emergency pulled two people off SSO cert renewal work; deploy is claimed to still land on time but with zero buffer, against a due date that has already passed.
- Self-reported risk: **Medium** (aligned with AI — no gap).