from .dto.analysis_score_input_dto import AnalysisScoreInputDTO
from .dto.analysis_score_result_dto import AnalysisScoreResultDTO

from .mapper import to_speaker_input, to_result_dto
from .weight_selector import select_weights
from .score_calculator import calculate_hsi
from .evidence_filter import filter_by_speaker


def analyze(input_dto: AnalysisScoreInputDTO) -> AnalysisScoreResultDTO:

    language_result = input_dto.language_result
    structure_results = input_dto.structure_results

    speaker_results = {}

    for speaker_id in structure_results.keys():

        # ① Speaker単位入力生成
        speaker_input = to_speaker_input(
            speaker_id,
            language_result,
            structure_results
        )

        # ② 重み決定
        alpha, beta, condition = select_weights(speaker_input)

        # ③ スコア算出
        hsi = calculate_hsi(
            speaker_input.structure_score,
            speaker_input.language_score,
            alpha,
            beta
        )

        # ④ Evidence抽出
        evidences = filter_by_speaker(
            language_result.evidences,
            speaker_id
        )

        # ⑤ DTO組み立て
        speaker_result = to_result_dto(
            speaker_id,
            hsi,
            speaker_input,
            evidences,
            alpha,
            beta,
            condition
        )

        speaker_results[speaker_id] = speaker_result

    return AnalysisScoreResultDTO(speaker_results=speaker_results)

