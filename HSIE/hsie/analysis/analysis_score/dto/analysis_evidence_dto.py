from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AnalysisEvidenceDTO:
    utterance_id: str
    speaker_id: str
    start_time: float
    end_time: float
    text: str
    score: float
    categories: Tuple[str, ...]
