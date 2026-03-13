from decimal import Decimal

from hsie.preprocessed_evidence.dto.waveform import (
    WaveformDTO,
    WaveformOutputDTO,
)
from hsie.preprocessed_evidence.waveform.ui_converter import (
    WaveformUIConverter,
)


class WaveformMapper:
    def __init__(
        self,
        ui_converter: WaveformUIConverter,
    ) -> None:
        self._ui_converter = ui_converter

    def to_output_dto(
        self,
        waveform_values: list[float],
        sampling_rate: int,
        duration: Decimal,
    ) -> WaveformOutputDTO:
        ui_values: list[float] = self._ui_converter.convert(
            waveform_values,
            sampling_rate,
        )

        # Store a size-limited waveform representation to avoid huge JSON payloads.
        # We reuse the UI downsampled values as the persisted waveform values so that
        # audio.waveform.values and audio.waveform.ui_downsampled_values are both
        # bounded by the converter's max_points.
        stored_values: list[float] = ui_values

        waveform_dto: WaveformDTO = WaveformDTO(
            values=stored_values,
            sampling_rate=sampling_rate,
            ui_downsampled_values=ui_values,
        )

        return WaveformOutputDTO(
            waveform=waveform_dto,
            sampling_rate=sampling_rate,
            duration=duration,
        )