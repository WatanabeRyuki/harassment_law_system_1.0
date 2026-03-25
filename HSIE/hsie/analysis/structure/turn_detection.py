from typing import List

from .dto.utterance_dto import UtteranceDTO
from .dto.turn_dto import TurnDTO


def detect_turns(utterances: List[UtteranceDTO]) -> List[TurnDTO]:
    """
    発話リストからターンを検出し、TurnDTOのリストを返す

    責務：
    ・話者交代の検出
    ・ターン境界の生成
    ・UtteranceDTOをTurn単位にグルーピング
    """

    if not utterances:
        return []

    turns: List[TurnDTO] = []

    current_speaker = utterances[0].speaker_id
    current_utterances: List[UtteranceDTO] = []

    for utt in utterances:
        # 同一話者 → 同一ターンに追加
        if utt.speaker_id == current_speaker:
            current_utterances.append(utt)
        else:
            # ターン確定
            turn = _build_turn(current_utterances)
            turns.append(turn)

            # 新ターン開始
            current_speaker = utt.speaker_id
            current_utterances = [utt]

    # 最後のターン
    if current_utterances:
        turn = _build_turn(current_utterances)
        turns.append(turn)

    return turns


# =========================
# 内部関数（本実装）
# =========================

def _build_turn(utterances: List[UtteranceDTO]) -> TurnDTO:
    """
    UtteranceDTOのリストからTurnDTOを生成する
    """

    if not utterances:
        raise ValueError("Utterances list is empty when building turn")

    speaker_id = utterances[0].speaker_id

    start_time = utterances[0].start_time
    end_time = utterances[-1].end_time

    return TurnDTO(
        speaker_id=speaker_id,
        start_time=start_time,
        end_time=end_time,
        utterances=utterances,
    )