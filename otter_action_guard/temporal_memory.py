import re
from typing import List, Dict, Tuple, Optional
from .models import (
    ActionItem,
    ActionStatus,
    CrossMeetingEvent,
    SpeakerTurn,
    MCPActionPayload
)
from .mcp_bridge import MCPActionBridge


class TemporalMemoryEngine:
    """
    Otter 'Conversational Knowledge Engine' / Temporal State Tracker.
    Maintains cross-meeting memory, tracks unresolved conditional prerequisites,
    and detects when subsequent meetings resolve, confirm, or modify commitments
    made in prior sessions.
    """

    # Resolution cues indicating a prerequisite has been satisfied
    RESOLUTION_INDICATORS = [
        r"\b(?:cleared|completed|finished|passed|approved|signed off|resolved|done|locked in|confirmed)\b",
        r"\b(?:customs\s+(?:cleared|clearance\s+clears?|is\s+done))\b",
        r"\b(?:qa\s+(?:passed|finished|approved|audit\s+is\s+done))\b",
        r"\b(?:lab\s+(?:results\s+are\s+in|cleared|tested))\b",
        r"\b(?:finance\s+(?:signed\s+off|approved))\b"
    ]

    def __init__(self):
        # Global ledger mapping action_id -> ActionItem across all meetings
        self.ledger: Dict[str, ActionItem] = {}
        # History of events across meetings
        self.events: List[CrossMeetingEvent] = []
        self.processed_meetings: List[str] = []
        self.bridge = MCPActionBridge()

    def register_meeting_actions(self, meeting_id: str, actions: List[ActionItem]) -> None:
        """Stores extracted actions from a meeting into the cross-meeting ledger."""
        for act in actions:
            act.source_meeting_id = meeting_id
            self.ledger[act.id] = act
        if meeting_id not in self.processed_meetings:
            self.processed_meetings.append(meeting_id)

    def scan_for_cross_meeting_resolutions(
        self,
        current_meeting_id: str,
        turns: List[SpeakerTurn]
    ) -> Tuple[List[CrossMeetingEvent], List[MCPActionPayload]]:
        """
        Inspects turns in the current meeting to see if any blocked prerequisites
        from past meetings are now fulfilled.
        """
        resolved_events: List[CrossMeetingEvent] = []
        unlocked_payloads: List[MCPActionPayload] = []

        # Find all active blocked commitments from prior meetings
        blocked_actions = [
            act for act in self.ledger.values()
            if act.status == ActionStatus.BLOCKED_ON_CONDITION
            and act.source_meeting_id != current_meeting_id
            and act.prerequisite_condition
        ]

        if not blocked_actions:
            return resolved_events, unlocked_payloads

        for turn in turns:
            turn_text = turn.text.lower()

            for act in blocked_actions:
                cond = (act.prerequisite_condition or "").lower()

                # Extract key noun entities from the prerequisite condition (e.g. 'customs', 'qa', 'audit', 'lab')
                key_entities = [k for k in ["customs", "qa", "stress-test", "audit", "lab", "finance", "redis", "secrets"] if k in cond]
                
                # Check if the turn mentions the entity and a positive resolution indicator
                entity_mentioned = any(ent in turn_text for ent in key_entities) if key_entities else False
                resolution_signaled = any(re.search(pat, turn_text) for pat in self.RESOLUTION_INDICATORS)

                if entity_mentioned and resolution_signaled:
                    # Resolution confirmed!
                    old_status = act.status
                    act.status = ActionStatus.READY_FOR_EXECUTION
                    act.thought_trace = (
                        f"Resolved in later session ({current_meeting_id}) by {turn.speaker}: "
                        f"\"{turn.text}\". Prerequisite ('{act.prerequisite_condition}') verified."
                    )
                    
                    event = CrossMeetingEvent(
                        event_id=f"EVT-{len(self.events) + 1:03d}",
                        event_type="PREREQUISITE_FULFILLED",
                        target_action_id=act.id,
                        source_meeting_id=current_meeting_id,
                        source_speaker=turn.speaker,
                        evidence_statement=turn.text,
                        previous_status=old_status,
                        new_status=ActionStatus.READY_FOR_EXECUTION,
                        explanation=f"Condition '{act.prerequisite_condition}' satisfied by update from {turn.speaker} in {current_meeting_id}."
                    )
                    
                    self.events.append(event)
                    resolved_events.append(event)

                    # Generate auto-approved dispatch payload
                    unlocked_payload = self.bridge.create_payload(act)
                    unlocked_payload.requires_approval = False
                    unlocked_payloads.append(unlocked_payload)

        return resolved_events, unlocked_payloads

    def get_ledger_summary(self) -> Dict[str, Any]:
        return {
            "total_tracked_actions": len(self.ledger),
            "total_meetings": len(self.processed_meetings),
            "ready_actions": sum(1 for a in self.ledger.values() if a.status == ActionStatus.READY_FOR_EXECUTION),
            "blocked_actions": sum(1 for a in self.ledger.values() if a.status == ActionStatus.BLOCKED_ON_CONDITION),
            "clarifications_needed": sum(1 for a in self.ledger.values() if a.status == ActionStatus.NEEDS_HUMAN_CLARIFICATION),
            "resolved_events": [e.to_dict() for e in self.events]
        }
