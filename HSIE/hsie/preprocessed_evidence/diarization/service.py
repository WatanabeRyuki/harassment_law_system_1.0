from pyannote.audio import Pipeline

from hsie.preprocessed_evidence.dto.diarization import (
    DiarizationInputDTO,
)


class DiarizationService:
    def __init__(
        self,
        pipeline: Pipeline,
    ) -> None:
        self._pipeline = pipeline

    def segment(
        self,
        input_dto: DiarizationInputDTO,
    ):
        """
        Execute speaker diarization.

        Args:
            input_dto: diarization input DTO

        Returns:
            pyannote diarization result
        """

        audio_path = input_dto.audio_path

        diarization = self._pipeline(audio_path)

        return diarization