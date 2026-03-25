from typing import List, Dict

from .dto.turn_dto import TurnDTO


# 否定語辞書（変更なし）
NEGATION_WORDS = {
    "違う", "違います", "いや", "ダメ", "誤り", "不正解", "間違い", "ありえない",
}


def detect_negation_chain(turns: List[TurnDTO], speakers: List[str]) -> Dict[str, float]:
    """
    話者ごとの否定連鎖スコアを算出する

    変更点：
    ・戻り値を Dict[str, float] に変更
    ・否定語を発した話者（curr_turn.speaker_id）に対して連鎖の責任（スコア）を割り当て
    """

    total_turns = len(turns)
    if not turns:
        return {sid: 0.0 for sid in speakers}

    gamma = 1.5  # 設計値
    
    # 話者ごとの連鎖長リストを保持
    speaker_chains: Dict[str, List[int]] = {sid: [] for sid in speakers}
    
    # 現在継続中の連鎖情報
    current_chain_length = 0
    current_chain_owner = None

    for i in range(1, len(turns)):
        curr_turn = turns[i]
        
        # 否定を検出
        is_negating = _detect_negation(curr_turn)

        if is_negating:
            current_chain_length += 1
            current_chain_owner = curr_turn.speaker_id
        else:
            # 否定が途切れたら、直前のオーナーに連鎖長を記録
            if current_chain_length > 0 and current_chain_owner:
                speaker_chains[current_chain_owner].append(current_chain_length)
            
            current_chain_length = 0
            current_chain_owner = None

    # 最後のチェーンを反映
    if current_chain_length > 0 and current_chain_owner:
        speaker_chains[current_chain_owner].append(current_chain_length)

    # 各話者ごとにスコア計算
    results = {}
    for sid in speakers:
        lengths = speaker_chains[sid]
        score = _calculate_chain_score(lengths, total_turns, gamma)
        results[sid] = min(1.0, score)  # 0〜1に収まるよう念のためクリップ

    return results


# =========================
# 内部関数（ロジックは維持）
# =========================

def _detect_negation(turn: TurnDTO) -> bool:
    for utt in turn.utterances:
        for token in utt.tokens:
            if token.base_form in NEGATION_WORDS or token.surface in NEGATION_WORDS:
                return True
    return False


def _calculate_chain_score(chain_lengths: List[int], total_turns: int, gamma: float) -> float:
    if total_turns == 0 or not chain_lengths:
        return 0.0

    score_sum = sum(pow(length, gamma) for length in chain_lengths)
    return score_sum / total_turns