from __future__ import annotations

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
_LEGAL_RETRIEVAL_DIR = os.path.join(_PROJECT_ROOT, "hsie", "legal_retrieval")
if _LEGAL_RETRIEVAL_DIR not in sys.path:
    sys.path.insert(0, _LEGAL_RETRIEVAL_DIR)

from hsie.analysis.analysis_runner import run_analysis
from hsie.hsi_result.dto.hsi_result_dto import HSIResultDTO
from hsie.hsi_result.dto.hsi_result_input_dto import HSIResultInputDTO, AnalysisEvidenceDTO
from hsie.hsi_result.hsi_result_analyzer import HSIResultAnalyzer
from hsie.analysis.test.debug_ui import render_result as render_analysis
from hsie.hsi_result.debug_ui import render_result as render_hsi_result
from hsie.legal_retrieval import legal_retrieval_analyzer as LegalRetrievalAnalyzer
from hsie.legal_retrieval.dto.input_dto import LegalRetrievalInputDTO
from hsie.legal_retrieval.debug_ui import print_result as render_legal_retrieval


def convert_to_hsi_result_input(speaker) -> HSIResultInputDTO:
    evidences = []

    for ev in getattr(speaker, "evidences", []) or []:
        categories = tuple((getattr(ev, "categories", None) or []))

        evidences.append(
            AnalysisEvidenceDTO(
                utterance_id=getattr(ev, "utterance_id", ""),
                speaker_id=getattr(ev, "speaker_id", ""),
                start_time=float(getattr(ev, "start_time", 0.0) or 0.0),
                end_time=float(getattr(ev, "end_time", 0.0) or 0.0),
                text=getattr(ev, "text", ""),
                score=float(getattr(ev, "score", 0.0) or 0.0),
                categories=categories,
            )
        )

    return HSIResultInputDTO(
        speaker_id=getattr(speaker, "speaker_id", ""),
        hsi_score=float(getattr(speaker, "hsi_score", 0.0) or 0.0),
        language_score=float(getattr(speaker, "language_score", 0.0) or 0.0),
        structure_score=float(getattr(speaker, "structure_score", 0.0) or 0.0),
        turn_occupancy=float(getattr(speaker, "turn_occupancy", 0.0) or 0.0),
        interruption_rate=float(getattr(speaker, "interruption_rate", 0.0) or 0.0),
        negation_score=float(getattr(speaker, "negation_score", 0.0) or 0.0),
        sai_score=float(getattr(speaker, "sai_score", 0.0) or 0.0),
        evidences=evidences,
        applied_condition=getattr(speaker, "applied_condition", ""),
        alpha=float(getattr(speaker, "alpha", 0.0) or 0.0),
        beta=float(getattr(speaker, "beta", 0.0) or 0.0),
    )


def convert_to_legal_retrieval_input(result: HSIResultDTO) -> LegalRetrievalInputDTO:
    return LegalRetrievalInputDTO(
        speaker_id=result.speaker_id,
        search_queries=result.search_queries,
    )


def run_test(json_path: str, debug: bool = True) -> None:
    analysis_result = run_analysis(json_path)

    speaker_results = getattr(analysis_result, "speaker_results", analysis_result)
    speakers = (
        speaker_results.values()
        if isinstance(speaker_results, dict)
        else speaker_results
    )

    for speaker in speakers:
        if debug:
            render_analysis(speaker)

        hsi_input = convert_to_hsi_result_input(speaker)
        hsi_result = HSIResultAnalyzer.execute(hsi_input)

        if debug:
            render_hsi_result(hsi_result)

        legal_input = convert_to_legal_retrieval_input(hsi_result)
        legal_result = LegalRetrievalAnalyzer.execute(legal_input)

        if debug:
            render_legal_retrieval(legal_result)


if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))

    json_path = os.path.join(current_dir, "../analysis/test/test2/language_harassment/test_case9.json")

    run_test(json_path, debug=True)
