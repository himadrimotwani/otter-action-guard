import re
from typing import Optional, Tuple
from .models import CommitmentType, ActionStatus


class ActionDisambiguator:
    """
    Analyzes raw speech statements to classify commitment intent,
    isolate conditional prerequisites, identify assignee clarity,
    and compute ambiguity confidence scores.
    """

    # Linguistic cues for conditionality
    CONDITIONAL_REGEX = re.compile(
        r"\b(if|only if|provided that|as long as|subject to|assuming|in case|unless|pending)\b\s+([^,.;]+)",
        re.IGNORECASE
    )

    # Cues for exploratory/hypothetical proposals
    EXPLORATORY_REGEX = re.compile(
        r"\b(what if|maybe we could|could we potentially|would it make sense|we might consider|how about if|thinking out loud)\b",
        re.IGNORECASE
    )

    # Cues for passive/unowned tasks
    PASSIVE_REGEX = re.compile(
        r"\b(someone needs to|somebody should|needs to get done|it would be good to|we ought to|ought to be looked at)\b",
        re.IGNORECASE
    )

    # Cues for delegation
    DELEGATION_REGEX = re.compile(
        r"(?:([A-Z][a-z]+),\s+)?\b(can you|could you please|please make sure to|let's have\s+([A-Z][a-z]+)\s+take care of|assign\s+(?:this\s+)?to\s+([A-Z][a-z]+))\b",
        re.IGNORECASE
    )

    # Cues for firm first-person commitment
    FIRM_REGEX = re.compile(
        r"\b(I will|I'll|we will|we'll|I am going to|I'm going to|I commit to|I will make sure to|I'll send|I'll deliver)\b",
        re.IGNORECASE
    )

    # Temporal cues for deadlines
    DATE_REGEX = re.compile(
        r"\b(by\s+(?:next\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|EOD|end of week|tomorrow|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*))\b",
        re.IGNORECASE
    )

    def analyze_statement(
        self,
        speaker: str,
        text: str
    ) -> Tuple[CommitmentType, ActionStatus, Optional[str], Optional[str], Optional[str], float, Optional[str]]:
        """
        Returns:
            commitment_type: CommitmentType
            status: ActionStatus
            assigned_to: Optional[str]
            condition: Optional[str]
            deadline: Optional[str]
            confidence: float
            clarification_prompt: Optional[str]
        """
        cleaned = text.strip()
        deadline_match = self.DATE_REGEX.search(cleaned)
        deadline = deadline_match.group(1) if deadline_match else None

        # 1. Check for Exploratory Proposals
        if self.EXPLORATORY_REGEX.search(cleaned):
            prompt = f"Otter noted this sounded like an exploratory proposal rather than a firm commitment. Should an action item be created?"
            return (
                CommitmentType.EXPLORATORY_PROPOSAL,
                ActionStatus.INFORMATIONAL_ONLY,
                None,
                None,
                deadline,
                0.88,
                prompt
            )

        # 2. Check for Passive / Unassigned Tasks
        if self.PASSIVE_REGEX.search(cleaned):
            prompt = f"Task was suggested ('{cleaned}') but has no assigned owner. Who should own this?"
            return (
                CommitmentType.AMBIGUOUS_PASSIVE,
                ActionStatus.NEEDS_HUMAN_CLARIFICATION,
                None,
                None,
                deadline,
                0.55,
                prompt
            )

        # 3. Check for Conditional Commitments
        cond_match = self.CONDITIONAL_REGEX.search(cleaned)
        if cond_match:
            condition = cond_match.group(0).strip()
            # Determine assignee
            assigned_to = speaker
            prompt = f"Action is contingent on: '{condition}'. Hold action execution until condition is verified?"
            return (
                CommitmentType.CONDITIONAL_COMMITMENT,
                ActionStatus.BLOCKED_ON_CONDITION,
                assigned_to,
                condition,
                deadline,
                0.82,
                prompt
            )

        # 4. Check for Delegation
        deleg_match = self.DELEGATION_REGEX.search(cleaned)
        if deleg_match:
            # Try to grab the named delegate if captured
            named_delegate = deleg_match.group(1) or deleg_match.group(3) or (deleg_match.group(4) if len(deleg_match.groups()) >= 4 else None)
            assigned_to = named_delegate if named_delegate else "Unassigned Delegate"
            prompt = f"{speaker} delegated this request. Awaiting acceptance from {assigned_to} before dispatching."
            return (
                CommitmentType.DELEGATED_REQUEST,
                ActionStatus.READY_FOR_EXECUTION if named_delegate else ActionStatus.NEEDS_HUMAN_CLARIFICATION,
                assigned_to,
                None,
                deadline,
                0.78,
                prompt
            )

        # 5. Check for Firm Direct Commitment
        if self.FIRM_REGEX.search(cleaned):
            return (
                CommitmentType.FIRM_COMMITMENT,
                ActionStatus.READY_FOR_EXECUTION,
                speaker,
                None,
                deadline,
                0.95,
                None
            )

        # Generic / Informational fallback
        return (
            CommitmentType.EXPLORATORY_PROPOSAL,
            ActionStatus.INFORMATIONAL_ONLY,
            None,
            None,
            deadline,
            0.60,
            None
        )
