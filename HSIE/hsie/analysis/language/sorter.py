# -*- coding: utf-8 -*-

"""
sorter.py

責務：
・Evidenceをスコア降順でソート

禁止事項：
・スコア変更
・フィルタリング
・構造変更
"""

from typing import List
from .dto.evidence_dto import EvidenceDTO


def sort_by_score(evidences: List[EvidenceDTO]) -> List[EvidenceDTO]:
    """
    入力：
        evidences: List[EvidenceDTO]

    出力：
        スコア降順リスト
    """

    # =========================
    # ■ None除去
    # =========================
    filtered = [e for e in evidences if e is not None]

    # =========================
    # ■ 安定ソート
    # ① score降順
    # ② start_time昇順（同スコア時）
    # =========================
    sorted_list = sorted(
        filtered,
        key=lambda x: (-round(x.score, 2), x.start_time)
    )

    # =========================
    # ■ 不変性担保
    # =========================
    return list(sorted_list)