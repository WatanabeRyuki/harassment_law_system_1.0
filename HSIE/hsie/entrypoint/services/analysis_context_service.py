"""Analysis context service for HSIE EntryPoint layer.

This service builds an AnalysisContext by bundling AudioMetadata, ASRResult,
and input parameters into a single snapshot structure.
It does not perform any analysis, judgment, or interpretation.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .asr_service import ASRResult
from .audio_metadata_service import AudioMetadata


class AnalysisContext(BaseModel):
    """Analysis context structure.

    This structure represents a snapshot of analysis prerequisites,
    bundling AudioMetadata, ASRResult, and input parameters together.
    It does not contain any analysis results, judgments, or interpretations.
    This is purely a container for the input data required for analysis.

    Attributes:
        context_id: Unique identifier for this analysis context (UUID).
        audio_id: Audio identifier from AudioMetadata (UUID).
        session_id: Conversation session identifier.
        speaker_id: Representative speaker identifier.
        audio_path: Audio file path reference.
        asr_engine: ASR engine name (placeholder).
        asr_version: ASR model version (optional, placeholder).
        language: Language code used for ASR.
        sampling_rate: Sampling frequency in Hz (optional).
        duration: Audio duration in seconds (optional).
        utterance_units: List of utterance units (empty list for now).
        created_at: Timestamp when this context was created.
        status: Status of the context ("CREATED" fixed).
    """

    context_id: UUID = Field(..., description="Unique identifier for this analysis context (UUID)")
    audio_id: UUID = Field(..., description="Audio identifier from AudioMetadata (UUID)")
    session_id: str = Field(..., description="Conversation session identifier")
    speaker_id: str = Field(..., description="Representative speaker identifier")
    audio_path: Path = Field(..., description="Audio file path reference")
    asr_engine: str = Field(..., description="ASR engine name (placeholder)")
    asr_version: Optional[str] = Field(None, description="ASR model version (optional, placeholder)")
    language: str = Field(..., description="Language code used for ASR")
    sampling_rate: Optional[int] = Field(None, description="Sampling frequency in Hz (optional)")
    duration: Optional[float] = Field(None, description="Audio duration in seconds (optional)")
    utterance_units: list = Field(default_factory=list, description="List of utterance units (empty list for now)")
    created_at: datetime = Field(..., description="Timestamp when this context was created")
    status: str = Field(..., description="Status of the context ('CREATED' fixed)")

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make the context immutable
        validate_assignment = True


class AnalysisContextService:
    """Service for building analysis context.

    This service bundles AudioMetadata, ASRResult, and input parameters
    into a single AnalysisContext structure.
    It does not perform any analysis, judgment, or interpretation.
    It only creates a snapshot of the prerequisites for analysis.

    Design Philosophy:
        - EntryPoint layer responsibility: Bundle input data only
        - No analysis: Does not interpret or analyze ASR results
        - No judgment: Does not make any decisions or calculations
        - Snapshot creation: Creates a snapshot of analysis prerequisites
        - Immutable result: Returns an immutable AnalysisContext structure
    """

    def build(
        self,
        audio_metadata: AudioMetadata,
        asr_result: ASRResult,
        session_id: str,
        speaker_id: str,
    ) -> AnalysisContext:
        """Build an AnalysisContext from AudioMetadata, ASRResult, and input parameters.

        This method creates a snapshot of analysis prerequisites by bundling
        the provided data into a single AnalysisContext structure.
        It does not perform any analysis, judgment, or interpretation.

        Args:
            audio_metadata: AudioMetadata object containing audio information.
            asr_result: ASRResult object containing transcription results.
            session_id: Conversation session identifier.
            speaker_id: Representative speaker identifier.

        Returns:
            AnalysisContext: Structured analysis context containing all prerequisites
                for analysis as an immutable snapshot.

        Note:
            - context_id is newly generated for each call
            - asr_engine and asr_version are placeholder values (fixed strings)
            - utterance_units is an empty list (to be structured by ASRResultStructurer)
            - status is fixed to "CREATED"
            - No analysis or interpretation is performed
        """
        # Generate new context_id
        context_id = uuid4()

        # Copy values from audio_metadata
        audio_id = audio_metadata.audio_id
        audio_path = audio_metadata.audio_path
        sampling_rate = audio_metadata.sampling_rate
        duration = audio_metadata.duration

        # Copy values from asr_result
        language = asr_result.language

        # Placeholder values for ASR engine information
        asr_engine = "placeholder"  # Placeholder ASR engine name
        asr_version: Optional[str] = None  # Placeholder ASR version

        # Empty list for utterance_units (to be structured by ASRResultStructurer)
        utterance_units: list = []

        # Set timestamp and status
        created_at = datetime.now()
        status = "CREATED"

        return AnalysisContext(
            context_id=context_id,
            audio_id=audio_id,
            session_id=session_id,
            speaker_id=speaker_id,
            audio_path=audio_path,
            asr_engine=asr_engine,
            asr_version=asr_version,
            language=language,
            sampling_rate=sampling_rate,
            duration=duration,
            utterance_units=utterance_units,
            created_at=created_at,
            status=status,
        )

