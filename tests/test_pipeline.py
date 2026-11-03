import unittest
from otter_action_guard.extractor import OtterActionGuard
from otter_action_guard.disambiguator import ActionDisambiguator
from otter_action_guard.models import CommitmentType, ActionStatus
from otter_action_guard.parser import TranscriptParser
from otter_action_guard.speech_corrector import ContextualSpeechCorrector
from otter_action_guard.ai_agent import AIAgentEngine


class TestOtterActionGuard(unittest.TestCase):

    def test_transcript_parser(self):
        raw = (
            "[01:15] Alice: I will send the update.\n"
            "[01:30] Bob: Let's follow up on Tuesday."
        )
        turns = TranscriptParser.parse_text(raw)
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0].speaker, "Alice")
        self.assertEqual(turns[0].timestamp, "01:15")
        self.assertIn("send the update", turns[0].text)
        self.assertEqual(turns[1].speaker, "Bob")

    def test_contextual_speech_corrector(self):
        corrector = ContextualSpeechCorrector()
        raw = "Please check the skew 902 inventory and send the revised bomb quotation."
        corrected, fixes = corrector.correct_text(raw)
        self.assertIn("SKU 902", corrected)
        self.assertIn("BOM", corrected)
        self.assertEqual(len(fixes), 2)

    def test_conditional_commitment_detection(self):
        disambiguator = ActionDisambiguator()
        comm_type, status, owner, cond, deadline, conf, prompt = disambiguator.analyze_statement(
            "David",
            "We can commit to delivery by next Friday if the customs clearance clears by Tuesday."
        )
        self.assertEqual(comm_type, CommitmentType.CONDITIONAL_COMMITMENT)
        self.assertEqual(status, ActionStatus.BLOCKED_ON_CONDITION)
        self.assertEqual(owner, "David")
        self.assertIn("if the customs clearance clears by Tuesday", cond)
        self.assertIn("by next Friday", deadline)
        self.assertIsNotNone(prompt)

    def test_exploratory_proposal_detection(self):
        disambiguator = ActionDisambiguator()
        comm_type, status, owner, cond, deadline, conf, prompt = disambiguator.analyze_statement(
            "Elena",
            "What if we split the shipment into two 25,000 unit air-freight drops instead?"
        )
        self.assertEqual(comm_type, CommitmentType.EXPLORATORY_PROPOSAL)
        self.assertEqual(status, ActionStatus.INFORMATIONAL_ONLY)

    def test_passive_unowned_task(self):
        disambiguator = ActionDisambiguator()
        comm_type, status, owner, cond, deadline, conf, prompt = disambiguator.analyze_statement(
            "Marcus",
            "Someone needs to follow up with the lab in Vietnam."
        )
        self.assertEqual(comm_type, CommitmentType.AMBIGUOUS_PASSIVE)
        self.assertEqual(status, ActionStatus.NEEDS_HUMAN_CLARIFICATION)
        self.assertIsNone(owner)
        self.assertIn("Who should own this?", prompt)

    def test_ai_agent_chain_of_thought_and_coreference(self):
        turns = TranscriptParser.parse_text(
            "[00:01] Marcus: We need to finalize the Nike Air Zoom 50k batch PO.\n"
            "[00:05] David: I can deliver it by next Friday if the lab clears batch 4."
        )
        ai_agent = AIAgentEngine()
        output = ai_agent.analyze_dialogue_with_context(turns, candidate_turn_index=1)
        self.assertIn("thought_trace", output)
        self.assertEqual(output["commitment_type"], "CONDITIONAL_COMMITMENT")
        self.assertEqual(output["status"], "BLOCKED_ON_CONDITION")

    def test_end_to_end_extractor(self):
        guard = OtterActionGuard()
        sample = (
            "[00:01] Sarah: I will review the lab results by Friday.\n"
            "[00:05] Dave: We will ship batch 3 only if QA passes the audit.\n"
            "[00:10] John: What if we change the packaging?\n"
        )
        result = guard.process_transcript(sample)
        self.assertEqual(result.total_turns, 3)
        self.assertGreaterEqual(result.ready_count, 1)
        self.assertGreaterEqual(result.blocked_count, 1)
        self.assertGreaterEqual(len(result.mcp_payloads), 2)


if __name__ == "__main__":
    unittest.main()
