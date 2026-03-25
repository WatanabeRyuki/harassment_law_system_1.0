from typing import List, Dict, Any

from janome.tokenizer import Tokenizer

from .dto.utterance_dto import UtteranceDTO, MorphToken


# 形態素解析器（初期化コスト削減のためグローバル）
_tokenizer = Tokenizer()


def segment_conversation(data: Dict[str, Any]) -> List[UtteranceDTO]:
    """
    会話データをセグメント化し、UtteranceDTOのリストを返す

    責務：
    ・時系列ソート
    ・同一話者の統合
    ・形態素解析（tokens付与）
    """

    # ① utterances取得（after_evidence前提）
    utterances = data.get("utterances", [])

    if not utterances:
        return []

    # ② start_timeでソート
    sorted_utts = sorted(utterances, key=lambda x: x["start_time"])

    # ③ 同一話者の連続発話を統合
    merged = _merge_same_speaker(sorted_utts)

    # ④ DTO化 + 形態素解析
    result: List[UtteranceDTO] = []
    for utt in merged:
        tokens = _analyze_text(utt["text"])

        dto = UtteranceDTO(
            speaker_id=utt["speaker_id"],
            start_time=utt["start_time"],
            end_time=utt["end_time"],
            text=utt["text"],
            tokens=tokens,
        )
        result.append(dto)

    return result


# =========================
# 内部関数（本実装）
# =========================

def _merge_same_speaker(utterances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    同一話者の連続発話を統合する
    """

    if not utterances:
        return []

    merged = []
    current = utterances[0].copy()

    for i in range(1, len(utterances)):
        nxt = utterances[i]

        # 同一話者なら統合
        if current["speaker_id"] == nxt["speaker_id"]:
            current["text"] += " " + nxt["text"]
            current["end_time"] = nxt["end_time"]
        else:
            merged.append(current)
            current = nxt.copy()

    # 最後の要素を追加
    merged.append(current)

    return merged


def _analyze_text(text: str) -> List[MorphToken]:
    """
    テキストを形態素解析し、MorphTokenリストを返す
    """

    tokens: List[MorphToken] = []

    for token in _tokenizer.tokenize(text):
        surface = token.surface
        base_form = token.base_form
        pos = token.part_of_speech.split(",")[0]  # 品詞の大分類のみ取得

        tokens.append(
            MorphToken(
                surface=surface,
                base_form=base_form,
                pos=pos
            )
        )

    return tokens