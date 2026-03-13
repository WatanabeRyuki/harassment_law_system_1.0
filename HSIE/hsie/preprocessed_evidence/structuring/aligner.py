from decimal import Decimal

from hsie.preprocessed_evidence.dto.alignment import (
    AlignmentInputDTO,
    AlignmentOutputDTO,
    AlignedUtteranceDTO,
)
from hsie.preprocessed_evidence.dto.asr import CorrectedUtteranceDTO
from hsie.preprocessed_evidence.dto.diarization import SpeakerSegmentDTO


class Aligner:
    def align(
        self,
        input_dto: AlignmentInputDTO,
    ) -> AlignmentOutputDTO:
        corrected_utterances: list[
            CorrectedUtteranceDTO
        ] = input_dto.corrected_utterances
        speaker_segments: list[
            SpeakerSegmentDTO
        ] = input_dto.speaker_segments

        aligned_utterances: list[AlignedUtteranceDTO] = []

        for utterance in corrected_utterances:
            u_start = (
                utterance.start_time
                if isinstance(utterance.start_time, Decimal)
                else Decimal(str(utterance.start_time))
            )
            u_end = (
                utterance.end_time
                if isinstance(utterance.end_time, Decimal)
                else Decimal(str(utterance.end_time))
            )

            best_speaker_id: str | None = None
            max_overlap: Decimal = Decimal("0")

            for segment in speaker_segments:
                s_start: Decimal = segment.start_time
                s_end: Decimal = segment.end_time

                overlap_start: Decimal = max(u_start, s_start)
                overlap_end: Decimal = min(u_end, s_end)
                overlap: Decimal = overlap_end - overlap_start

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker_id = segment.speaker_id

            aligned = AlignedUtteranceDTO(
                utterance_id=utterance.utterance_id,
                speaker_id=best_speaker_id,
                start_time=u_start,
                end_time=u_end,
                text=utterance.corrected_text,
            )

            aligned_utterances.append(aligned)

        return AlignmentOutputDTO(
            aligned_utterances=aligned_utterances
        )