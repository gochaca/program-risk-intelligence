# Weekly Program Status Report — Team-Level Detail

## 1. Health Snapshot

**On track: 1 | At risk: 3 | Blocked: 6 | Total: 10**

## 2. Cross-Source Patterns (Act on These First)

### 🔴 Pattern A: Program-wide non-response wave — 8 tickets, likely a common root cause
**Tickets:** CRH-11, CRH-10, CRH-9, CRH-8, CRH-7, CRH-5, CRH-4, CRH-3
Eight unrelated teams (IAM, CDP, QA services, regional marketing, cloud infra, legal ops, dealer systems, mobile engineering) all report the exact same symptom this week — two unanswered requests (initial + follow-up), no response. This is too uniform to be eight independent people problems.
**Action:** Before escalating each ticket individually, check for a common-cause disruption this week (broken escalation/notification channel, tool outage, company-wide event/offsite). Fix the root cause once instead of chasing 8 teams separately.

### 🟠 Pattern B: CCPA initiative — "on track" status is masking real risk
**Tickets:** CRH-4 (Dealer Systems), CRH-3 (Mobile), CRH-2 (Web Platform)
Same initiative (CCPA Regulatory Website Updates). Web Platform (CRH-2) is on track and unblocked, but Dealer Systems and Mobile — both required for the same Aug 14 deadline — have gone silent on two requests.
**Action:** Don't let CRH-2's green status create false comfort on the initiative overall. Escalate directly to Dealer Systems and Mobile leads now; they are the actual critical path.

### 🟠 Pattern C: Data Center Cloud Migration — one upstream blocker likely explains both statuses
**Tickets:** CRH-7 (Security Review, blocked), CRH-6 (Cutover, at risk)
Same team (acme-cloud-infrastructure), sequential phases of one migration. Cutover depends on Security Review sign-off, and both are stalled by the same non-response pattern.
**Action:** Identify and unblock whoever is not responding on CRH-7 first — this likely resolves CRH-6's "quiet" status too, since Cutover can't proceed without it.

### 🟡 Pattern D: acme-cloud-infrastructure — possible overload, two dependent deadlines in flight
**Tickets:** CRH-7 (due Aug 14), CRH-6 (due Aug 21)
Same team running two sequential, dependent phases in parallel, both stalled simultaneously.
**Action:** Check this team's capacity/resourcing. If Security Review slips, Cutover's Aug 21 date is next to fall — consider re-sequencing or adding resourcing now rather than waiting for the slip.

---

## 3. Ticket Detail by Team

### enterprise-iam
**CRH-11** — Partner Integration Incident Response — Due **2026-08-07 (today)**
- AI: **Blocked** (unowned_escalation) — Two requests (initial + follow-up) unanswered; due date is today with no progress.
- Self-reported risk: none provided.

### cdp-team
**CRH-10** — Consent Signal Integration — Due **2026-08-08**
- AI: **Blocked** (unowned_escalation) — Two requests unanswered, due tomorrow, no owner engaged.
- Self-reported risk: none provided.

### brightpath-qa-services
**CRH-9** — Dealer Portal Release Calendar — Due **2026-08-07 (today)**
- AI: **Blocked** (unowned_escalation) — Unresponsive to two outreach attempts, due date today, no engagement.
- Self-reported risk: none provided.

### regional-marketing-na
**CRH-8** — Competitor-Response Campaign — Due **2026-08-14**
- AI: **Blocked** (unowned_escalation) — Two unanswered requests, due date one week out, no owner has picked up escalation.
- Self-reported risk: none provided.

### acme-cloud-infrastructure
**CRH-7** — Data Center Cloud Migration - Security Review — Due **2026-08-14**
- AI: **Blocked** (unowned_escalation) — Two unanswered requests, due date one week away, no response received.
- Self-reported risk: none provided.
- *See Pattern C/D — likely upstream cause for CRH-6.*

**CRH-6** — Data Center Cloud Migration - Cutover — Due **2026-08-21**
- AI: **At Risk** (quiet) — Team silent on two requests; due date two weeks out, credible threat if silence continues.
- Self-reported risk: none provided.
- *See Pattern C/D — likely downstream of CRH-7's blocker.*

### data-privacy-legal-ops
**CRH-5** — Consent Taxonomy Review — Due **2026-08-14**
- AI: **Blocked** (unowned_escalation) — Two unanswered requests, due date one week away, no decision-maker responding.
- Self-reported risk: none provided.

### dealer-systems-integration
**CRH-4** — CCPA Regulatory Website Updates - Dealer Systems — Due **2026-08-14**
- AI: **At Risk** (quiet) — No response to two outreach attempts; due date one week away, silence threatens deadline.
- Self-reported risk: none provided.
- *See Pattern B — part of CCPA initiative critical path.*

### mobile-app-engineering
**CRH-3** — CCPA Regulatory Website Updates - Mobile — Due **2026-08-14**
- AI: **At Risk** (quiet) — No response to either request this week; due date one week away, no visible progress.
- Self-reported risk: none provided.
- *See Pattern B — part of CCPA initiative critical path.*

### web-platform-team
**CRH-2** — CCPA Regulatory Website Updates - Web Platform — Due **2026-08-14**
- AI: **On Track** (none) — Copy implemented across all pages, no blockers, expected done by Wednesday.
- Self-reported risk: **Low** — "No blockers on their end." *(Matches AI classification — no gap.)*
- *See Pattern B — this team's green status should not be read as the initiative being on track overall.*