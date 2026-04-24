from .dto.speaker_score_input_dto import SpeakerScoreInputDTO
from .dto.speaker_analysis_score_dto import SpeakerAnalysisScoreDTO
from .dto.analysis_evidence_dto import AnalysisEvidenceDTO


def to_speaker_input(speaker_id, language_result, structure_results):
    structure_result = structure_results[speaker_id]
    return SpeakerScoreInputDTO(
        speaker_id=speaker_id,
        language_score=language_result.speaker_scores.get(speaker_id, 0.0),
        structure_score=structure_result.final_score,
        turn_occupancy=structure_result.turn_occupancy,
        interruption_rate=structure_result.interruption_rate,
        negation_score=structure_result.negation_score,
        sai_score=structure_result.sai_score,
        is_S_reversal=structure_result.used_inversion_logic
    )


def to_result_dto(
    speaker_id,
    hsi,
    speaker_input,
    evidences,
    alpha,
    beta,
    condition
):
    mapped_evidences = [
        AnalysisEvidenceDTO(
            utterance_id=e.utterance_id,
            speaker_id=e.speaker_id,
            start_time=e.start_time,
            end_time=e.end_time,
            text=e.text,
            score=e.score,
            categories=tuple(e.categories),
        )
        for e in evidences
    ]

    return SpeakerAnalysisScoreDTO(
        speaker_id=speaker_id,
        hsi_score=hsi,
        language_score=speaker_input.language_score,
        structure_score=speaker_input.structure_score,
        turn_occupancy=speaker_input.turn_occupancy,
        interruption_rate=speaker_input.interruption_rate,
        negation_score=speaker_input.negation_score,
        sai_score=speaker_input.sai_score,
        evidences=mapped_evidences,
        applied_condition=condition,
        alpha=alpha,
        beta=beta
    )