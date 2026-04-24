from dataclasses import dataclass
from typing import List

from .analysis_evidence_dto import AnalysisEvidenceDTO


@dataclass
class SpeakerAnalysisScoreDTO:
    speaker_id: str

    hsi_score: float

    language_score: float
    structure_score: float
    turn_occupancy: float
    interruption_rate: float
    negation_score: float
    sai_score: float

    evidences: List[AnalysisEvidenceDTO]

    applied_condition: str
    alpha: float
    beta: float