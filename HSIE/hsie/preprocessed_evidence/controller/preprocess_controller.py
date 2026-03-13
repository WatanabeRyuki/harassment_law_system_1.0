"""Preprocessed Evidence pipeline controller."""

import logging
from pathlib import Path
from typing import Any, Union
from uuid import UUID

from hsie.preprocessed_evidence.adapters.entrypoint_adapter import EntrypointAdapter
from hsie.preprocessed_evidence.asr_postprocess.service import ASRPostprocessService
from hsie.preprocessed_evidence.diarization.mapper import DiarizationMapper
from hsie.preprocessed_evidence.diarization.service import DiarizationService
from hsie.preprocessed_evidence.waveform.service import WaveformService
from hsie.preprocessed_evidence.waveform.mapper import WaveformMapper
from hsie.preprocessed_evidence.structuring.aligner import Aligner
from hsie.preprocessed_evidence.structuring.builder import Builder
from hsie.preprocessed_evidence.validators.consistency_checker import ConsistencyChecker
from hsie.preprocessed_evidence.dto.asr import ASRPostProcessInputDTO, UtteranceDTO
from hsie.preprocessed_evidence.dto.diarization import (
    DiarizationInputDTO,
    DiarizationOutputDTO,
)
from hsie.preprocessed_evidence.dto.waveform import WaveformInputDTO
from hsie.preprocessed_evidence.dto.alignment import AlignmentInputDTO
from hsie.preprocessed_evidence.dto.builder import BuilderInputDTO
from hsie.preprocessed_evidence.dto.serializer import _serialize

logger = logging.getLogger(__name__)


class PreprocessController:
    """Orchestrates the Preprocessed Evidence pipeline."""

    def __init__(
        self,
        adapter: EntrypointAdapter,
        asr_service: ASRPostprocessService,
        diarization_service: DiarizationService,
        diarization_mapper: DiarizationMapper,
        waveform_service: WaveformService,
        waveform_mapper: WaveformMapper,
        aligner: Aligner,
        builder: Builder,
        checker: ConsistencyChecker,
    ):
        self.adapter = adapter
        self.asr_service = asr_service
        self.diarization_service = diarization_service
        self.diarization_mapper = diarization_mapper
        self.waveform_service = waveform_service
        self.waveform_mapper = waveform_mapper
        self.aligner = aligner
        self.builder = builder
        self.checker = checker

    def run_diarization(
        self,
        audio_path: Union[str, Path],
    ) -> DiarizationOutputDTO:
        """Extract speaker segments from audio."""
        input_dto = DiarizationInputDTO(audio_path=audio_path)
        annotation = self.diarization_service.segment(input_dto)
        return self.diarization_mapper.to_output_dto(annotation)

    def execute(self, raw_json: Any) -> dict[str, Any]:
        """
        Run the full pipeline: adapt -> ASR -> diarization -> waveform -> align -> build -> validate.
        """
        adapted_dto = self.adapter.adapt(raw_json)

        # ASR postprocess
        asr_input = ASRPostProcessInputDTO(
            utterances=[
                UtteranceDTO(
                    utterance_id=u.utterance_id,
                    speaker_id=u.speaker_id,
                    text=u.text,
                    start_time=u.start_time,
                    end_time=u.end_time,
                )
                for u in adapted_dto.utterance_units
            ],
            language=adapted_dto.language,
        )
        asr_result = self.asr_service.correct(asr_input)

        # Diarization
        diarization_result = self.run_diarization(adapted_dto.audio_path)

        # Waveform
        waveform_input = WaveformInputDTO(audio_path=adapted_dto.audio_path)
        wav_values, sampling_rate, duration = self.waveform_service.decode(waveform_input)
        waveform_result = self.waveform_mapper.to_output_dto(
            waveform_values=wav_values,
            sampling_rate=sampling_rate,
            duration=duration,
        )

        # Alignment
        alignment_input = AlignmentInputDTO(
            corrected_utterances=asr_result.corrected_utterances,
            speaker_segments=diarization_result.speaker_segments,
        )
        aligned = self.aligner.align(alignment_input)

        # Build
        builder_input = BuilderInputDTO(
            evidence_id=UUID(adapted_dto.evidence_id),
            context_id=UUID(adapted_dto.context_id),
            audio_id=UUID(adapted_dto.audio_id),
            version=adapted_dto.version,
            aligned_utterances=aligned.aligned_utterances,
            waveform=waveform_result.waveform,
            sampling_rate=waveform_result.sampling_rate,
            duration=waveform_result.duration,
        )
        final_dto = self.builder.build(builder_input)

        # Validate
        self.checker.validate(final_dto)

        return _serialize(final_dto)
