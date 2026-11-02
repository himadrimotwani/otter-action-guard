#!/usr/bin/env python3
"""
OtterActionGuard Demo
Run: python demo.py
Demonstrates meeting-to-action disambiguation, conditional tracking,
and Model Context Protocol (MCP) payload generation on supply-chain and engineering transcripts.
"""

import json
from pathlib import Path
from otter_action_guard.extractor import OtterActionGuard
from otter_action_guard.evaluator import BenchmarkEvaluator
from otter_action_guard.models import ActionStatus


def run_demo():
    print("=" * 80)
    print(" 🦦 OtterActionGuard: Meeting-to-Action Disambiguation & Verification Engine")
    print("=" * 80)

    data_path = Path(__file__).parent / "data" / "sample_transcripts.json"
    if not data_path.exists():
        print(f"Error: Data file {data_path} not found.")
        return

    with open(data_path, "r") as f:
        samples = json.load(f)

    evaluator = BenchmarkEvaluator()
    guard = OtterActionGuard()

    for idx, sample in enumerate(samples, 1):
        print(f"\n[{idx}] SCENARIO: {sample['title']} (ID: {sample['meeting_id']})")
        print("-" * 80)
        print("RAW TRANSCRIPT SNIPPET:")
        for line in sample["transcript"].strip().split("\n")[:4]:
            print(f"  {line}")
        print("  ... [truncated for display]")

        # Process with OtterActionGuard
        result = guard.process_transcript(
            sample["transcript"],
            meeting_id=sample["meeting_id"],
            title=sample["title"]
        )

        metrics = evaluator.evaluate_transcript(sample["transcript"], title=sample["title"])

        print("\n📊 BENCHMARK COMPARISON:")
        print(f"  • Total Speaker Turns Analyzed        : {result.total_turns}")
        print(f"  • Naive LLM Actions (Flat Extraction)  : {metrics['naive_action_count']} (Treats tentative ideas as commitments)")
        print(f"  • OtterActionGuard Verified Actions   : {result.ready_count} READY FOR DISPATCH")
        print(f"  • Conditional Actions Gated           : {result.blocked_count} (Requires prerequisite before execution)")
        print(f"  • Unassigned / Ambiguous Tasks Flagged: {result.clarification_count} (Prompt drafted for in-call assist)")
        print(f"  🛡️ PREMATURE TICKET EXECUTIONS BLOCKED: {metrics['premature_executions_prevented']}")

        print("\n🔍 DETAILED ACTION DISAMBIGUATION BREAKDOWN:")
        for action in result.actions:
            status_symbol = "✅" if action.status == ActionStatus.READY_FOR_EXECUTION else (
                "⏳" if action.status == ActionStatus.BLOCKED_ON_CONDITION else (
                    "❓" if action.status == ActionStatus.NEEDS_HUMAN_CLARIFICATION else "💡"
                )
            )
            print(f"  [{action.id}] {status_symbol} [{action.status.value}] ({action.commitment_type.value})")
            print(f"      Speaker: {action.speaker} | Owner: {action.assigned_to or 'UNASSIGNED'}")
            print(f"      Quote  : \"{action.raw_statement}\"")
            if action.prerequisite_condition:
                print(f"      ⚠️  Gating Condition : {action.prerequisite_condition}")
            if action.clarification_prompt:
                print(f"      💬 Live Assist Prompt: {action.clarification_prompt}")

        print("\n🔌 MODEL CONTEXT PROTOCOL (MCP) DISPATCH PAYLOADS:")
        for payload in result.mcp_payloads[:2]:
            approval_badge = "[MANUAL APPROVAL REQUIRED]" if payload.requires_approval else "[AUTO-APPROVED]"
            print(f"  • Tool: {payload.tool_name} {approval_badge}")
            print(f"    Params: {json.dumps(payload.parameters, indent=6)}")

        print("=" * 80)

    print("\n✅ Demo finished successfully.")


if __name__ == "__main__":
    run_demo()
