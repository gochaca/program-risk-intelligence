"""Gmail access: creating draft status-request emails. Draft-only, by design --
this never calls Gmail's send endpoint. A human reviews and sends every email
this tool ever produces.

- MockGmailClient: writes drafts to data/mock_drafts.json and prints them. No
  network calls, safe to run any time.
- RealGmailClient: Gmail API (google-api-python-client), OAuth. Requires a
  Google Cloud project with the Gmail API enabled and an OAuth client
  credentials.json (see README "Connecting real accounts"). Uses
  users().drafts().create() -- there is no code path to users().messages().send()
  anywhere in this file.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TOKEN_PATH = Path(__file__).parent / ".gmail_token.json"
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",  # needed for find_reply()
]


class MockGmailClient:
    def __init__(self, log_path: Path | None = None, simulated_replies: dict[str, str] | None = None):
        self.log_path = log_path or DATA_DIR / "mock_drafts.json"
        self.simulated_replies = simulated_replies or {}

    def create_draft(self, to: str, subject: str, body: str) -> dict:
        log = []
        if self.log_path.exists():
            log = json.loads(self.log_path.read_text())
        draft = {
            "to": to,
            "subject": subject,
            "body": body,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        log.append(draft)
        self.log_path.write_text(json.dumps(log, indent=2))
        print(f"[MockGmailClient] draft logged -> {to} | {subject}")
        return draft

    def find_reply(self, jira_ticket: str, since_date: str) -> str | None:
        """No live inbox in mock mode -- looks up whatever was passed in at
        construction, if anything. weekly_cycle.py's `simulate` phase doesn't
        use this at all; it has its own explicit mock_inbox handling instead."""
        return self.simulated_replies.get(jira_ticket)


class RealGmailClient:
    """Gmail API. Draft creation only -- there is no code path to
    users().messages().send() anywhere in this file, deliberately. Also reads
    (gmail.readonly scope) to find replies, since knowing who's responded is
    read-only.

    Setup: create a Google Cloud OAuth client (Desktop app type), download it
    as credentials.json into this directory, then run this module directly
    once (`python3 gmail_client.py`) to complete the one-time browser OAuth
    consent flow; it caches a token in .gmail_token.json (git-ignored) for
    subsequent runs.
    """

    def __init__(self):
        # Lazy imports -- only needed in live mode, keeps requirements.txt
        # light for anyone just running the mock/classification pipeline.
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(Path(__file__).parent / "credentials.json"), GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)

    def create_draft(self, to: str, subject: str, body: str) -> dict:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return self.service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()

    def find_reply(self, jira_ticket: str, since_date: str) -> str | None:
        """Search the inbox for a reply mentioning this ticket, received on
        or after since_date (YYYY-MM-DD), from someone other than the
        account owner. Returns the first match's plain-text body, or None if
        nothing's arrived yet.

        The ticket ID is quoted in the query -- Gmail's search parser treats
        a bare hyphen as a NOT operator, which would silently break a search
        for e.g. "CRH-2" (interpreted as "CRH" and not "2") if left unquoted.
        """
        since_gmail_fmt = since_date.replace("-", "/")
        query = f'subject:"{jira_ticket}" after:{since_gmail_fmt} -from:me'
        resp = self.service.users().messages().list(userId="me", q=query, maxResults=1).execute()
        messages = resp.get("messages", [])
        if not messages:
            return None
        full_message = self.service.users().messages().get(userId="me", id=messages[0]["id"], format="full").execute()
        return _extract_plain_text(full_message["payload"]) or None


def _extract_plain_text(payload: dict) -> str:
    """Walk a Gmail message payload (which may be multipart) for the
    text/plain body, base64url-decoded."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        text = _extract_plain_text(part)
        if text:
            return text
    return ""


def get_gmail_client():
    """Real client if credentials.json is present, mock otherwise."""
    if (Path(__file__).parent / "credentials.json").exists():
        return RealGmailClient()
    return MockGmailClient()


if __name__ == "__main__":
    # Run this directly, once, to do the one-time OAuth consent flow.
    get_gmail_client()
