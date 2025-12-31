"""ASR service for HSIE EntryPoint layer.

This service performs speech-to-text transcription from audio files.
It does not perform any analysis, judgment, or interpretation.
This is a skeleton implementation that does not use any specific ASR technology
(Whisper, Google, Azure, etc.) to allow for future flexibility.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .audio_metadata_service import AudioMetadata


class ASRSegment(BaseModel):
    """ASR segment structure.

    Represents the minimum unit of ASR transcription with time information.
    Each segment corresponds to a portion of the audio with start and end times.

    Attributes:
        segment_id: Unique identifier for the segment (sequential number).
        start_time: Start time of the segment in seconds.
        end_time: End time of the segment in seconds.
        text: Transcribed text for this segment.
        speaker_id: Speaker identifier (optional, None in Phase1).
    """

    segment_id: int = Field(..., description="Unique identifier for the segment (sequential number)")
    start_time: float = Field(..., description="Start time of the segment in seconds", ge=0.0)
    end_time: float = Field(..., description="End time of the segment in seconds", ge=0.0)
    text: str = Field(..., description="Transcribed text for this segment")
    speaker_id: Optional[str] = Field(None, description="Speaker identifier (optional, None in Phase1)")

    model_config = ConfigDict(
        frozen=True,  # Make the segment immutable
        validate_assignment=True,
    )


class ASRResult(BaseModel):
    """ASR result structure.

    Represents the complete output of ASR transcription.
    Contains the full transcript and time-aligned segments.
    This structure holds only the transcription result without any analysis or judgment.

    Attributes:
        asr_id: Unique identifier for this ASR execution (UUID).
        audio_id: Audio identifier from AudioMetadata (UUID).
        language: Language code used for ASR model selection.
        transcript: Full transcription text of the entire audio.
        segments: List of time-aligned segments (can be empty list).
        created_at: Timestamp when ASR was executed.
        engine_name: Name of the ASR engine used (e.g., "whisper").
        model_name: Name of the ASR model used (e.g., "base").
    """

    asr_id: UUID = Field(..., description="Unique identifier for this ASR execution (UUID)")
    audio_id: UUID = Field(..., description="Audio identifier from AudioMetadata (UUID)")
    language: str = Field(..., description="Language code used for ASR model selection")
    transcript: str = Field(..., description="Full transcription text of the entire audio")
    segments: list[ASRSegment] = Field(default_factory=list, description="List of time-aligned segments (can be empty)")
    created_at: datetime = Field(..., description="Timestamp when ASR was executed")
    engine_name: Optional[str] = Field(None, description="Name of the ASR engine used (e.g., 'whisper')")
    model_name: Optional[str] = Field(None, description="Name of the ASR model used (e.g., 'base')")

    model_config = ConfigDict(
        frozen=True,  # Make the result immutable
        validate_assignment=True,
        protected_namespaces=(),  # Allow model_name field without conflict
    )


class ASRService:
    """Service for performing speech-to-text transcription.

    This service provides an abstract interface for ASR processing.
    It does not perform any analysis, judgment, or interpretation.
    Only transcription is performed.

    Design Philosophy:
        - EntryPoint layer responsibility: Convert audio to text only
        - No analysis: Does not judge content, context, or meaning
        - Technology agnostic: Skeleton implementation allows future replacement
          with specific ASR technologies (Whisper, Google, Azure, etc.)
        - Extensible: Concrete implementations can inherit from this base class

    Future Implementation:
        - WhisperASRService(ASRService) can be added for Whisper integration
        - GoogleASRService(ASRService) can be added for Google Cloud Speech
        - AzureASRService(ASRService) can be added for Azure Speech Services
    """

    def transcribe(
        self,
        audio_metadata: AudioMetadata,
        language: str,
    ) -> ASRResult:
        """Perform speech-to-text transcription.

        This method must not perform any analysis or judgment.
        It only converts audio to text transcription.

        Args:
            audio_metadata: AudioMetadata object containing audio information.
            language: Language code for ASR model selection (e.g., "ja", "en").

        Returns:
            ASRResult: Structured ASR result containing transcript and segments.

        Raises:
            NotImplementedError: This is a skeleton implementation.
                Concrete implementations should override this method.
        """
        # Skeleton implementation: Raise NotImplementedError
        # Alternative: Return dummy implementation with empty transcript and segments
        # For now, we raise NotImplementedError to make it explicit that
        # this is a placeholder for future implementation

        raise NotImplementedError(
            "ASRService.transcribe() is a skeleton implementation. "
            "Concrete ASR service implementations (e.g., WhisperASRService) "
            "should override this method."
        )

