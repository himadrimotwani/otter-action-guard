from typing import Dict, Any, List
from .extractor import OtterActionGuard
from .models import ActionStatus, CommitmentType


class BenchmarkEvaluator:
    """
    Evaluates extraction fidelity, false positive rates for tentative/conditional
    ideas, and condition tracking between naive extraction vs OtterActionGuard.
    """

    def __init__(self):
        self.guard = OtterActionGuard()

    def evaluate_transcript(self, raw_text: str, title: str = "Test") -> Dict[str, Any]:
        result = self.guard.process_transcript(raw_text, title=title)

        # Naive approach simulation:
        # Naive extraction treats every statement with "will", "can", "if", "by" as a flat committed action item.
        naive_actions = [
            a for a in result.actions
            if any(k in a.raw_statement.lower() for k in ["will", "commit", "split", "deliver", "follow up", "update"])
        ]

        # Calculate metrics
        premature_executions_prevented = sum(
            1 for a in result.actions
            if a.status in [ActionStatus.BLOCKED_ON_CONDITION, ActionStatus.NEEDS_HUMAN_CLARIFICATION]
        )
        exploratory_false_positives_filtered = sum(
            1 for a in result.actions
            if a.commitment_type == CommitmentType.EXPLORATORY_PROPOSAL
        )
        verified_ready = result.ready_count

        return {
            "title": title,
            "total_turns": result.total_turns,
            "naive_action_count": len(naive_actions),
            "guard_total_candidates": result.total_candidate_actions,
            "guard_ready_count": verified_ready,
            "guard_blocked_count": result.blocked_count,
            "guard_clarification_count": result.clarification_count,
            "premature_executions_prevented": premature_executions_prevented,
            "exploratory_ideas_filtered": exploratory_false_positives_filtered,
            "mcp_payloads_generated": len(result.mcp_payloads),
            "detailed_actions": result.actions
        }
