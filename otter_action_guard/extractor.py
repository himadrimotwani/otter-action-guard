import re
from typing import List, Optional
from .models import SpeakerTurn, ActionItem, MeetingAnalysisResult, ActionStatus
from .parser import TranscriptParser
from .disambiguator import ActionDisambiguator
from .mcp_bridge import MCPActionBridge


class OtterActionGuard:
    """
    Main orchestration engine for analyzing meeting transcripts,
    extracting commitments, resolving ambiguities, and bridging to MCP tools.
    """

    # Quick candidate filter for lines likely containing commitments, actions, or requests
    ACTION_TRIGGER_REGEX = re.compile(
        r"\b(will|going to|let's|can you|could you|please|if|should|need to|ought to|what if|commit|send|prepare|update|follow up|schedule|review|approve)\b",
        re.IGNORECASE
    )

    def __init__(self):
        self.parser = TranscriptParser()
        self.disambiguator = ActionDisambiguator()
        self.bridge = MCPActionBridge()

    def process_transcript(
        self,
        raw_transcript: str,
        meeting_id: str = "MEET-001",
        title: str = "Enterprise Operations Review"
    ) -> MeetingAnalysisResult:
        turns: List[SpeakerTurn] = self.parser.parse_text(raw_transcript)
        actions: List[ActionItem] = []

        action_counter = 1
        for idx, turn in enumerate(turns):
            if not self.ACTION_TRIGGER_REGEX.search(turn.text):
                continue

            (
                comm_type,
                status,
                assigned_to,
                condition,
                deadline,
                confidence,
                clarification_prompt
            ) = self.disambiguator.analyze_statement(turn.speaker, turn.text)

            # Assign integration suggestion
            if "jira" in turn.text.lower() or "ticket" in turn.text.lower():
                integration = "jira"
            elif any(k in turn.text.lower() for k in ["po", "supplier", "shipment", "batch"]):
                integration = "erp"
            elif "calendar" in turn.text.lower() or "meeting" in turn.text.lower():
                integration = "calendar"
            else:
                integration = "slack"

            action = ActionItem(
                id=f"ACT-{action_counter:03d}",
                source_turn_index=idx,
                raw_statement=turn.text,
                speaker=turn.speaker,
                assigned_to=assigned_to,
                commitment_type=comm_type,
                action_description=turn.text,
                prerequisite_condition=condition,
                target_date_raw=deadline,
                confidence_score=confidence,
                status=status,
                clarification_prompt=clarification_prompt,
                suggested_integration=integration
            )
            actions.append(action)
            action_counter += 1

        mcp_payloads = self.bridge.generate_all(actions)

        ready_count = sum(1 for a in actions if a.status == ActionStatus.READY_FOR_EXECUTION)
        blocked_count = sum(1 for a in actions if a.status == ActionStatus.BLOCKED_ON_CONDITION)
        clarification_count = sum(1 for a in actions if a.status == ActionStatus.NEEDS_HUMAN_CLARIFICATION)

        return MeetingAnalysisResult(
            meeting_id=meeting_id,
            title=title,
            total_turns=len(turns),
            total_candidate_actions=len(actions),
            ready_count=ready_count,
            blocked_count=blocked_count,
            clarification_count=clarification_count,
            actions=actions,
            mcp_payloads=mcp_payloads
        )
