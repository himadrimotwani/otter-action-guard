import re
from typing import List
from .models import SpeakerTurn


class TranscriptParser:
    """Parses standard multi-speaker meeting transcript formats (including Otter.ai export formats)."""

    @staticmethod
    def parse_text(raw_text: str) -> List[SpeakerTurn]:
        """
        Parses transcripts formatted like:
        [12:34] Alice: We will prepare the delivery schedule.
        or
        Bob (01:45): Let me check with our supplier first.
        or standard multi-line speaker blocks.
        """
        turns: List[SpeakerTurn] = []
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]

        # Pattern 1: [00:12] Speaker Name: Message
        pattern_bracket = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.*)$")
        # Pattern 2: Speaker Name [00:12]: Message or Speaker Name (00:12): Message
        pattern_paren = re.compile(r"^([^\(\[]+)\s*[\(\[](\d{1,2}:\d{2}(?::\d{2})?)[\)\]]:\s*(.*)$")
        # Pattern 3: Speaker Name: Message
        pattern_simple = re.compile(r"^([A-Za-z\s]+):\s*(.*)$")

        for line in lines:
            m = pattern_bracket.match(line)
            if m:
                ts, speaker, text = m.group(1), m.group(2).strip(), m.group(3).strip()
                turns.append(SpeakerTurn(speaker=speaker, timestamp=ts, text=text))
                continue

            m = pattern_paren.match(line)
            if m:
                speaker, ts, text = m.group(1).strip(), m.group(2), m.group(3).strip()
                turns.append(SpeakerTurn(speaker=speaker, timestamp=ts, text=text))
                continue

            m = pattern_simple.match(line)
            if m:
                speaker, text = m.group(1).strip(), m.group(2).strip()
                turns.append(SpeakerTurn(speaker=speaker, timestamp="00:00", text=text))
                continue

            # Fallback if line is continuation
            if turns:
                turns[-1].text += f" {line}"
            else:
                turns.append(SpeakerTurn(speaker="Unknown", timestamp="00:00", text=line))

        return turns
