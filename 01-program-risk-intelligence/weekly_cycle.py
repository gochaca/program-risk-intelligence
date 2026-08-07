"""Orchestrates the weekly cadence: Wednesday first request -> Friday morning
follow-up (non-responders only, determined by actually checking the inbox for
replies in live mode) -> collect replies -> run the existing
classify/detect_patterns/generate_report pipeline -> write the AI's
classification back to Jira as a comment.

Three phases, meant to run as three separate scheduled invocations in
production (`first-request` Wed morning, `followup` Fri morning, `report` Fri
once replies are in) -- see README "Running this for real." `simulate` runs
all three back-to-back against the mock inbox, for testing the whole loop
locally today.

`first-request`/`followup`/`report` use get_jira_client()/get_gmail_client(),
which pick Real vs Mock based on whether live credentials are configured.
`simulate` is the exception: it ALWAYS uses MockJiraClient/MockGmailClient
explicitly, regardless of what's configured in the environment, because its
entire purpose is a safe local test -- it must never write to a real Jira
project or Gmail account just because credentials happen to be set.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from anthropic import Anthropic

import classify
import detect_patterns
import generate_report
from email_parser import parse_reply_to_update
from email_templates import first_request_email, followup_email
from gmail_client import MockGmailClient, get_gmail_client
from jira_client import MockJiraClient, get_jira_client

DATA_DIR = Path(__file__).parent / "data"
STATE_PATH = DATA_DIR / "cycle_state.json"
SIMULATED_REPORT_DATE = "2025-10-31"  # a Friday; keeps simulate mode's dates coherent with the mock roster's 2025 due dates


def _load_mock_inbox() -> dict[str, dict]:
    """jira_ticket -> reply record, for simulate mode only."""
    inbox = json.loads((DATA_DIR / "mock_inbox.json").read_text())["replies"]
    return {r["jira_ticket"]: r for r in inbox}


def _save_state(awaiting_response: list[str], sent_at: str | None = None) -> None:
    if sent_at is None:
        sent_at = _load_state().get("sent_at")
    STATE_PATH.write_text(json.dumps({"awaiting_response": awaiting_response, "sent_at": sent_at}, indent=2))


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"awaiting_response": [], "sent_at": None}
    return json.loads(STATE_PATH.read_text())


def send_first_requests(jira_client, gmail_client) -> list[dict]:
    roster = jira_client.get_roster()
    skipped = [item for item in roster if not item.get("contact_email")]
    roster = [item for item in roster if item.get("contact_email")]

    for item in roster:
        email = first_request_email(item)
        gmail_client.create_draft(**email)

    for item in skipped:
        print(f"Skipping {item['jira_ticket']} ({item['initiative']!r}) -- no assignee/contact email to send to.")

    _save_state([item["jira_ticket"] for item in roster], sent_at=date.today().isoformat())
    print(f"Drafted {len(roster)} first-request emails ({len(skipped)} skipped, no contact).")
    return roster


def send_followups(jira_client, gmail_client, mock_inbox: dict[str, dict] | None = None) -> list[str]:
    """Sends follow-ups only to tickets still marked awaiting_response.

    In simulate mode, mock_inbox tells us who already replied to the first
    request so we know who to skip. In live mode, checks the real inbox via
    gmail_client.find_reply() for each awaiting ticket, searching since the
    first request was sent (tracked in cycle_state.json) -- anyone who's
    already replied gets dropped from state instead of getting a redundant
    follow-up.
    """
    roster_by_ticket = {item["jira_ticket"]: item for item in jira_client.get_roster()}
    state = _load_state()
    awaiting = state["awaiting_response"]
    sent_at = state.get("sent_at") or date.today().isoformat()

    if mock_inbox is not None:
        awaiting = [t for t in awaiting if mock_inbox.get(t, {}).get("replied_after") != "first_request"]
    else:
        still_awaiting = []
        for ticket in awaiting:
            if gmail_client.find_reply(ticket, since_date=sent_at):
                print(f"{ticket}: reply already received, skipping follow-up.")
            else:
                still_awaiting.append(ticket)
        awaiting = still_awaiting

    for ticket in awaiting:
        email = followup_email(roster_by_ticket[ticket])
        gmail_client.create_draft(**email)

    _save_state(awaiting, sent_at=sent_at)
    print(f"Drafted {len(awaiting)} follow-up emails (sent only to non-responders).")
    return awaiting


def collect_responses(
    jira_client,
    gmail_client=None,
    mock_inbox: dict[str, dict] | None = None,
    client: Anthropic | None = None,
    report_date: str | None = None,
    since_date: str | None = None,
) -> list[dict]:
    """Builds classify.py-shaped update records from whatever replies came in.

    A ticket with no reply at all becomes an explicit "no response" record --
    silence is data, not a gap, consistent with the 'quiet' signal already in
    the rubric (see README).

    report_date defaults to today, for live use. Simulate mode passes an
    explicit date instead -- the mock roster's due dates are fixed 2025
    dates, and stamping them with the real today would put weeks or months
    between "report date" and "due date" for no reason, confusing the
    model's own reasoning about how much runway is left.

    In live mode (mock_inbox=None), looks up each ticket's reply via
    gmail_client.find_reply(), searching since_date onward (defaults to
    when the first request was sent, per cycle_state.json).

    Skips any roster item with no contact_email, matching
    send_first_requests()'s skip -- a ticket we never actually asked for a
    status update on shouldn't get "no response" classified against it.
    """
    client = client or Anthropic()
    roster = [item for item in jira_client.get_roster() if item.get("contact_email")]
    today = report_date or date.today().isoformat()
    since = since_date or _load_state().get("sent_at") or today
    updates = []

    for item in roster:
        if mock_inbox is not None:
            reply = mock_inbox.get(item["jira_ticket"])
            reply_body = reply["body"] if reply else None
        elif gmail_client is not None:
            reply_body = gmail_client.find_reply(item["jira_ticket"], since_date=since)
        else:
            reply_body = None

        if reply_body:
            parsed = parse_reply_to_update(reply_body, client=client)
        else:
            parsed = {
                "update_text": "No response to two requests this week (first request and follow-up).",
                "self_reported_risk": None,
                "self_reported_rationale": None,
            }

        updates.append(
            {
                "team": item["team"],
                "team_type": item["team_type"],
                "jira_ticket": item["jira_ticket"],
                "initiative": item["initiative"],
                "category": item["category"],
                "due_date": item["due_date"],
                "report_date": today,
                **parsed,
            }
        )

    print(f"Collected {len(updates)} updates ({sum(1 for u in updates if u['self_reported_risk'] is None)} non-responses).")
    return updates


def post_classifications_to_jira(jira_client, classified_updates: list[dict]) -> None:
    for u in classified_updates:
        comment = (
            f"Program Risk Intelligence -- weekly classification ({u['report_date']})\n"
            f"Status: {u['ai_classification'].upper()} (signal: {u['ai_signal']})\n"
            f"{u['ai_reason']}"
        )
        jira_client.post_comment(u["jira_ticket"], comment)
    print(f"Posted {len(classified_updates)} classification comments to Jira.")


def run_report_phase(jira_client, gmail_client=None, mock_inbox: dict[str, dict] | None = None, report_date: str | None = None) -> None:
    client = Anthropic()
    updates = collect_responses(jira_client, gmail_client=gmail_client, mock_inbox=mock_inbox, client=client, report_date=report_date)

    classified = []
    for u in updates:
        result = classify.classify_update(u, client=client)
        classified.append({**u, "ai_classification": result["classification"], "ai_signal": result["signal"], "ai_reason": result["reason"]})

    patterns = detect_patterns.detect_patterns(classified, client=client)

    team_report = generate_report.generate_team_report(classified, patterns, client=client)
    exec_report = generate_report.generate_exec_report(classified, patterns, client=client)

    (DATA_DIR / "live_classified_updates.json").write_text(json.dumps({"updates": classified}, indent=2))
    (DATA_DIR / "live_patterns.json").write_text(json.dumps({"patterns": patterns}, indent=2))
    (DATA_DIR / "live_team_report.md").write_text(team_report)
    (DATA_DIR / "live_exec_report.md").write_text(exec_report)

    post_classifications_to_jira(jira_client, classified)

    print("\nWrote data/live_classified_updates.json, live_patterns.json, live_team_report.md, live_exec_report.md")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase",
        choices=["first-request", "followup", "report", "simulate"],
        help="Which phase to run, or 'simulate' to run the whole week against the mock inbox.",
    )
    args = parser.parse_args()

    if args.phase == "simulate":
        # Always mock, regardless of configured credentials -- simulate's
        # entire purpose is a safe local test. It must never touch a real
        # Jira project or Gmail account even if live credentials are set.
        jira_client = MockJiraClient()
        gmail_client = MockGmailClient()
        mock_inbox = _load_mock_inbox()
        print("=== Wednesday: first requests ===")
        send_first_requests(jira_client, gmail_client)
        print("\n=== Friday morning: follow-ups (non-responders only) ===")
        send_followups(jira_client, gmail_client, mock_inbox=mock_inbox)
        print("\n=== Friday: collect, classify, detect patterns, report, post to Jira ===")
        run_report_phase(jira_client, mock_inbox=mock_inbox, report_date=SIMULATED_REPORT_DATE)
        return

    jira_client = get_jira_client()
    gmail_client = get_gmail_client()

    if args.phase == "first-request":
        send_first_requests(jira_client, gmail_client)
    elif args.phase == "followup":
        send_followups(jira_client, gmail_client)
    elif args.phase == "report":
        run_report_phase(jira_client, gmail_client=gmail_client)


if __name__ == "__main__":
    main()
