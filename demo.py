#!/usr/bin/env python3
"""
OtterActionGuard Demo
Run: python3 demo.py

Demonstrates:
1. Contextual ASR Speech Correction (recovering acoustic phoneme errors like 'bomb' -> 'BOM', 'skew' -> 'SKU')
2. Multi-turn AI Agent Coreference & Chain-of-Thought (CoT) Deliberation
3. Gated Model Context Protocol (MCP) Enterprise Tool Dispatch
"""

import json
from pathlib import Path
from otter_action_guard.extractor import OtterActionGuard
from otter_action_guard.evaluator import BenchmarkEvaluator
from otter_action_guard.models import ActionStatus


def run_demo():
    print("=" * 85)
    print(" 🦦 OtterActionGuard: AI Agent Meeting-to-Action Disambiguation Engine")
    print("=" * 85)

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
        print("-" * 85)
        print("RAW TRANSCRIPT (Showing first 4 lines with raw speech ASR artifacts):")
        for line in sample["transcript"].strip().split("\n")[:4]:
            print(f"  {line}")
        print("  ... [truncated for display]")

        # Run extraction pipeline
        result = guard.process_transcript(
            sample["transcript"],
            meeting_id=sample["meeting_id"],
            title=sample["title"]
        )

        metrics = evaluator.evaluate_transcript(sample["transcript"], title=sample["title"])

        print(f"\n🎙️ 1. CONTEXTUAL SPEECH ASR REPAIR:")
        print(f"  • Acoustic / Phonetic Corrections Applied: {result.speech_corrections_made} domain terms repaired")

        print(f"\n📊 2. AI BENCHMARK COMPARISON:")
        print(f"  • Total Speaker Turns Analyzed          : {result.total_turns}")
        print(f"  • Naive LLM Actions (Flat Extraction)    : {metrics['naive_action_count']} (mistakes ideas & conditional chat for commitments)")
        print(f"  • OtterActionGuard Verified Actions     : {result.ready_count} READY FOR DISPATCH")
        print(f"  • Conditional Actions Gated             : {result.blocked_count} (Prerequisites locked prior to execution)")
        print(f"  • Unassigned / Ambiguous Tasks Flagged  : {result.clarification_count} (Otter Live Assist prompt generated)")
        print(f"  🛡️ PREMATURE ENTERPRISE ACTIONS PREVENTED: {metrics['premature_executions_prevented']}")

        print(f"\n🧠 3. AI AGENT REASONING TRACE (CHAIN-OF-THOUGHT & COREFERENCE):")
        for action in result.actions:
            status_symbol = "✅" if action.status == ActionStatus.READY_FOR_EXECUTION else (
                "⏳" if action.status == ActionStatus.BLOCKED_ON_CONDITION else (
                    "❓" if action.status == ActionStatus.NEEDS_HUMAN_CLARIFICATION else "💡"
                )
            )
            print(f"\n  [{action.id}] {status_symbol} {action.status.value} ({action.commitment_type.value})")
            print(f"      Speaker : {action.speaker} | Assigned: {action.assigned_to or 'UNASSIGNED'}")
            print(f"      Quote   : \"{action.raw_statement}\"")
            if action.thought_trace:
                print(f"      💭 CoT  : {action.thought_trace}")
            if action.prerequisite_condition:
                print(f"      ⚠️ Gate : {action.prerequisite_condition}")
            if action.clarification_prompt:
                print(f"      💬 Ping : {action.clarification_prompt}")

        print(f"\n🔌 4. MODEL CONTEXT PROTOCOL (MCP) TOOL EXECUTION PAYLOADS:")
        for payload in result.mcp_payloads[:2]:
            badge = "[MANUAL APPROVAL REQUIRED]" if payload.requires_approval else "[AUTO-APPROVED]"
            print(f"  • Tool: {payload.tool_name} {badge}")
            print(f"    Params: {json.dumps(payload.parameters, indent=6)}")

        print("=" * 85)

    print("\n✅ Demo completed successfully.")


if __name__ == "__main__":
    run_demo()
