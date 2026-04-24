"""
統合パイプライン: JSON → Language → Structure → AnalysisScore → 標準出力にレポート表示
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# どのディレクトリから実行しても `analysis` が hsie 配下を指すようにする
_HSIE_ROOT = Path(__file__).resolve().parent.parent.parent
if _HSIE_ROOT.is_dir():
    _p = str(_HSIE_ROOT)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from analysis.analysis_score.analysis_score_analyzer import analyze as analysis_score_analyze
from analysis.analysis_score.dto.analysis_score_input_dto import AnalysisScoreInputDTO
from analysis.test.debug_ui import format_report
from analysis.language.language_analyzer import analyze as language_analyze
from analysis.structure.structure_analyzer import analyze_structure


class _LanguageInputUtterance:
    __slots__ = ("utterance_id", "speaker_id", "text", "start_time", "end_time")

    def __init__(self, u: dict) -> None:
        self.utterance_id = u["utterance_id"]
        self.speaker_id = u["speaker_id"]
        self.text = u["text"]
        self.start_time = u["start_time"]
        self.end_time = u["end_time"]


class _LanguageInputDTO:
    __slots__ = ("speakers", "conversation_duration", "utterances")

    def __init__(self, data: dict) -> None:
        self.speakers = [s["speaker_id"] for s in data.get("speakers", [])]
        self.conversation_duration = float(data.get("conversation_duration", 0.0))
        self.utterances = [_LanguageInputUtterance(u) for u in data["utterances"]]


def _resolve_case_data(data: dict, case_id: str | None = None) -> dict:
    if "test_cases" not in data:
        return data
    cases = data.get("test_cases", [])
    if not cases:
        raise ValueError("test_cases is empty.")
    if case_id:
        for case in cases:
            if case.get("case_id") == case_id:
                return case
        raise ValueError(f"case_id not found: {case_id}")
    return cases[0]


def run_test(json_path: str, debug: bool = True) -> None:
    _ = debug
    if not os.path.isfile(json_path):
        print(f"File not found: {json_path}", file=sys.stderr)
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Failed to load JSON: {e}", file=sys.stderr)
        return

    try:
        case_data = _resolve_case_data(raw, case_id=None)
        language_input = _LanguageInputDTO(case_data)
        language_result = language_analyze(language_input)
        structure_results, _sai, _aggressor = analyze_structure(case_data)
        score_input = AnalysisScoreInputDTO(
            language_result=language_result,
            structure_results=structure_results,
        )
        analysis_score_result = analysis_score_analyze(score_input)
    except Exception as e:
        print(f"Analysis failed: {e}", file=sys.stderr)
        return

    print(format_report(language_result, structure_results, analysis_score_result))


if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))

    json_path = os.path.join(current_dir, "test2/language_harassment/test_case9.json")

    run_test(json_path, debug=True)
