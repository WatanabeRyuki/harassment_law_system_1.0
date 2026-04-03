import json
import os
import sys

# パス調整（hsieルートを通す）
current_dir = os.path.dirname(__file__)
hsie_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if hsie_root not in sys.path:
    sys.path.append(hsie_root)

from analysis.language.language_analyzer import analyze
from analysis.language.debug_analyzer import debug_analyze


# =========================
# ■ DTO変換
# =========================
class InputDTO:
    def __init__(self, data):
        self.speakers = [s["speaker_id"] for s in data.get("speakers", [])]
        self.conversation_duration = data.get("conversation_duration", 0.0)
        self.utterances = [UtteranceDTO(u) for u in data["utterances"]]


class UtteranceDTO:
    def __init__(self, u):
        self.utterance_id = u["utterance_id"]
        self.speaker_id = u["speaker_id"]
        self.text = u["text"]
        self.start_time = u["start_time"]
        self.end_time = u["end_time"]


# =========================
# ■ 実行
# =========================
def _resolve_case_data(data: dict, case_id: str | None = None) -> dict:
    """
    JSONが単体ケース or test_cases配列のどちらでも扱えるようにする。
    """
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


def run_test(file_path: str, debug: bool = False, case_id: str | None = None):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    case_data = _resolve_case_data(data, case_id=case_id)
    input_dto = InputDTO(case_data)

    print(f"\n{'='*50}")
    print(f" TEST: {os.path.basename(file_path)}")
    print(f"{'='*50}")

    if case_data.get("case_id"):
        print(f" CASE ID: {case_data['case_id']}")
    if case_data.get("description"):
        print(f" DESC   : {case_data['description']}")

    if debug:
        # =========================
        # ① DEBUG
        # =========================
        print("\n===== DEBUG OUTPUT =====")
        debug_analyze(input_dto)

    # =========================
    # ② RESULT
    # =========================
    print("\n===== FINAL RESULT =====")
    result = analyze(input_dto)

    print("\n[Speaker Scores]")
    for k, v in result.speaker_scores.items():
        print(f"{k}: {v:.2f}")

    print("\n[Evidence]")
    for ev in result.evidences:
        print("----------------------------")
        print(f"Speaker: {ev.speaker_id}")
        print(f"Text: {ev.text}")
        print(f"Score: {ev.score:.2f}")
        print(f"Categories: {ev.categories}")

    print(f"\n{'='*50}")


if __name__ == "__main__":
    json_path = os.path.join(current_dir, "test_case_discussion.json")
    run_test(json_path, debug=True)