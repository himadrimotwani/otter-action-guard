from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


class CommitmentType(str, Enum):
    FIRM_COMMITMENT = "FIRM_COMMITMENT"             # Explicit pledge by speaker ("I will deliver the report")
    CONDITIONAL_COMMITMENT = "CONDITIONAL_COMMITMENT" # Gated on external factor ("If QA passes, we will ship")
    EXPLORATORY_PROPOSAL = "EXPLORATORY_PROPOSAL"   # Hypothetical / brainstorming ("What if we offered 5%?")
    DELEGATED_REQUEST = "DELEGATED_REQUEST"         # Task assigned to another party ("Dave, please audit this")
    AMBIGUOUS_PASSIVE = "AMBIGUOUS_PASSIVE"         # Unowned / passive ("Someone should follow up")


class ActionStatus(str, Enum):
    READY_FOR_EXECUTION = "READY_FOR_EXECUTION"         # High confidence, unblocked, clear assignee
    BLOCKED_ON_CONDITION = "BLOCKED_ON_CONDITION"       # Valid commitment, but has pending prerequisite
    NEEDS_HUMAN_CLARIFICATION = "NEEDS_CLARIFICATION"   # Low confidence, unassigned, or vague timeline
    INFORMATIONAL_ONLY = "INFORMATIONAL_ONLY"           # Discussion item, not a dispatchable action


@dataclass
class SpeakerTurn:
    speaker: str
    timestamp: str = "00:00"
    text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ActionItem:
    id: str
    source_turn_index: int
    raw_statement: str
    speaker: str
    assigned_to: Optional[str] = None
    commitment_type: CommitmentType = CommitmentType.FIRM_COMMITMENT
    action_description: str = ""
    prerequisite_condition: Optional[str] = None
    target_date_raw: Optional[str] = None
    confidence_score: float = 1.0
    status: ActionStatus = ActionStatus.READY_FOR_EXECUTION
    clarification_prompt: Optional[str] = None
    suggested_integration: Optional[str] = None  # e.g. "jira", "slack", "erp", "calendar"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["commitment_type"] = self.commitment_type.value
        d["status"] = self.status.value
        return d


@dataclass
class MCPActionPayload:
    """Payload compliant with Model Context Protocol (MCP) tool execution schemas."""
    tool_name: str
    parameters: Dict[str, Any]
    requires_approval: bool
    source_action_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingAnalysisResult:
    meeting_id: str
    title: str
    total_turns: int
    total_candidate_actions: int
    ready_count: int
    blocked_count: int
    clarification_count: int
    actions: List[ActionItem] = field(default_factory=list)
    mcp_payloads: List[MCPActionPayload] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "total_turns": self.total_turns,
            "total_candidate_actions": self.total_candidate_actions,
            "ready_count": self.ready_count,
            "blocked_count": self.blocked_count,
            "clarification_count": self.clarification_count,
            "actions": [a.to_dict() for a in self.actions],
            "mcp_payloads": [p.to_dict() for p in self.mcp_payloads]
        }
