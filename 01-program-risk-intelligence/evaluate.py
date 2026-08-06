"""Milestone 5 evaluation: accuracy, and explicit false positive/negative analysis.

Runs the classifier against two sets:
  - data/mock_status_updates.json  (17 items) -- the "regression" set the rubric
    was originally built against.
  - data/eval_scenarios.json       (8 items)  -- a harder, deliberately adversarial
    set, each one built to bait a specific failure mode (over-trusting alarmed
    tone, under-trusting calm boilerplate, blindly inflating severity because
    the self-report says High, a missing/null update, etc.) rather than to be a
    "typical" update.

Severity is ordered on_track < at_risk < blocked. A false positive is a
prediction more severe than ground truth (crying wolf); a false negative is a
prediction less severe than ground truth (missing a real risk) -- the more
dangerous direction for a tool whose whole purpose is not missing what a human
would have caught.
"""
from __future__ import annotations

import json
from pathlib import Path

from anthropic import Anthropic

from classify import classify_update

SEVERITY = {"on_track": 0, "at_risk": 1, "blocked": 2}
META_KEYS_TO_STRIP = {"purpose", "context_note"}


def strip_eval_only_fields(update: dict) -> dict:
    return {
        k: v
        for k, v in update.items()
        if not k.startswith("ground_truth") and k not in META_KEYS_TO_STRIP
    }


def evaluate_set(name: str, updates: list[dict], client: Anthropic) -> dict:
    rows = []
    for update in updates:
        result = classify_update(strip_eval_only_fields(update), client=client)
        expected = update["ground_truth_classification"]
        predicted = result["classification"]

        pred_sev = SEVERITY[predicted]
        exp_sev = SEVERITY[expected]
        if pred_sev == exp_sev:
            outcome = "match"
        elif pred_sev > exp_sev:
            outcome = "false_positive"
        else:
            outcome = "false_negative"

        rows.append(
            {
                "jira_ticket": update["jira_ticket"],
                "purpose": update.get("purpose"),
                "expected": expected,
                "predicted": predicted,
                "expected_signal": update.get("ground_truth_signal"),
                "predicted_signal": result["signal"],
                "signal_match": result["signal"] == update.get("ground_truth_signal"),
                "reason": result["reason"],
                "outcome": outcome,
            }
        )

    matches = sum(1 for r in rows if r["outcome"] == "match")
    signal_matches = sum(1 for r in rows if r["signal_match"])
    return {
        "name": name,
        "rows": rows,
        "classification_accuracy": matches / len(rows),
        "signal_accuracy": signal_matches / len(rows),
        "false_positives": [r for r in rows if r["outcome"] == "false_positive"],
        "false_negatives": [r for r in rows if r["outcome"] == "false_negative"],
    }


def render_markdown(regression: dict, adversarial: dict) -> str:
    lines = ["# Milestone 5 — Evaluation Report", ""]

    for result in (regression, adversarial):
        n = len(result["rows"])
        lines += [
            f"## {result['name']} ({n} items)",
            "",
            f"- Classification accuracy: **{result['classification_accuracy']:.0%}** ({sum(1 for r in result['rows'] if r['outcome'] == 'match')}/{n})",
            f"- Signal-type accuracy: **{result['signal_accuracy']:.0%}** ({sum(1 for r in result['rows'] if r['signal_match'])}/{n})",
            f"- False positives (predicted more severe than actual): **{len(result['false_positives'])}**",
            f"- False negatives (predicted less severe than actual, i.e. missed real risk): **{len(result['false_negatives'])}**",
            "",
        ]
        if result["false_positives"] or result["false_negatives"]:
            lines.append("| Ticket | Purpose | Expected | Predicted | Outcome | AI reason |")
            lines.append("|---|---|---|---|---|---|")
            for r in result["false_positives"] + result["false_negatives"]:
                purpose = r["purpose"] or "-"
                lines.append(
                    f"| {r['jira_ticket']} | {purpose} | {r['expected']} | {r['predicted']} | {r['outcome']} | {r['reason']} |"
                )
            lines.append("")
        else:
            lines.append("No false positives or false negatives in this set.")
            lines.append("")

        signal_misses = [r for r in result["rows"] if not r["signal_match"]]
        if signal_misses:
            lines.append("**Signal-type misses (classification still correct, but the *why* differed):**")
            lines.append("")
            for r in signal_misses:
                lines.append(
                    f"- `{r['jira_ticket']}` — predicted `{r['predicted_signal']}`, expected `{r['expected_signal']}`"
                )
            lines.append("")

    lines += [
        "## Reading these results",
        "",
        f"The regression set ({len(regression['rows'])} items) is the same dataset the rubric in the README was written against, "
        "so a high score there mostly confirms the rubric is internally consistent -- it's not a strong test on its own.",
        "",
        f"The adversarial set ({len(adversarial['rows'])} items) is the more meaningful number: each item was purpose-built to bait a "
        "specific failure mode (see the `purpose` column above) rather than to be a realistic 'typical' update. A tool that scores well "
        "here is resisting the two failure modes that would make it useless in practice: crying wolf on things that are actually fine "
        "(false positive), and getting lulled by calm language or an over-cautious self-report into missing something real (false negative).",
    ]
    return "\n".join(lines)


def main():
    project_dir = Path(__file__).parent
    regression_updates = json.loads((project_dir / "data" / "mock_status_updates.json").read_text())["updates"]
    adversarial_updates = json.loads((project_dir / "data" / "eval_scenarios.json").read_text())["updates"]

    client = Anthropic()

    print(f"Evaluating regression set ({len(regression_updates)} items)...")
    regression = evaluate_set("Regression set (mock_status_updates.json)", regression_updates, client)

    print(f"Evaluating adversarial set ({len(adversarial_updates)} items)...")
    adversarial = evaluate_set("Adversarial set (eval_scenarios.json)", adversarial_updates, client)

    report = render_markdown(regression, adversarial)
    output_path = project_dir / "data" / "evaluation_report.md"
    output_path.write_text(report)

    print()
    print(report)
    print()
    print(f"Wrote {output_path.relative_to(project_dir)}")


if __name__ == "__main__":
    main()
