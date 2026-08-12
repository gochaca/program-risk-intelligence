# Weekly Program Status Report — Team-Level Detail

## 1. Health Snapshot
**On track: 6 | At risk: 1 | Blocked: 3 | Total: 10**

## 2. Cross-Source Patterns (Act on These First)

### 🔴 Shared Dependency: CCPA Legal Copy Bottleneck
**Tickets:** CRH-4 (blocked), CRH-2 (on track), CRH-3 (on track)
All three CCPA Regulatory Website Updates workstreams depend on the same legal team deliverable (CCPA copy). Dealer Systems (CRH-4) is explicitly blocked with no copy delivered. Mobile (CRH-3) and Web Platform (CRH-2) report completion, but it's unclear whether the copy they used is final/legal-approved or a placeholder that will need rework.
**Action:** Escalate directly to legal today to unblock CRH-4 before the Aug 14 due date. Simultaneously confirm with Web Platform whether their implemented copy is the final legal-approved version — don't let two "on track" tickets mask a single point of failure on the critical path.

### 🔴 Systemic Theme: Unowned Escalations Across Teams
**Tickets:** CRH-9 (blocked), CRH-5 (blocked), CRH-4 (blocked)
Three unrelated initiatives are stalled for the same structural reason: no one is actively driving the blocking party to respond. CRH-9 has two unanswered requests, CRH-5 is stuck on a traveling VP with no delegate, CRH-4 is waiting on legal with no one pushing urgency.
**Action:** This isn't three isolated blockers — it's a missing escalation process. Establish approval delegates for traveling execs and SLAs for legal/vendor response times now, rather than chasing each ticket individually.

### 🟡 Dependency Chain: Partner/Cross-Team Response Slips
**Tickets:** CRH-10 (at risk), CRH-11 (on track)
Both tickets slipped their due dates (to Aug 14–15) while waiting on another party to respond — Signal team's agreement on CRH-10, partner details on CRH-11. Individually manageable, but the clustering suggests a broader response-time problem.
**Action:** Review whether partner/cross-team SLAs need tightening to prevent this becoming a recurring pattern.

---

## 3. Ticket Detail by Team

### enterprise-iam
**CRH-11 — Partner Integration Incident Response** | Due: 2026-08-14
- **AI: on_track** (signal: none) — Prior blocker resolved; partner responded with needed details, due date moved to Aug 14, no further blockers anticipated.
- Self-reported: Low (matches AI).

### cdp-team
**CRH-10 — Consent Signal Integration** | Due: 2026-08-08 (slipped to Aug 15)
- **AI: at_risk** (signal: none) — Original due date already passed as of report date; new target is Aug 15. Work is progressing smoothly and Signal team agreed to the extension, but the miss itself elevates risk.
- ⚠️ **Gap:** Self-reported risk is **Low**, but AI flags **at_risk** due to the missed original date. Worth a quick check-in to confirm the new Aug 15 date is firm.

### brightpath-qa-services
**CRH-9 — Dealer Portal Release Calendar** | Due: 2026-08-07 (past due)
- **AI: blocked** (signal: unowned_escalation) — Due date passed 5 days ago; two requests (initial + follow-up) have gone unanswered with no owner engaging.
- Self-reported risk: none provided. **No response from the team at all — this needs direct outreach in the next hour.**

### regional-marketing-na
**CRH-8 — Competitor-Response Campaign** | Due: 2026-08-14
- **AI: on_track** (signal: none) — Received the responses they were waiting on; proceeding on schedule, due date two days out.
- Self-reported: Low (matches AI).

### acme-cloud-infrastructure
**CRH-7 — Data Center Cloud Migration - Security Review** | Due: 2026-08-14
- **AI: on_track** (signal: none) — Migration and validation complete, finished four days ahead of schedule.
- Self-reported: Low (matches AI).

**CRH-6 — Data Center Cloud Migration - Cutover** | Due: 2026-08-21
- **AI: on_track** (signal: none) — Cutover planned and on schedule, due date over a week out.
- Self-reported: Low (matches AI).

### data-privacy-legal-ops
**CRH-5 — Consent Taxonomy Review** | Due: 2026-08-14
- **AI: blocked** (signal: unowned_escalation) — Review work is done, but sign-off is stuck with a traveling VP not returning until Monday (after due date), and no delegate is empowered to approve.
- Self-reported risk: none provided. **Needs an owner to secure a delegate approver before Monday's return date passes the deadline.**

### dealer-systems-integration
**CRH-4 — CCPA Regulatory Website Updates - Dealer Systems** | Due: 2026-08-14
- **AI: blocked** (signal: unowned_escalation) — Blocked pending CCPA copy from legal; due date is 2 days away; no one appears to be actively pushing legal to deliver despite urgency being flagged.
- Self-reported: High (matches AI direction — team itself flagged urgency). See cross-source pattern above; this is the critical-path item for CCPA.

### mobile-app-engineering
**CRH-3 — CCPA Regulatory Website Updates - Mobile** | Due: 2026-08-14
- **AI: on_track** (signal: none) — Task completed ahead of schedule.
- Self-reported: Low (matches AI). **Verify copy used is final/legal-approved** (see pattern above).

### web-platform-team
**CRH-2 — CCPA Regulatory Website Updates - Web Platform** | Due: 2026-08-14
- **AI: on_track** (signal: none) — Copy implemented across all pages, no blockers, expected done Wednesday (just after due date).
- Self-reported: Low (matches AI). **Confirm copy source with legal before treating this as fully closed** (see pattern above).