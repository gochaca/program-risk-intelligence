"""Risk classification for weekly program status updates, via the Claude API.

Classifies a single status update into on_track / at_risk / blocked, plus a
signal type (quiet, bottlenecked, competing_objectives, unowned_escalation,
none) and a stated reason. See README.md for the full rubric definition.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")

RUBRIC = """You are a program risk analyst reviewing a single weekly status update \
from a team or vendor on a large, multi-team enterprise program. Classify it \
using this rubric.

CLASSIFICATION (pick exactly one):
- on_track: No credible threat to the due date. Any mentioned risk is proactively \
managed with a clear plan.
- at_risk: One or more signals below are present and could threaten the due date \
without intervention, but the work is still moving.
- blocked: Progress has actually stopped -- waiting on a person, team, vendor, or \
decision outside this team's control, with no forward movement possible until \
it's resolved.

SIGNAL (pick the single best-fitting one; use "none" only if the update is \
genuinely clean):
- quiet: The workstream has gone quiet -- no update submitted, or the update just \
repeats a prior status with no new information.
- bottlenecked: Work is stalled behind a dependency, review, or decision that \
isn't moving.
- competing_objectives: An urgent, unplanned item (emergency, executive ask, \
incident) has superseded the reported work.
- unowned_escalation: A real risk has been raised (possibly even self-rated High) \
but no leader or decision-maker has picked it up or moved on it.
- none: No signal present.

Do not simply trust the team's self-reported risk rating -- teams sometimes \
under-report risk they're causing for others, or rate risk without accounting for \
how close the due date actually is. Read the update text and due date and make \
your own call. State a concise reason in your own words, citing specifics from \
the update."""

CLASSIFY_TOOL = {
    "name": "classify_status_update",
    "description": "Record the risk classification for a single status update.",
    "input_schema": {
        "type": "object",
        "properties": {
            "classification": {
                "type": "string",
                "enum": ["on_track", "at_risk", "blocked"],
            },
            "signal": {
                "type": "string",
                "enum": [
                    "quiet",
                    "bottlenecked",
                    "competing_objectives",
                    "unowned_escalation",
                    "none",
                ],
            },
            "reason": {
                "type": "string",
                "description": "One or two sentences citing specifics from the update.",
            },
        },
        "required": ["classification", "signal", "reason"],
    },
}


def classify_update(update: dict, client: Anthropic | None = None) -> dict:
    """Classify a single status update.

    `update` should be the fields a team actually submits (team, jira_ticket,
    initiative, due_date, report_date, update_text, self_reported_risk,
    self_reported_rationale). Any ground_truth_* fields are stripped before
    the update is sent to the model -- they exist only for evaluation.
    """
    client = client or Anthropic()

    update_for_model = {k: v for k, v in update.items() if not k.startswith("ground_truth")}

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=RUBRIC,
        tools=[CLASSIFY_TOOL],
        tool_choice={"type": "tool", "name": "classify_status_update"},
        messages=[{"role": "user", "content": json.dumps(update_for_model, indent=2)}],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    return tool_use.input


def main():
    data_path = Path(__file__).parent / "data" / "mock_status_updates.json"
    output_path = Path(__file__).parent / "data" / "classified_updates.json"
    data = json.loads(data_path.read_text())

    client = Anthropic()
    correct = 0
    total = 0
    classified = []

    for update in data["updates"]:
        result = classify_update(update, client=client)
        expected = update.get("ground_truth_classification")
        is_match = expected is not None and result["classification"] == expected
        if expected:
            total += 1
            correct += int(is_match)

        status = "match" if is_match else "MISMATCH"
        print(f"{update['jira_ticket']:10} predicted={result['classification']:11} expected={expected or '-':11} [{status}]")
        print(f"           signal={result['signal']:20} reason={result['reason']}")
        print()

        classified.append(
            {
                **update,
                "ai_classification": result["classification"],
                "ai_signal": result["signal"],
                "ai_reason": result["reason"],
            }
        )

    if total:
        print(f"Classification match rate vs ground truth: {correct}/{total} ({correct / total:.0%})")

    output_path.write_text(json.dumps({"report_date": data["report_date"], "updates": classified}, indent=2))
    print(f"\nWrote classified output to {output_path.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    main()
