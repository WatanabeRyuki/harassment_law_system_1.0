from dataclasses import dataclass


@dataclass
class SpeakerScoreInputDTO:
    speaker_id: str
    language_score: float
    structure_score: float
    turn_occupancy: float
    interruption_rate: float
    negation_score: float
    sai_score: float
    is_S_reversal: bool