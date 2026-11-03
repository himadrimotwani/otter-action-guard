import re
from typing import List, Optional
from .models import SpeakerTurn, ActionItem, MeetingAnalysisResult, ActionStatus, CommitmentType
from .parser import TranscriptParser
from .disambiguator import ActionDisambiguator
from .mcp_bridge import MCPActionBridge
from .speech_corrector import ContextualSpeechCorrector
from .ai_agent import AIAgentEngine


class OtterActionGuard:
    """
    Orchestration engine combining:
    1. Contextual ASR Phonetic Speech Correction
    2. Multi-turn AI Agent Coreference & Chain-of-Thought Reasoning
    3. Prerequisite Gating & Ambiguity Disambiguation
    4. Model Context Protocol (MCP) Enterprise Tool Payload Generation
    """

    ACTION_TRIGGER_REGEX = re.compile(
        r"\b(will|going to|let's|can you|could you|please|if|should|need to|ought to|what if|commit|send|prepare|update|follow up|schedule|review|approve)\b",
        re.IGNORECASE
    )

    def __init__(self, ai_provider: str = "auto"):
        self.parser = TranscriptParser()
        self.speech_corrector = ContextualSpeechCorrector()
        self.disambiguator = ActionDisambiguator()
        self.ai_agent = AIAgentEngine(provider=ai_provider)
        self.bridge = MCPActionBridge()

    def process_transcript(
        self,
        raw_transcript: str,
        meeting_id: str = "MEET-001",
        title: str = "Enterprise Operations Review",
        enable_speech_correction: bool = True,
        enable_ai_agent: bool = True
    ) -> MeetingAnalysisResult:
        # Step 1: Parse multi-speaker turns
        raw_turns: List[SpeakerTurn] = self.parser.parse_text(raw_transcript)
        turns: List[SpeakerTurn] = []
        total_corrections = 0

        # Step 2: Contextual Speech / ASR Correction
        for turn in raw_turns:
            if enable_speech_correction:
                cleaned_text, fixes = self.speech_corrector.correct_text(turn.text)
                total_corrections += len(fixes)
                turns.append(SpeakerTurn(speaker=turn.speaker, timestamp=turn.timestamp, text=cleaned_text))
            else:
                turns.append(turn)

        actions: List[ActionItem] = []
        action_counter = 1

        # Step 3: Action candidate filtering and AI Agent deliberation
        for idx, turn in enumerate(turns):
            if not self.ACTION_TRIGGER_REGEX.search(turn.text):
                continue

            # Deterministic linguistic analysis
            (
                rule_comm_type,
                rule_status,
                assigned_to,
                condition,
                deadline,
                confidence,
                rule_prompt
            ) = self.disambiguator.analyze_statement(turn.speaker, turn.text)

            thought_trace = None
            coreferences = None

            # Deep AI Agent reasoning (incorporating dialogue history & coreference resolution)
            if enable_ai_agent:
                ai_output = self.ai_agent.analyze_dialogue_with_context(turns, idx)
                thought_trace = ai_output.get("thought_trace")
                coreferences = ai_output.get("resolved_coreferences")
                
                # Align commitment type and status if AI provided structured classification
                if "commitment_type" in ai_output:
                    try:
                        rule_comm_type = CommitmentType(ai_output["commitment_type"])
                    except Exception:
                        pass
                if "status" in ai_output:
                    try:
                        rule_status = ActionStatus(ai_output["status"])
                    except Exception:
                        pass
                if ai_output.get("clarification_prompt"):
                    rule_prompt = ai_output["clarification_prompt"]

            # Determine suggested integration
            text_lower = turn.text.lower()
            if any(k in text_lower for k in ["po", "batch", "supplier", "shipment", "bom", "wms", "pricing"]):
                integration = "erp"
            elif any(k in text_lower for k in ["jira", "ticket", "rate-limiter", "staging", "secrets"]):
                integration = "jira"
            elif "calendar" in text_lower or "schedule" in text_lower:
                integration = "calendar"
            else:
                integration = "slack"

            action = ActionItem(
                id=f"ACT-{action_counter:03d}",
                source_turn_index=idx,
                raw_statement=turn.text,
                speaker=turn.speaker,
                assigned_to=assigned_to,
                commitment_type=rule_comm_type,
                action_description=turn.text,
                prerequisite_condition=condition,
                target_date_raw=deadline,
                confidence_score=confidence,
                status=rule_status,
                clarification_prompt=rule_prompt,
                suggested_integration=integration,
                thought_trace=thought_trace,
                coreference_resolution=coreferences
            )
            actions.append(action)
            action_counter += 1

        # Step 4: Generate Model Context Protocol (MCP) tool payloads
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
            speech_corrections_made=total_corrections,
            actions=actions,
            mcp_payloads=mcp_payloads
        )
