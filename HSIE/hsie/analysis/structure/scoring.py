from typing import Dict

def calc_s_raw(
    speaker_scores: Dict[str, float]
) -> float:
    """
    特定話者の S_raw を算出する（0〜100で返す）

    引数:
    - speaker_scores: {"turn_occupancy": float, "interruption_rate": float, "negation_score": float}
    """

    # =========================
    # パラメータ（チューニング可能）
    # =========================
    v1 = 0.6  # ターン占有率の重み
    v2 = 0.4  # 割り込み率の重み
    v3 = 0.2  # 否定連鎖の重み

    # 重みの正規化（合計を 1.0 に調整）
    total_w = v1 + v2 + v3
    w_turn = v1 / total_w
    w_int = v2 / total_w
    w_neg = v3 / total_w

    # =========================
    # 各指標の取得とクレンジング
    # =========================
    # 各モジュールから渡される 0.0〜1.0 の値を確実に 0〜1 に収める
    t_occ = _clamp(speaker_scores.get("turn_occupancy", 0.0), 0.0, 1.0)
    i_rate = _clamp(speaker_scores.get("interruption_rate", 0.0), 0.0, 1.0)
    n_score = _clamp(speaker_scores.get("negation_score", 0.0), 0.0, 1.0)

    # =========================
    # 重み付き合成とスケーリング (0〜100)
    # =========================
    # 各項を 0〜100 にスケールしてから合成
    s_raw = (
        w_turn * _scale_100(t_occ) +
        w_int * _scale_100(i_rate) +
        w_neg * _scale_100(n_score)
    )

    return _clamp(s_raw, 0.0, 100.0)


# =========================
# 内部関数
# =========================

def _scale_100(value: float) -> float:
    """0〜1 の値を 0〜100 にスケーリング"""
    return value * 100.0


def _clamp(value: float, min_val: float, max_val: float) -> float:
    """値を範囲内に収める"""
    return max(min_val, min(value, max_val))