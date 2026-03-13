"""EntryPoint JSON / Preprocess input DTOs."""

from dataclasses import dataclass
from typing import Any, List
from uuid import UUID


@dataclass
class SegmentDTO:
    """ASR segment from EntryPoint asr_result.segments."""

    segment_id: int
    start_time: float
    end_time: float
    text: str
    speaker_id: str


@dataclass
class UtteranceUnitDTO:
    """Utterance unit from EntryPoint utterance_units."""

    utterance_id: str
    speaker_id: str
    text: str
    start_time: float
    end_time: float


@dataclass
class RawEntryPointJSONDTO:
    """Raw EntryPoint JSON structure (parsed from JSON)."""

    evidence_id: str
    context_id: str
    audio_id: str
    version: str
    audio_path: str
    language: str
    asr_segments: List[SegmentDTO]
    utterance_units: List[UtteranceUnitDTO]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RawEntryPointJSONDTO":
        """Parse raw JSON dict into DTO."""
        ctx = data.get("context") or {}
        asr = data.get("asr_result") or {}
        units = data.get("utterance_units") or []

        evidence_id = str(data.get("evidence_id", ""))
        context_id = str(ctx.get("context_id", ""))
        audio_id = str(ctx.get("audio_id", ""))
        version = str(data.get("version", "v1"))
        audio_path = str(ctx.get("audio_path", ""))
        language = str(ctx.get("language", "ja"))

        segments_raw = asr.get("segments") or []
        asr_segments = [
            SegmentDTO(
                segment_id=s.get("segment_id", i),
                start_time=float(s.get("start_time", 0)),
                end_time=float(s.get("end_time", 0)),
                text=str(s.get("text", "")),
                speaker_id=str(s.get("speaker_id", "speaker_0")),
            )
            for i, s in enumerate(segments_raw)
        ]

        utterance_units = [
            UtteranceUnitDTO(
                utterance_id=str(u.get("utterance_id", "")),
                speaker_id=str(u.get("speaker_id", "speaker_0")),
                text=str(u.get("text", "")),
                start_time=float(u.get("start_time", 0)),
                end_time=float(u.get("end_time", 0)),
            )
            for u in units
        ]

        return cls(
            evidence_id=evidence_id,
            context_id=context_id,
            audio_id=audio_id,
            version=version,
            audio_path=audio_path,
            language=language,
            asr_segments=asr_segments,
            utterance_units=utterance_units,
        )


@dataclass
class PreprocessInputBundleDTO:
    """Bundle of inputs for the preprocess pipeline."""

    evidence_id: str
    context_id: str
    audio_id: str
    version: str
    audio_path: str
    language: str
    asr_segments: List[SegmentDTO]
    utterance_units: List[UtteranceUnitDTO]
