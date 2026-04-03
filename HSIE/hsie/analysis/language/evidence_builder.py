# -*- coding: utf-8 -*-

"""
evidence_builder.py

責務：
・Evidenceをspeaker別にグルーピング
・時系列順で保持

禁止事項：
・スコア変更
・カテゴリ変更
・フィルタリング（抽出は別責務）
"""

from collections import defaultdict
from typing import Dict, List
from .dto.evidence_dto import EvidenceDTO


def build(evidences: List[EvidenceDTO]) -> Dict[str, List[EvidenceDTO]]:
    """
    入力：
        evidences: List[EvidenceDTO]

    出力：
        Dict[speaker_id, List[EvidenceDTO]]
    """

    grouped = defaultdict(list)

    # =========================
    # ■ None除去＋グルーピング
    # =========================
    for e in evidences:
        if e is None:
            continue
        grouped[e.speaker_id].append(e)

    # =========================
    # ■ 時系列ソート
    # =========================
    result: Dict[str, List[EvidenceDTO]] = {}

    for speaker_id, ev_list in grouped.items():
        sorted_list = sorted(
            ev_list,
            key=lambda x: x.start_time
        )

        # コピーして不変性担保
        result[speaker_id] = list(sorted_list)

    return result