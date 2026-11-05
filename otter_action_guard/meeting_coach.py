from typing import List, Dict, Any
from .models import SpeakerTurn, SpeakerMetric, MeetingCoachSummary


class MeetingCoach:
    """
    Analyzes multi-speaker conversational dynamics, speaking time distributions,
    pacing, and turn-taking behavior. Generates automated coaching feedback
    for presentations, supplier negotiations, and team syncs.
    
    (Built to model presentation coaching and meeting intelligence analytics).
    """

    def analyze(self, turns: List[SpeakerTurn]) -> MeetingCoachSummary:
        if not turns:
            return MeetingCoachSummary(
                speaker_metrics=[],
                pace_wpm_estimate=0,
                interaction_balance_score=0.0,
                coaching_tips=["No speaker turns detected in transcript."]
            )

        speaker_words: Dict[str, int] = {}
        speaker_turns: Dict[str, int] = {}
        speaker_monologues: Dict[str, int] = {}
        total_words = 0

        # Monologue threshold: turns with 35+ words in short dialogue snippets
        MONOLOGUE_WORD_THRESHOLD = 35

        for turn in turns:
            words = [w for w in turn.text.strip().split() if w]
            count = len(words)
            speaker = turn.speaker

            speaker_words[speaker] = speaker_words.get(speaker, 0) + count
            speaker_turns[speaker] = speaker_turns.get(speaker, 0) + 1
            total_words += count

            if count >= MONOLOGUE_WORD_THRESHOLD:
                speaker_monologues[speaker] = speaker_monologues.get(speaker, 0) + 1

        # Calculate metrics per speaker
        metrics: List[SpeakerMetric] = []
        for speaker, words in speaker_words.items():
            pct = round((words / total_words) * 100, 1) if total_words > 0 else 0.0
            metrics.append(
                SpeakerMetric(
                    speaker=speaker,
                    word_count=words,
                    talk_time_pct=pct,
                    turn_count=speaker_turns.get(speaker, 0),
                    monologue_count=speaker_monologues.get(speaker, 0)
                )
            )

        # Sort by talk time percentage descending
        metrics.sort(key=lambda m: m.talk_time_pct, reverse=True)

        # Estimate interaction balance score (Gini-like balance, 1.0 = perfectly even)
        num_speakers = len(metrics)
        if num_speakers <= 1:
            balance_score = 0.5
        else:
            ideal_pct = 100.0 / num_speakers
            variance = sum(abs(m.talk_time_pct - ideal_pct) for m in metrics) / (200.0)
            balance_score = round(max(0.1, 1.0 - variance), 2)

        # Generate rule-augmented AI coaching tips
        coaching_tips: List[str] = []

        top_speaker = metrics[0]
        if top_speaker.talk_time_pct > 60.0:
            coaching_tips.append(
                f"High talk-time concentration: {top_speaker.speaker} held {top_speaker.talk_time_pct}% of the dialogue. Encourage more inter-team participation."
            )
        elif 30.0 <= top_speaker.talk_time_pct <= 50.0:
            coaching_tips.append(
                f"Healthy negotiation balance: Leading participant ({top_speaker.speaker}) spoke {top_speaker.talk_time_pct}% of the time, allowing active two-way engagement."
            )

        monologue_speakers = [m for m in metrics if m.monologue_count > 0]
        if monologue_speakers:
            names = ", ".join(m.speaker for m in monologue_speakers)
            coaching_tips.append(
                f"Pacing check: Detected extended turns (>35 words) by {names}. Consider introducing check-in pauses for participant questions."
            )
        else:
            coaching_tips.append(
                "Crisp turn-taking: All participants communicated in concise, conversational segments without dominant monologues."
            )

        if len(metrics) >= 3:
            coaching_tips.append(
                f"Multi-party inclusion: All {len(metrics)} stakeholders contributed actively to operational decision-making."
            )

        return MeetingCoachSummary(
            speaker_metrics=metrics,
            pace_wpm_estimate=145,  # Standard conversational baseline
            interaction_balance_score=balance_score,
            coaching_tips=coaching_tips
        )
