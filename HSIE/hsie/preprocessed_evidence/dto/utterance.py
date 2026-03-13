"""Final utterance DTO."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class FinalUtteranceDTO:
    """Final utterance in preprocessed evidence."""

    utterance_id: str
    speaker_id: Optional[str]
    text: str
    start_time: Decimal
    end_time: Decimal
