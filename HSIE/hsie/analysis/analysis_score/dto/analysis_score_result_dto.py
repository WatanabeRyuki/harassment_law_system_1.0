from dataclasses import dataclass
from typing import Dict

from .speaker_analysis_score_dto import SpeakerAnalysisScoreDTO


@dataclass
class AnalysisScoreResultDTO:
    speaker_results: Dict[str, SpeakerAnalysisScoreDTO]