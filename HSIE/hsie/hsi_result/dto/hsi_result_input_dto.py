# hsie/hsi_result/dto/hsi_result_input_dto.py

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class AnalysisEvidenceDTO:
    utterance_id: str
    speaker_id: str
    start_time: float
    end_time: float
    text: str
    score: float
    categories: Tuple[str, ...]


@dataclass
class HSIResultInputDTO:

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