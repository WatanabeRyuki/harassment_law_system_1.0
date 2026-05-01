# hsie/run_test.py

from hsie.hsi_result.dto.hsi_result_input_dto import (
    HSIResultInputDTO,
    AnalysisEvidenceDTO
)
from hsie.hsi_result.hsi_result_analyzer import HSIResultAnalyzer
from hsie.hsi_result.debug_ui import render_result


# -----------------------------
# ■ ダミーデータ生成
# -----------------------------

def create_test_input() -> HSIResultInputDTO:

    evidences = [
        AnalysisEvidenceDTO(
            utterance_id="u1",
            speaker_id="speaker_0",
            start_time=0.0,
            end_time=2.0,
            text="提示するだけじゃ意味ないって分かる？実行できないなら意味ないから。",
            score=100.0,
            categories=("D_a", "D_v")
        ),
        AnalysisEvidenceDTO(
            utterance_id="u2",
            speaker_id="speaker_0",
            start_time=2.0,
            end_time=4.0,
            text="あー、やっぱりね。そのレベルならこんなもんか。",
            score=94.62,
            categories=("I_dir", "D_p", "D_a", "D_v")
        ),
        AnalysisEvidenceDTO(
            utterance_id="u3",
            speaker_id="speaker_0",
            start_time=4.0,
            end_time=6.0,
            text="いや修正とか以前にさ、基礎ができてないよね。",
            score=77.43,
            categories=("I_ind", "D_a")
        ),
    ]

    return HSIResultInputDTO(
        speaker_id="speaker_0",

        hsi_score=82.14,

        language_score=76.16,
        structure_score=83.63,

        turn_occupancy=0.71,
        interruption_rate=0.0,
        negation_score=0.06,
        sai_score=0.03,

        evidences=evidences,

        applied_condition="S_highest",
        alpha=0.8,
        beta=0.2
    )


# -----------------------------
# ■ 実行
# -----------------------------

def main():
    input_dto = create_test_input()

    result = HSIResultAnalyzer.execute(input_dto)

    render_result(result)


if __name__ == "__main__":
    main()