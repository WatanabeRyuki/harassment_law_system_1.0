"""Audio metadata service for HSIE EntryPoint layer.

This service collects physical and objective metadata from audio files only.
It does not perform any analysis, judgment, or interpretation.
"""

import os
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AudioMetadata(BaseModel):
    """Audio metadata structure.

    This structure contains only physical and objective information
    extracted from audio files. No interpretation or analysis is performed.

    Attributes:
        audio_id: Audio identifier (UUID).
        audio_path: Normalized audio file path.
        duration: Total audio length in seconds.
        sampling_rate: Sampling frequency (Hz).
        audio_format: Audio format (wav, mp3, etc.).
        channel: Channel configuration (mono, stereo, etc.).
        recorded_at: Recorded timestamp (estimated, optional).
    """

    audio_id: UUID = Field(..., description="Audio identifier (UUID)")
    audio_path: Path = Field(..., description="Normalized audio file path")
    duration: Optional[float] = Field(None, description="Total audio length in seconds")
    sampling_rate: Optional[int] = Field(None, description="Sampling frequency (Hz)")
    audio_format: Optional[str] = Field(None, description="Audio format (wav, mp3, etc.)")
    channel: Optional[str] = Field(None, description="Channel configuration (mono, stereo, etc.)")
    recorded_at: Optional[datetime] = Field(None, description="Recorded timestamp (estimated)")

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make the metadata immutable
        validate_assignment = True


class AudioMetadataService:
    """Service for collecting audio metadata.

    This service extracts only physical and objective metadata from audio files.
    It does not perform any analysis, judgment, or interpretation.
    """

    def collect(self, audio_file: Union[Path, str]) -> AudioMetadata:
        """Collect audio metadata from the specified file.

        Args:
            audio_file: Path to the audio file (Path or str).

        Returns:
            AudioMetadata: Structured audio metadata.

        Raises:
            FileNotFoundError: If the audio file does not exist.
            ValueError: If the file cannot be read as an audio file.
        """
        audio_path = Path(audio_file).resolve()

        # Check if file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Generate UUID for audio_id
        audio_id = uuid4()

        # Get audio format from extension
        audio_format = self._get_audio_format(audio_path)

        # Get file modification time as recorded_at (simple estimation)
        recorded_at = self._get_file_timestamp(audio_path)

        # Extract metadata based on format
        duration: Optional[float] = None
        sampling_rate: Optional[int] = None
        channel: Optional[str] = None

        if audio_format == "wav":
            try:
                duration, sampling_rate, channel = self._extract_wav_metadata(audio_path)
            except Exception:
                # If extraction fails, continue with None values
                pass
        # For other formats (mp3, etc.), metadata extraction is limited
        # with standard library only. We leave them as None.

        return AudioMetadata(
            audio_id=audio_id,
            audio_path=audio_path,
            duration=duration,
            sampling_rate=sampling_rate,
            audio_format=audio_format,
            channel=channel,
            recorded_at=recorded_at,
        )

    def _get_audio_format(self, audio_path: Path) -> Optional[str]:
        """Get audio format from file extension.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Audio format string (wav, mp3, etc.) or None.
        """
        ext = audio_path.suffix.lower()
        if ext.startswith("."):
            ext = ext[1:]
        return ext if ext else None

    def _get_file_timestamp(self, audio_path: Path) -> Optional[datetime]:
        """Get file modification timestamp as estimated recorded_at.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Datetime object representing file modification time.
        """
        try:
            mtime = os.path.getmtime(audio_path)
            return datetime.fromtimestamp(mtime)
        except Exception:
            return None

    def _extract_wav_metadata(self, audio_path: Path) -> Tuple[Optional[float], Optional[int], Optional[str]]:
        """Extract metadata from WAV file.

        Args:
            audio_path: Path to the WAV file.

        Returns:
            Tuple of (duration, sampling_rate, channel).
        """
        try:
            with wave.open(str(audio_path), "rb") as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()

                duration = frames / float(sample_rate) if sample_rate > 0 else None
                channel_str = "mono" if channels == 1 else "stereo" if channels == 2 else f"{channels}ch"

                return duration, sample_rate, channel_str
        except Exception:
            # If reading fails, return None values
            return None, None, None

