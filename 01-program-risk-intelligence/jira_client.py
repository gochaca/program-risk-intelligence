"""Jira access: who to ask (the roster) and where the AI's classification gets
written back to (a comment on the ticket).

Two implementations of the same interface -- get_roster() and post_comment() --
so weekly_cycle.py doesn't change when a real Jira project gets connected:

- MockJiraClient: reads data/team_roster.json, logs comments locally to
  data/mock_jira_comments.json. No network calls, safe to run any time.
- RealJiraClient: Jira Cloud REST API v3 (requests + an API token). Validated
  against a real Jira Cloud test project (get_roster() and post_comment()
  both confirmed working end to end). Field mapping (which JQL finds "this
  week's open tickets," which custom field holds the initiative name) is
  still project-specific -- what's here matches one real project's schema,
  but expect to adjust JIRA_INITIATIVE_FIELD/JIRA_CATEGORY_FIELD/
  JIRA_TEAM_SOURCE for a different one.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


class MockJiraClient:
    def __init__(self, roster_path: Path | None = None, comment_log_path: Path | None = None):
        self.roster_path = roster_path or DATA_DIR / "team_roster.json"
        self.comment_log_path = comment_log_path or DATA_DIR / "mock_jira_comments.json"

    def get_roster(self) -> list[dict]:
        return json.loads(self.roster_path.read_text())["roster"]

    def post_comment(self, jira_ticket: str, comment_text: str) -> None:
        log = []
        if self.comment_log_path.exists():
            log = json.loads(self.comment_log_path.read_text())
        log.append(
            {
                "jira_ticket": jira_ticket,
                "comment": comment_text,
                "posted_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.comment_log_path.write_text(json.dumps(log, indent=2))
        print(f"[MockJiraClient] logged comment on {jira_ticket} -> {self.comment_log_path.name}")


class RealJiraClient:
    """Jira Cloud REST API v3. Requires JIRA_BASE_URL, JIRA_EMAIL,
    JIRA_API_TOKEN in the environment. JIRA_ROSTER_JQL selects which tickets
    count as "this week's open asks" -- e.g. a saved filter's JQL string.

    Team comes from a label or a component, not the project name -- for a
    single shared project (one per-org Jira project, many teams), the
    project name is the same for every ticket and useless as "team." Set
    JIRA_TEAM_SOURCE=label (default) or JIRA_TEAM_SOURCE=component.

    Field mapping note: this reads the standard 'assignee' and 'duedate'
    fields and expects the assignee to have a public emailAddress (Jira Cloud
    can hide this depending on org privacy settings -- if so, you'll need to
    resolve email via the /rest/api/3/user endpoint or maintain email
    separately). 'initiative'/'category' fall back to the summary/labels if
    no custom field is configured -- adjust JIRA_INITIATIVE_FIELD /
    JIRA_CATEGORY_FIELD if your project uses custom fields for these.
    """

    def __init__(self):
        import requests  # lazy import -- only needed in live mode

        self._requests = requests
        self.base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
        self.auth = (os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
        self.roster_jql = os.environ.get("JIRA_ROSTER_JQL", "resolution = Unresolved ORDER BY duedate ASC")
        self.initiative_field = os.environ.get("JIRA_INITIATIVE_FIELD", "summary")
        self.category_field = os.environ.get("JIRA_CATEGORY_FIELD")
        self.team_source = os.environ.get("JIRA_TEAM_SOURCE", "label")  # "label" or "component"

    def _team_from_fields(self, fields: dict) -> str:
        if self.team_source == "component":
            components = fields.get("components") or []
            return components[0]["name"] if components else "Unassigned Team"
        labels = fields.get("labels") or []
        return labels[0] if labels else "Unassigned Team"

    def get_roster(self) -> list[dict]:
        # /rest/api/3/search (GET) is deprecated (410 Gone) -- /rest/api/3/search/jql
        # (POST) is the current replacement.
        fields = ["summary", "assignee", "duedate", "labels", "components"]
        if self.category_field:
            fields.append(self.category_field)
        resp = self._requests.post(
            f"{self.base_url}/rest/api/3/search/jql",
            auth=self.auth,
            json={"jql": self.roster_jql, "fields": fields},
        )
        resp.raise_for_status()
        roster = []
        for issue in resp.json()["issues"]:
            fields = issue["fields"]
            assignee = fields.get("assignee") or {}
            roster.append(
                {
                    "team": self._team_from_fields(fields),
                    "team_type": "internal",
                    "jira_ticket": issue["key"],
                    "initiative": fields.get(self.initiative_field, fields.get("summary", "")),
                    "category": fields.get(self.category_field, "") if self.category_field else "",
                    "due_date": fields.get("duedate"),
                    "contact_name": assignee.get("displayName", "Unassigned"),
                    "contact_email": assignee.get("emailAddress"),
                }
            )
        return roster

    def post_comment(self, jira_ticket: str, comment_text: str) -> None:
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}],
            }
        }
        resp = self._requests.post(
            f"{self.base_url}/rest/api/3/issue/{jira_ticket}/comment",
            auth=self.auth,
            json=body,
        )
        resp.raise_for_status()

    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        labels: list[str] | None = None,
        due_date: str | None = None,
        assignee_account_id: str | None = None,
    ) -> str:
        """Creates an issue, returns its key (e.g. 'CRH-12')."""
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if labels:
            fields["labels"] = labels
        if due_date:
            fields["duedate"] = due_date
        if assignee_account_id:
            fields["assignee"] = {"id": assignee_account_id}
        resp = self._requests.post(
            f"{self.base_url}/rest/api/3/issue",
            auth=self.auth,
            json={"fields": fields},
        )
        resp.raise_for_status()
        return resp.json()["key"]


def get_jira_client():
    """Real client if JIRA_BASE_URL is configured, mock otherwise."""
    if os.environ.get("JIRA_BASE_URL"):
        return RealJiraClient()
    return MockJiraClient()
