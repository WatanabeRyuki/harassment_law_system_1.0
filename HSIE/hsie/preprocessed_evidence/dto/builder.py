"""Builder input/output DTOs."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from hsie.preprocessed_evidence.dto.alignment import AlignedUtteranceDTO
from hsie.preprocessed_evidence.dto.audio import AudioDTO
from hsie.preprocessed_evidence.dto.evidence import EvidenceMetadataDTO
from hsie.preprocessed_evidence.dto.management import ManagementDTO
from hsie.preprocessed_evidence.dto.source import SourceReferenceDTO
from hsie.preprocessed_evidence.dto.speaker import SpeakerDTO
from hsie.preprocessed_evidence.dto.utterance import FinalUtteranceDTO
from hsie.preprocessed_evidence.dto.alignment_meta import AlignmentMetaDTO
from hsie.preprocessed_evidence.dto.waveform import WaveformDTO


@dataclass
class BuilderInputDTO:
    """Input for the preprocessed evidence builder."""

    evidence_id: UUID
    context_id: UUID
    audio_id: UUID
    version: str
    aligned_utterances: List[AlignedUtteranceDTO]
    waveform: WaveformDTO
    sampling_rate: int
    duration: Decimal


@dataclass
class PreprocessedEvidenceDTO:
    """Final preprocessed evidence output."""

    evidence_metadata: EvidenceMetadataDTO
    source_reference: SourceReferenceDTO
    audio: AudioDTO
    speakers: List[SpeakerDTO]
    utterances: List[FinalUtteranceDTO]
    alignment: AlignmentMetaDTO
    management: ManagementDTO
