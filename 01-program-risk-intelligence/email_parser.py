"""Extract a structured status update from a freeform email reply.

Real people don't reliably fill in a template, so instead of regex-splitting
on expected headers, this uses the same forced-tool-use pattern as classify.py
to have Claude read the reply and pull out the update text and the sender's
self-reported risk -- being honest when the sender didn't actually state one.
"""
from __future__ import annotations

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

PARSE_SYSTEM_PROMPT = """You are extracting a structured status update from a \
freeform email reply. The sender was asked for current status and any risk to a \
due date, but people don't always answer in a fixed format -- read the whole \
reply and extract what's actually there.

- update_text: a neutral, complete restatement of what the sender said about \
status/progress, in their own substance (not just a copy-paste, but don't lose \
detail either).
- self_reported_risk: Low, Medium, or High if the sender stated or clearly \
implied one, otherwise null -- do not invent a rating they didn't give.
- self_reported_rationale: the sender's own reasoning for that risk level, if \
given, otherwise null."""

PARSE_TOOL = {
    "name": "extract_status_update",
    "description": "Record the structured status update extracted from an email reply.",
    "input_schema": {
        "type": "object",
        "properties": {
            "update_text": {"type": "string"},
            "self_reported_risk": {"type": ["string", "null"], "enum": ["Low", "Medium", "High", None]},
            "self_reported_rationale": {"type": ["string", "null"]},
        },
        "required": ["update_text", "self_reported_risk", "self_reported_rationale"],
    },
}


def parse_reply_to_update(reply_body: str, client: Anthropic | None = None) -> dict:
    client = client or Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=PARSE_SYSTEM_PROMPT,
        tools=[PARSE_TOOL],
        tool_choice={"type": "tool", "name": "extract_status_update"},
        messages=[{"role": "user", "content": reply_body}],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    return tool_use.input
