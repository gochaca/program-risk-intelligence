"""Two-altitude status report generation, via the Claude API.

Drafts the same weekly status report at two altitudes from the same
underlying data: a team-level detail report (every ticket, every signal,
grounded in the raw update text) and an executive summary (health snapshot,
cross-source patterns first, only the tickets that need a decision).

The two altitudes are NOT just "ask the model to summarize shorter" -- the
exec payload structurally strips fields before the model ever sees them.
See README.md ("Two-altitude reporting") for why.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

GROUNDING_RULE = (
    "Only use the facts given in the data below. Do not invent teams, tickets, "
    "numbers, or details not present in the data."
)

TEAM_SYSTEM_PROMPT = f"""You are drafting the team-level detail section of a weekly \
program status report for a program lead who needs to act on it, not just read it. \
{GROUNDING_RULE}

Structure:
1. One-line health snapshot -- quote the on_track / at_risk / blocked / total \
counts exactly as given in `health_snapshot`. Do not recount from the ticket list.
2. Cross-source patterns section first -- these are the highest-leverage findings, \
list each with the tickets involved and the recommended action.
3. Then every ticket, grouped by team, in this format: ticket ID, initiative, due \
date, AI classification and signal, the reason, and the team's own self-reported \
risk alongside it when it differs from the AI classification (call out the gap \
explicitly when it exists).

Use markdown. Be direct and specific -- this is read by someone who will act on it \
in the next hour, not a general audience."""

EXEC_SYSTEM_PROMPT = f"""You are drafting the executive-altitude section of a weekly \
program status report, for leadership who have a few minutes and need to know what \
requires their attention. {GROUNDING_RULE}

You have deliberately NOT been given the full list of on-track tickets, raw update \
text, or team self-reported risk ratings -- only the health snapshot counts, the \
tickets that are at_risk or blocked, and the cross-source patterns. Do not apologize \
for or mention this omission; it's intentional.

Structure:
1. One-line health snapshot -- quote the on_track / at_risk / blocked / total \
counts exactly as given in `health_snapshot`. Do not recompute or restate them \
differently anywhere else in the report.
2. Cross-source patterns first, in plain business language -- especially any \
systemic_theme, since that's a portfolio-level issue, not a single ticket problem. \
State the recommended action for each.
3. A short list of the at_risk/blocked tickets that aren't already covered by a \
pattern above, each as one line: what it is, why it's at risk, what's needed from \
leadership (if anything).

Keep it tight -- this should be readable in under two minutes. Use markdown."""


def _health_snapshot(classified_updates: list[dict]) -> dict:
    """Compute exact counts in code, not in the model's head.

    Both prompts are instructed to quote these numbers verbatim rather than
    recount from the ticket list -- a report leadership acts on can't have
    arithmetic the model got wrong while composing prose.
    """
    counts = {"on_track": 0, "at_risk": 0, "blocked": 0}
    for u in classified_updates:
        counts[u["ai_classification"]] += 1
    return {"total_tickets": len(classified_updates), **counts}


def build_exec_payload(classified_updates: list[dict], patterns: list[dict]) -> dict:
    """Strip the payload down to what an executive reader needs.

    Dropped entirely: update_text, self_reported_risk, self_reported_rationale
    (leadership needs the program's final call, not the raw team input or the
    back-and-forth that produced it), and every on_track ticket's detail (rolled
    up into a single count -- a clean ticket doesn't need a paragraph).
    """
    needs_attention = [u for u in classified_updates if u["ai_classification"] != "on_track"]

    return {
        "health_snapshot": _health_snapshot(classified_updates),
        "needs_attention": [
            {
                "jira_ticket": u["jira_ticket"],
                "team": u["team"],
                "initiative": u["initiative"],
                "due_date": u["due_date"],
                "ai_classification": u["ai_classification"],
                "ai_signal": u["ai_signal"],
                "ai_reason": u["ai_reason"],
            }
            for u in needs_attention
        ],
        "patterns": patterns,
    }


def build_team_payload(classified_updates: list[dict], patterns: list[dict]) -> dict:
    return {
        "health_snapshot": _health_snapshot(classified_updates),
        "updates": [{k: v for k, v in u.items() if not k.startswith("ground_truth")} for u in classified_updates],
        "patterns": patterns,
    }


def generate_team_report(classified_updates: list[dict], patterns: list[dict], client: Anthropic | None = None) -> str:
    client = client or Anthropic()
    payload = build_team_payload(classified_updates, patterns)
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=TEAM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, indent=2)}],
    )
    if response.stop_reason == "max_tokens":
        print("WARNING: team report was cut off by max_tokens -- output is incomplete.", file=sys.stderr)
    return "".join(block.text for block in response.content if block.type == "text")


def generate_exec_report(classified_updates: list[dict], patterns: list[dict], client: Anthropic | None = None) -> str:
    client = client or Anthropic()
    payload = build_exec_payload(classified_updates, patterns)
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=EXEC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, indent=2)}],
    )
    if response.stop_reason == "max_tokens":
        print("WARNING: exec report was cut off by max_tokens -- output is incomplete.", file=sys.stderr)
    return "".join(block.text for block in response.content if block.type == "text")


def main():
    project_dir = Path(__file__).parent
    classified_path = project_dir / "data" / "classified_updates.json"
    patterns_path = project_dir / "data" / "patterns.json"

    if not patterns_path.exists():
        print("data/patterns.json not found -- running detect_patterns.py first...\n")
        subprocess.run([sys.executable, str(project_dir / "detect_patterns.py")], check=True)
        print()

    classified = json.loads(classified_path.read_text())["updates"]
    patterns = json.loads(patterns_path.read_text())["patterns"]

    client = Anthropic()

    team_report = generate_team_report(classified, patterns, client=client)
    exec_report = generate_exec_report(classified, patterns, client=client)

    (project_dir / "data" / "team_report.md").write_text(team_report)
    (project_dir / "data" / "exec_report.md").write_text(exec_report)

    print("=" * 70)
    print("TEAM-LEVEL DETAIL REPORT")
    print("=" * 70)
    print(team_report)
    print()
    print("=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)
    print(exec_report)
    print()
    print("Wrote data/team_report.md and data/exec_report.md")


if __name__ == "__main__":
    main()
