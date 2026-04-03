import math


def finalize(score: float) -> float:
    """
    最終スコア整形

    責務：
    ・0〜100にクリップ
    ・NaN / None対策
    ・float保証

    ※ロジック追加は禁止（整形のみ）
    """

    # =========================
    # ■ 異常値対策
    # =========================
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return 0.0

    # =========================
    # ■ 型保証
    # =========================
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 0.0

    # =========================
    # ■ クリップ処理
    # =========================
    if score < 0:
        return 0.0
    if score > 100:
        return 100.0

    return score