from typing import List
from .models import ActionItem, ActionStatus, MCPActionPayload


class MCPActionBridge:
    """
    Translates disambiguated action items into standardized Model Context Protocol (MCP)
    tool call payloads for target enterprise connectors (Jira, Slack, ERP/Procurement).
    """

    @staticmethod
    def create_payload(action: ActionItem) -> MCPActionPayload:
        """Constructs an MCP-compliant payload based on the action type and status."""
        
        # Decide destination based on content & conditions
        is_supply_chain_or_po = any(
            kw in action.action_description.lower()
            for kw in ["batch", "supplier", "shipment", "po", "pricing", "units", "vendor", "inventory"]
        )

        requires_approval = action.status != ActionStatus.READY_FOR_EXECUTION

        if is_supply_chain_or_po:
            tool_name = "erp_procurement_update_commitment"
            params = {
                "owner": action.assigned_to or "Unassigned",
                "summary": action.action_description,
                "target_date": action.target_date_raw or "TBD",
                "prerequisite": action.prerequisite_condition,
                "status": "PENDING_VERIFICATION" if requires_approval else "COMMITTED",
                "confidence": action.confidence_score,
                "source_transcript_quote": action.raw_statement
            }
        elif action.assigned_to and action.status == ActionStatus.READY_FOR_EXECUTION:
            tool_name = "jira_create_issue"
            params = {
                "project_key": "PROJ",
                "summary": action.action_description,
                "assignee": action.assigned_to,
                "due_date": action.target_date_raw or "Unspecified",
                "description": f"Extracted from Otter Meeting transcript:\n\"{action.raw_statement}\"",
                "issue_type": "Task"
            }
        else:
            # Fallback to Slack confirmation / clarification ping
            tool_name = "slack_post_clarification_prompt"
            params = {
                "channel": "#meeting-followups",
                "recipient": action.assigned_to or action.speaker,
                "prompt_message": action.clarification_prompt or f"Please verify task: {action.action_description}",
                "original_quote": action.raw_statement
            }

        return MCPActionPayload(
            tool_name=tool_name,
            parameters=params,
            requires_approval=requires_approval,
            source_action_id=action.id
        )

    def generate_all(self, actions: List[ActionItem]) -> List[MCPActionPayload]:
        # Filter out purely informational statements
        actionable = [a for a in actions if a.status != ActionStatus.INFORMATIONAL_ONLY]
        return [self.create_payload(a) for a in actionable]
