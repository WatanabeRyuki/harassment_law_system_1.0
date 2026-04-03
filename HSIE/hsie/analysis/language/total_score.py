# -*- coding: utf-8 -*-

"""
total_score.py

責務：
・EvidenceリストからLスコア算出
・単純加算 ＋ 時間正規化（30秒ユニット）
"""

from typing import List
from .dto.evidence_dto import EvidenceDTO


def calc_total(
    evidences: List[EvidenceDTO],
    duration_sec: float
) -> float:
    """
    入力：
        evidences（※スコア降順前提）
        duration_sec（録音の全秒数）

    出力：
        Lスコア（0〜100）
    """

    # =========================
    # ■ 空リスト/時間ゼロ対応
    # =========================
    if not evidences:
        return 0.0
    duration_sec = float(duration_sec)
    if duration_sec <= 0.0:
        return 0.0

    raw_total = 0.0

    # =========================
    # ■ 単純加算（減衰を廃止）
    # =========================
    for e in evidences:
        # 各エビデンスのスコアをそのまま加算
        # 100を大幅に超過することを許容する
        raw_total += _clip(e.score)

    # =========================
    # ■ 時間正規化（30秒を1ユニット）
    # =========================
    # 30秒あたりに換算したハラスメント密度を算出
    time_factor = max(duration_sec / 30.0, 1.0)
    normalized_score = raw_total / time_factor

    # =========================
    # ■ 最終クリップ＋安定化
    # =========================
    final_score = _clip(normalized_score)

    return round(final_score, 2)


# =========================
# ■ 内部ユーティリティ
# =========================
def _clip(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return value