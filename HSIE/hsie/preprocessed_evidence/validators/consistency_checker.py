from decimal import Decimal

from hsie.preprocessed_evidence.dto.builder import PreprocessedEvidenceDTO


class ConsistencyChecker:
    def validate(
        self,
        dto: PreprocessedEvidenceDTO,
    ) -> None:
        self._validate_duration(dto)
        self._validate_sampling_rate(dto)
        self._validate_waveform(dto)
        self._validate_speakers(dto)
        self._validate_utterances(dto)

    # -------------------------
    # Duration / Sampling Rate
    # -------------------------

    def _validate_duration(self, dto: PreprocessedEvidenceDTO) -> None:
        duration: Decimal = dto.source_reference.duration

        if duration <= 0:
            raise ValueError("duration must be greater than 0")

    def _validate_sampling_rate(self, dto: PreprocessedEvidenceDTO) -> None:
        sampling_rate: int = dto.source_reference.sampling_rate

        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be greater than 0")

    # -------------------------
    # Waveform
    # -------------------------

    def _validate_waveform(self, dto: PreprocessedEvidenceDTO) -> None:
        waveform = dto.audio.waveform

        if waveform.sampling_rate <= 0:
            raise ValueError("waveform sampling_rate must be greater than 0")

        for value in waveform.values:
            if not isinstance(value, float):
                raise ValueError("waveform values must be float")

        for value in waveform.ui_downsampled_values:
            if not isinstance(value, float):
                raise ValueError("ui_downsampled_values must be float")

    # -------------------------
    # Speaker consistency
    # -------------------------

    def _validate_speakers(self, dto: PreprocessedEvidenceDTO) -> None:
        speaker_ids = [speaker.speaker_id for speaker in dto.speakers]

        if len(speaker_ids) != len(set(speaker_ids)):
            raise ValueError("duplicate speaker_id detected")

    # -------------------------
    # Utterance consistency
    # -------------------------

    def _validate_utterances(self, dto: PreprocessedEvidenceDTO) -> None:
        duration: Decimal = dto.source_reference.duration
        speaker_ids = {speaker.speaker_id for speaker in dto.speakers}

        utterance_ids = []

        for utterance in dto.utterances:
            # ID duplication check
            utterance_ids.append(utterance.utterance_id)

            # Time checks
            if utterance.start_time < 0:
                raise ValueError("utterance start_time must be >= 0")

            if utterance.end_time < 0:
                raise ValueError("utterance end_time must be >= 0")

            if utterance.start_time >= utterance.end_time:
                raise ValueError("utterance start_time must be < end_time")

            if utterance.end_time > duration:
                raise ValueError("utterance end_time exceeds duration")

            # Speaker reference check
            if (
                utterance.speaker_id is not None
                and utterance.speaker_id not in speaker_ids
            ):
                raise ValueError("utterance references unknown speaker_id")

        if len(utterance_ids) != len(set(utterance_ids)):
            raise ValueError("duplicate utterance_id detected")