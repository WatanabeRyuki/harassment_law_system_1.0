"""Audio DTO."""

from dataclasses import dataclass

from hsie.preprocessed_evidence.dto.waveform import WaveformDTO


@dataclass
class AudioDTO:
    """Audio section with waveform data."""

    waveform: WaveformDTO
