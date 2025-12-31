"""Whisper ASR service for HSIE EntryPoint layer.

This service performs speech-to-text transcription using OpenAI Whisper (open-source).
It does not perform any analysis, judgment, or interpretation.
Only mechanical transcription is performed.

Design Philosophy:
    - EntryPoint layer responsibility: Convert audio to text only
    - No analysis: Does not judge content, context, or meaning
    - Mechanical processing: Only reproducible, mechanical transcription
    - Technology: Uses open-source Whisper (local execution)
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import whisper

from .asr_service import ASRResult, ASRSegment, ASRService
from .audio_metadata_service import AudioMetadata

logger = logging.getLogger(__name__)


class WhisperASRService(ASRService):
    """Service for performing speech-to-text transcription using Whisper.

    This service uses OpenAI Whisper (open-source) to transcribe audio files.
    It performs only mechanical transcription without any analysis or judgment.

    Design Philosophy:
        - EntryPoint layer responsibility: Convert audio to text only
        - No analysis: Does not interpret meaning, combine sentences, or remove fillers
        - Mechanical processing: Only reproducible, mechanical transcription
        - Technology: Uses open-source Whisper (local execution)
        - No exception swallowing: All exceptions are propagated to the caller

    Attributes:
        model_name: Name of the Whisper model to use (default: "base").
    """

    def __init__(self, model_name: str = "large") -> None:
        """Initialize WhisperASRService.

        Args:
            model_name: Name of the Whisper model to use (default: "base").
                Valid options: "tiny", "base", "small", "medium", "large".
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> whisper.Whisper:
        """Load Whisper model (lazy loading).

        Returns:
            Loaded Whisper model instance.

        Raises:
            RuntimeError: If model loading fails.
        """
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def transcribe(
        self,
        audio_metadata: AudioMetadata,
        language: str,
    ) -> ASRResult:
        """Perform speech-to-text transcription using Whisper.

        This method performs only mechanical transcription without any analysis or judgment.
        It converts audio to text and structures the result into ASRResult.

        Args:
            audio_metadata: AudioMetadata object containing audio information.
            language: Language code for ASR model selection (e.g., "ja", "en").
                If None or empty, Whisper will auto-detect the language.

        Returns:
            ASRResult: Structured ASR result containing transcript and segments.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            RuntimeError: If Whisper model loading or transcription fails.
            ValueError: If the audio file cannot be processed.
            Any other exception from Whisper is propagated as-is.
        """
        # Validate audio file exists
        audio_path = audio_metadata.audio_path
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load Whisper model
        model = self._load_model()

        # Prepare language parameter for Whisper
        # If language is None or empty, Whisper will auto-detect
        whisper_language = language if language and language.strip() else None

        # Perform transcription using Whisper
        logger.info(f"Transcribing audio: {audio_path} (language: {whisper_language})")
        result = model.transcribe(
            str(audio_path),
            language=whisper_language,
        )

        # Extract transcript
        transcript = result.get("text", "").strip()

        # Convert Whisper segments to ASRSegment
        segments = self._convert_segments(
            whisper_segments=result.get("segments", []),
            audio_metadata=audio_metadata,
        )

        # Sort segments by start_time (ascending)
        segments.sort(key=lambda s: s.start_time)

        # Generate ASR ID
        asr_id = uuid4()

        # Create ASRResult
        asr_result = ASRResult(
            asr_id=asr_id,
            audio_id=audio_metadata.audio_id,
            language=language,
            transcript=transcript,
            segments=segments,
            created_at=datetime.now(timezone.utc),
            engine_name="whisper",
            model_name=self.model_name,
        )

        logger.info(f"Transcription completed: {len(segments)} segments")
        return asr_result

    def _convert_segments(
        self,
        whisper_segments: list[dict],
        audio_metadata: AudioMetadata,
    ) -> list[ASRSegment]:
        """Convert Whisper segments to ASRSegment objects.

        This method performs only mechanical conversion without any analysis or judgment.
        It converts Whisper's segment structure to ASRSegment DTOs.

        Args:
            whisper_segments: List of Whisper segment dictionaries.
            audio_metadata: AudioMetadata object for speaker_id determination.

        Returns:
            List of ASRSegment objects.
        """
        segments = []
        speaker_id = self._get_speaker_id(audio_metadata)
        segment_id = 0

        for whisper_seg in whisper_segments:
            # Extract segment information
            start_time = float(whisper_seg.get("start", 0.0))
            end_time = float(whisper_seg.get("end", 0.0))
            text = whisper_seg.get("text", "").strip()

            # Skip empty segments
            if not text:
                continue

            # Create ASRSegment with sequential segment_id
            segment = ASRSegment(
                segment_id=segment_id,
                start_time=start_time,
                end_time=end_time,
                text=text,
                speaker_id=speaker_id,
            )
            segments.append(segment)
            segment_id += 1

        return segments

    def _get_speaker_id(self, audio_metadata: AudioMetadata) -> str:
        """Get speaker ID for Phase1.

        In Phase1, speaker_id is fixed. This method determines the speaker_id
        from audio_metadata or uses a default value.

        Args:
            audio_metadata: AudioMetadata object.

        Returns:
            Speaker ID string (default: "speaker_0").
        """
        # Phase1: Use fixed speaker_id
        # If audio_metadata has speaker information, use it
        # Otherwise, use default "speaker_0"
        # For now, we use "speaker_0" as default
        return "speaker_0"

