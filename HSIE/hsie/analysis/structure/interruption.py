from typing import List, Dict

from .dto.turn_dto import TurnDTO
from .dto.interruption_dto import InterruptionDTO
from .sentence_completion import is_sentence_complete


def detect_interruptions(turns: List[TurnDTO], speakers: List[str]) -> Dict[str, InterruptionDTO]:
    """
    話者ごとの割り込みを検出し、話者IDをキーとしたDTOの辞書を返す

    変更点：
    ・戻り値を Dict[str, InterruptionDTO] に変更
    ・割り込みを「発生させた側（次の話者）」のカウントとして集計
    """

    # 初期化：全話者分のDTOを用意
    total_turns = len(turns)
    results = {
        sid: InterruptionDTO(
            speaker_id=sid,
            total_turns=total_turns,
            interruption_count=0,
            interruption_rate=0.0
        ) for sid in speakers
    }

    if total_turns < 2:
        return results

    # 各話者のカウント用一時変数
    counts = {sid: 0 for sid in speakers}

    for i in range(len(turns) - 1):
        current_turn = turns[i]
        next_turn = turns[i + 1]

        # 条件1：話者変更（speaker_change）
        # ※ TurnDetectionの仕様上、隣接ターンは必ず話者が異なるはずですが明示的にチェック
        if current_turn.speaker_id == next_turn.speaker_id:
            continue

        # 条件2：時間接近
        time_close = _is_time_close(current_turn, next_turn)

        # 条件3：前話者の文章未完
        sentence_incomplete = _is_sentence_incomplete(current_turn)

        # 割り込み成立判定
        if time_close and sentence_incomplete:
            # 「割り込んだ側」である next_turn.speaker_id のカウントを増やす
            counts[next_turn.speaker_id] += 1

    # 各話者のレートを算出してDTOを再生成
    for sid in speakers:
        count = counts[sid]
        # レート定義：その話者が「全ターン数」に対して何回割り込んだか
        rate = count / total_turns if total_turns > 0 else 0.0
        
        results[sid] = InterruptionDTO(
            speaker_id=sid,
            total_turns=total_turns,
            interruption_count=count,
            interruption_rate=rate
        )

    return results


# --- 内部関数は変更なし ---
def _is_time_close(current: TurnDTO, next_turn: TurnDTO, delta: float = 0.5) -> bool:
    gap = next_turn.start_time - current.end_time
    return gap < delta


def _is_sentence_incomplete(turn: TurnDTO) -> bool:
    if not turn.utterances:
        return False
    last_utterance = turn.utterances[-1]
    return not is_sentence_complete(last_utterance.tokens)