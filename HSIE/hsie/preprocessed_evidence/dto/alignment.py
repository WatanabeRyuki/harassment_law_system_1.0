"""Alignment DTOs."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List

from hsie.preprocessed_evidence.dto.asr import CorrectedUtteranceDTO
from hsie.preprocessed_evidence.dto.diarization import SpeakerSegmentDTO


@dataclass
class AlignedUtteranceDTO:
    """Aligned utterance with speaker assignment."""

    utterance_id: str
    speaker_id: str | None
    start_time: Decimal
    end_time: Decimal
    text: str


@dataclass
class AlignmentInputDTO:
    """Input for the aligner."""

    corrected_utterances: List[CorrectedUtteranceDTO]
    speaker_segments: List[SpeakerSegmentDTO]


@dataclass
class AlignmentOutputDTO:
    """Output from the aligner."""

    aligned_utterances: List[AlignedUtteranceDTO]
