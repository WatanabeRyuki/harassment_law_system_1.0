"""EntryPoint JSON adapter."""

from typing import Any

from hsie.preprocessed_evidence.dto.entrypoint import (
    PreprocessInputBundleDTO,
    RawEntryPointJSONDTO,
)


class EntrypointAdapter:
    """Adapts raw EntryPoint JSON into preprocess input DTOs."""

    def adapt(self, raw: dict[str, Any] | RawEntryPointJSONDTO) -> PreprocessInputBundleDTO:
        """Convert EntryPoint JSON (or parsed DTO) into PreprocessInputBundleDTO."""
        if isinstance(raw, dict):
            parsed = RawEntryPointJSONDTO.from_dict(raw)
        else:
            parsed = raw

        return PreprocessInputBundleDTO(
            evidence_id=parsed.evidence_id,
            context_id=parsed.context_id,
            audio_id=parsed.audio_id,
            version=parsed.version,
            audio_path=parsed.audio_path,
            language=parsed.language,
            asr_segments=parsed.asr_segments,
            utterance_units=parsed.utterance_units,
        )
