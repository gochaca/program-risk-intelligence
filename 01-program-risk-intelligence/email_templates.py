"""Email copy for the weekly status request cycle.

Two templates: the Wednesday first request, and the Friday-morning follow-up
sent only to teams that haven't replied yet. Plain text, no template engine --
these are short enough not to need one.
"""
from __future__ import annotations


def first_request_email(roster_item: dict) -> dict:
    subject = f"[Status request] {roster_item['initiative']} ({roster_item['jira_ticket']}) -- due {roster_item['due_date']}"
    body = f"""Hi {roster_item['contact_name']},

Quick status check for this week's program report on {roster_item['initiative']} ({roster_item['jira_ticket']}), due {roster_item['due_date']}.

Could you reply with:
- What's the current status?
- Any risk to the due date, and why?

Thanks -- this rolls up into Friday's program status report.
"""
    return {"to": roster_item["contact_email"], "subject": subject, "body": body}


def followup_email(roster_item: dict) -> dict:
    subject = f"[Second request] {roster_item['initiative']} ({roster_item['jira_ticket']}) -- due {roster_item['due_date']}"
    body = f"""Hi {roster_item['contact_name']},

Following up on my note earlier this week -- haven't heard back on {roster_item['initiative']} ({roster_item['jira_ticket']}), due {roster_item['due_date']}.

I need a quick status for this week's program report, going out this morning. If I don't hear back before then, I'll note this workstream as unresponsive this week and follow up directly.

Thanks.
"""
    return {"to": roster_item["contact_email"], "subject": subject, "body": body}
