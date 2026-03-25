from typing import List, Dict

from .dto.utterance_dto import UtteranceDTO


def calc_turn_occupancy(utterances: List[UtteranceDTO], speakers: List[str]) -> Dict[str, float]:
    """
    話者ごとのターン占有率（ScoreDTOのturn_occupancyに相当）を算出する

    変更点：
    ・戻り値を Dict[str, float] に変更（話者ごとの占有率）
    ・「支配話者の特定」ステップを廃止し、全員分を並列で計算
    """

    if not utterances:
        return {sid: 0.0 for sid in speakers}

    # =========================
    # ① 全体の統計と話者ごとの集計
    # =========================
    speaker_time: Dict[str, float] = {sid: 0.0 for sid in speakers}
    speaker_tokens: Dict[str, int] = {sid: 0 for sid in speakers}

    total_time = 0.0
    total_tokens = 0

    for utt in utterances:
        duration = utt.end_time - utt.start_time
        token_count = len(utt.tokens)

        total_time += duration
        total_tokens += token_count

        # 登録外の話者がいた場合の安全処理を含め加算
        sid = utt.speaker_id
        speaker_time[sid] = speaker_time.get(sid, 0.0) + duration
        speaker_tokens[sid] = speaker_tokens.get(sid, 0) + token_count

    # =========================
    # ② 全話者分のスコア算出
    # =========================
    results = {}
    
    # 重み付けパラメータ（元のロジックを維持）
    alpha = 0.5
    beta = 0.5
    lambda_ = 0.8  # 静かな圧（密度）の考慮用

    for sid in speakers:
        time_ratio = _safe_divide(speaker_time.get(sid, 0.0), total_time)
        token_ratio = _safe_divide(speaker_tokens.get(sid, 0), total_tokens)

        # 基本的な占有率 (Presence)
        presence = alpha * time_ratio + beta * token_ratio

        # 密度による補正 (Pressure Bonus)
        # トークン密度が高い（短時間に詰め込んでいる）場合に加点される元の思想を継承
        pressure_bonus = token_ratio - time_ratio
        
        # 最終的な占有スコア
        # ※ 支配者決定ロジック (_resolve_silent_pressure) の計算式を全話者に適用
        occupancy_score = presence + lambda_ * pressure_bonus
        
        # 負の値にならないようクリップ（0.0 〜 1.0）
        results[sid] = max(0.0, min(1.0, occupancy_score))

    return results


# =========================
# 内部関数
# =========================

def _safe_divide(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b