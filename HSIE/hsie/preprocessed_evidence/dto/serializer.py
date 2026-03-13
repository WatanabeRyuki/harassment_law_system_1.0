"""PreprocessedEvidence DTO to JSON-serializable dict."""

from decimal import Decimal
from uuid import UUID

from hsie.preprocessed_evidence.dto.builder import PreprocessedEvidenceDTO


def _decimal_to_float(d: Decimal) -> float:
    return float(d)


def _serialize(dto: PreprocessedEvidenceDTO) -> dict:
    """Convert PreprocessedEvidenceDTO to JSON-serializable dict."""
    return {
        "evidence_metadata": {
            "evidence_id": str(dto.evidence_metadata.evidence_id),
            "context_id": str(dto.evidence_metadata.context_id),
            "version": dto.evidence_metadata.version,
        },
        "source_reference": {
            "audio_id": str(dto.source_reference.audio_id),
            "sampling_rate": dto.source_reference.sampling_rate,
            "duration": _decimal_to_float(dto.source_reference.duration),
        },
        "audio": {
            "waveform": {
                "values": dto.audio.waveform.values,
                "sampling_rate": dto.audio.waveform.sampling_rate,
                "ui_downsampled_values": dto.audio.waveform.ui_downsampled_values,
            }
        },
        "speakers": [{"speaker_id": s.speaker_id} for s in dto.speakers],
        "utterances": [
            {
                "utterance_id": u.utterance_id,
                "speaker_id": u.speaker_id,
                "text": u.text,
                "start_time": _decimal_to_float(u.start_time),
                "end_time": _decimal_to_float(u.end_time),
            }
            for u in dto.utterances
        ],
        "alignment": {
            "time_base": dto.alignment.time_base,
        },
        "management": {
            "version": dto.management.version,
            "build_timestamp": dto.management.build_timestamp.isoformat(),
        },
    }
