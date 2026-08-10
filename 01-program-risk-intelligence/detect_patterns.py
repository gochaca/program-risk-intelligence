"""Cross-source pattern detection across a batch of classified status updates.

A single update can only tell you about itself. This looks at the whole
week's batch at once and surfaces things no single update would reveal:
the same vendor blocking two different teams, one team getting hit by
multiple competing priorities in the same week, a chain of tickets where
one team's delay is causing another's, or a signal (e.g. competing_objectives)
showing up often enough to be a program-level problem rather than an
isolated incident.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from classify import _strip_stray_tags

load_dotenv()

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

PATTERN_SYSTEM_PROMPT = """You are a program risk analyst reviewing a full week's \
worth of status updates from multiple teams and vendors on a large, multi-team \
enterprise program, each already classified as on_track / at_risk / blocked with \
a signal type and reason.

Your job is to find patterns that are only visible across multiple updates, not \
from reading any single one. Look specifically for:

- shared_dependency: Two or more updates from different teams point at the same \
root cause -- the same vendor, the same upstream team, the same decision -- even \
if they don't reference each other's ticket numbers directly.
- team_overload: A single team has multiple issues this week where the combination \
(not any one issue alone) suggests real strain -- e.g. an unplanned incident \
pulling resources off a separate on-track item for the same team.
- dependency_chain: One team's update explains why another team is stuck -- the \
blocker named in ticket A is the subject of ticket B.
- systemic_theme: The same signal type (e.g. competing_objectives) is showing up \
across enough unrelated tickets/teams that it points to a program-level problem \
(e.g. a pattern of emergencies displacing planned work), not a one-off.

Only report a pattern if it involves two or more distinct tickets and would change \
what a program lead does this week. Do not restate a single update's own risk --\
that's already been classified. List `tickets_involved` using the jira_ticket \
values provided."""

PATTERN_TOOL = {
    "name": "report_cross_source_patterns",
    "description": "Record the cross-source patterns found across this batch of status updates.",
    "input_schema": {
        "type": "object",
        "properties": {
            "patterns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pattern_type": {
                            "type": "string",
                            "enum": [
                                "shared_dependency",
                                "team_overload",
                                "dependency_chain",
                                "systemic_theme",
                            ],
                        },
                        "tickets_involved": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                        },
                        "description": {
                            "type": "string",
                            "description": "What the pattern is, in plain language.",
                        },
                        "why_it_matters": {
                            "type": "string",
                            "description": "What a program lead should do about it this week.",
                        },
                    },
                    "required": ["pattern_type", "tickets_involved", "description", "why_it_matters"],
                },
            }
        },
        "required": ["patterns"],
    },
}


def detect_patterns(classified_updates: list[dict], client: Anthropic | None = None) -> list[dict]:
    """Find cross-source patterns across a batch of already-classified updates.

    Each item in `classified_updates` is expected to carry ai_classification,
    ai_signal, and ai_reason (as written by classify.py). ground_truth_* fields
    are stripped before sending -- they exist only for evaluation.
    """
    client = client or Anthropic()

    batch_for_model = [
        {k: v for k, v in update.items() if not k.startswith("ground_truth")}
        for update in classified_updates
    ]

    # Forced tool-use occasionally returns a malformed response -- either
    # missing the "patterns" key entirely, or (seen once, 2026-08-10) present
    # but with plain strings instead of pattern objects as its items. Both
    # are transient API-side glitches, not prompt problems. One retry has
    # always been enough; if it fails twice in a row that's a real error.
    last_error = None
    for attempt in range(2):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=PATTERN_SYSTEM_PROMPT,
            tools=[PATTERN_TOOL],
            tool_choice={"type": "tool", "name": "report_cross_source_patterns"},
            messages=[{"role": "user", "content": json.dumps(batch_for_model, indent=2)}],
        )
        tool_use = next(block for block in response.content if block.type == "tool_use")
        try:
            patterns = tool_use.input["patterns"]
            if not isinstance(patterns, list) or not all(isinstance(p, dict) for p in patterns):
                raise TypeError(f"expected a list of pattern objects, got {patterns!r}")
            break
        except (KeyError, TypeError) as e:
            last_error = e
            print(f"detect_patterns: malformed tool response on attempt {attempt + 1} ({e}), retrying...")
    else:
        raise RuntimeError("detect_patterns: malformed tool response on both attempts") from last_error
    for p in patterns:
        p["description"] = _strip_stray_tags(p["description"])
        p["why_it_matters"] = _strip_stray_tags(p["why_it_matters"])
    return patterns


def main():
    project_dir = Path(__file__).parent
    classified_path = project_dir / "data" / "classified_updates.json"

    if not classified_path.exists():
        print("data/classified_updates.json not found -- running classify.py first...\n")
        subprocess.run([sys.executable, str(project_dir / "classify.py")], check=True)
        print()

    data = json.loads(classified_path.read_text())
    patterns = detect_patterns(data["updates"])

    print(f"Found {len(patterns)} cross-source pattern(s):\n")
    for p in patterns:
        print(f"[{p['pattern_type']}] {', '.join(p['tickets_involved'])}")
        print(f"  {p['description']}")
        print(f"  Why it matters: {p['why_it_matters']}")
        print()

    output_path = project_dir / "data" / "patterns.json"
    output_path.write_text(json.dumps({"report_date": data["report_date"], "patterns": patterns}, indent=2))
    print(f"Wrote patterns to {output_path.relative_to(project_dir)}")


if __name__ == "__main__":
    main()
