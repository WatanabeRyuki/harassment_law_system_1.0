"""Source reference DTO."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class SourceReferenceDTO:
    """Source reference section."""

    audio_id: UUID
    sampling_rate: int
    duration: Decimal
