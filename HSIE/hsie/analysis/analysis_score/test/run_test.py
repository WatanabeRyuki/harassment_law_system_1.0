import os
import json

from analysis.analysis_score.analysis_score_analyzer import analyze
from analysis.analysis_score.dto.analysis_score_input_dto import AnalysisScoreInputDTO
from analysis.analysis_score.debug import debug_print_result

# DTO
from analysis.language.dto.language_result_dto import LanguageResultDTO
from analysis.structure.dto.structure_result_dto import StructureResultDTO
from analysis.language.dto.evidence_dto import EvidenceDTO


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_language_result(data):
    evidences = [
        EvidenceDTO(**e) for e in data.get("evidences", [])
    ]

    return LanguageResultDTO(
        speaker_scores=data["speaker_scores"],
        total_score=data["total_score"],
        evidences=evidences,
        conversation_duration=data.get("conversation_duration", 0.0)
    )


def parse_structure_results(data):
    results = {}

    for speaker_id, s in data.items():
        results[speaker_id] = StructureResultDTO(
            speaker_id=speaker_id,
            s_raw=s["s_raw"],
            c=s["c"],
            x=s["x"],
            final_score=s["final_score"],
            turn_occupancy=s.get("turn_occupancy", 0.0),
            interruption_rate=s.get("interruption_rate", 0.0),
            negation_score=s.get("negation_score", 0.0),
            sai_score=s["sai_score"],
            used_inversion_logic=s["used_inversion_logic"]
        )

    return results


def run_test(json_path, debug=False):
    data = load_json(json_path)

    language_result = parse_language_result(data["language_result"])
    structure_results = parse_structure_results(data["structure_results"])

    input_dto = AnalysisScoreInputDTO(
        language_result=language_result,
        structure_results=structure_results
    )

    result = analyze(input_dto)

    if debug:
        debug_print_result(result)

    return result


# 🔥 あなたの指定形式（完成版）
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    json_path = os.path.join(current_dir, "test_case_lhigh.json")

    run_test(json_path, debug=True)