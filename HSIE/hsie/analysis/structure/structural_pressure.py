from typing import List, Dict

def calc_structural_pressure(scores_by_window: List[Dict[str, Dict[str, float]]], speakers: List[str]) -> Dict[str, float]:
    """
    話者ごとの構造圧力係数 c を算出する

    引数:
    - scores_by_window: ウィンドウごとのスコア。
      構造例: [{"speaker_0": {"turn_occupancy": 75, ...}, "speaker_1": {...}}, ...]
    - speakers: 話者IDリスト
    """

    # パラメータ（設計値維持）
    threshold = 0.7        # 高スコア判定
    window_duration = 180.0 # 3分（秒）
    k = 0.002               # 継続時間係数
    c_max = 1.5

    results = {}

    for sid in speakers:
        current_continuous_time = 0.0
        max_continuous_time = 0.0

        for window in scores_by_window:
            # その話者のウィンドウ内スコアを取得
            speaker_scores = window.get(sid, {})
            
            if _is_high_pressure(speaker_scores, threshold):
                current_continuous_time += window_duration
                max_continuous_time = max(max_continuous_time, current_continuous_time)
            else:
                current_continuous_time = 0.0

        # 話者ごとの最大継続時間から c を算出
        c = 1 + k * max_continuous_time
        results[sid] = min(c, c_max)

    return results


# =========================
# 内部関数（対象話者のスコアを見るよう修正）
# =========================

def _is_high_pressure(speaker_scores: dict, threshold: float) -> bool:
    """
    特定話者のウィンドウ内スコアが高圧的か判定
    """
    # 各指標は 0.0〜1.0 または 0〜100 の想定に合わせて調整が必要ですが、
    # ここでは既存の threshold（70.0）との比較を維持します
    turn = speaker_scores.get("turn_occupancy", 0.0)
    interrupt = speaker_scores.get("interruption_rate", 0.0)
    negation = speaker_scores.get("negation_score", 0.0)

    # いずれかの指標が閾値を超えていれば、その話者はその時間枠で「圧」をかけているとみなす
    return (
        turn >= threshold
        or interrupt >= threshold
        or negation >= threshold
    )