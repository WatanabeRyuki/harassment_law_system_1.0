from typing import List
from .dto.utterance_dto import LanguageUtteranceDTO


def preprocess(input_dto) -> List[LanguageUtteranceDTO]:
    """
    前処理（整形・文脈付与）

    責務：
    ・時系列ソート
    ・内部DTO変換
    ・prev / next 文脈付与

    禁止：
    ・スコア計算
    ・NLP処理
    """

    # =========================
    # ■ ① ソート
    # =========================
    utterances = sorted(input_dto.utterances, key=lambda x: x.start_time)

    result = []

    # =========================
    # ■ ② DTO変換 + 文脈付与
    # =========================
    for i, u in enumerate(utterances):
        prev_text = utterances[i - 1].text if i > 0 else ""
        next_text = utterances[i + 1].text if i < len(utterances) - 1 else ""

        result.append(
            LanguageUtteranceDTO(
                utterance_id=u.utterance_id,
                speaker_id=u.speaker_id,
                text=u.text,
                start_time=u.start_time,
                end_time=u.end_time,
                prev_text=prev_text,
                next_text=next_text,
            )
        )

    return result