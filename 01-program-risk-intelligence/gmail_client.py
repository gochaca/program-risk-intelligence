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
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


class MockGmailClient:
    def __init__(self, log_path: Path | None = None):
        self.log_path = log_path or DATA_DIR / "mock_drafts.json"

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


class RealGmailClient:
    """Gmail API, drafts.compose scope only -- deliberately cannot send.

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


def get_gmail_client():
    """Real client if credentials.json is present, mock otherwise."""
    if (Path(__file__).parent / "credentials.json").exists():
        return RealGmailClient()
    return MockGmailClient()


if __name__ == "__main__":
    # Run this directly, once, to do the one-time OAuth consent flow.
    get_gmail_client()
