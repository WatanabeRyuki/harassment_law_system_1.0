from dataclasses import dataclass
from typing import List

from .utterance_dto import UtteranceDTO


@dataclass(frozen=True)
class TurnDTO:
    """
    ターン単位DTO（TurnDetectionの出力）
    """
    speaker_id: str
    start_time: float
    end_time: float
    utterances: List[UtteranceDTO]