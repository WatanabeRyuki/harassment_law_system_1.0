# -*- coding: utf-8 -*-

"""
evidence_extractor.py

責務：
・L_raw >= 閾値 の発話のみ Evidence化
・DTO生成のみ

禁止事項：
・スコア変更
・カテゴリ変更
・リスト操作
"""

from typing import Optional, List
from .dto.evidence_dto import EvidenceDTO


# =========================
# ■ 定数
# =========================
EVIDENCE_THRESHOLD = 60.0


def extract(utterance, score: float, categories: List[str]) -> Optional[EvidenceDTO]:
    """
    入力：
        utterance
        score (L_raw)
        categories

    出力：
        EvidenceDTO or None
    """

    # =========================
    # ■ 安定化
    # =========================
    score = round(score, 2)

    # =========================
    # ■ 閾値判定
    # =========================
    if score < EVIDENCE_THRESHOLD:
        return None

    # =========================
    # ■ categories防御
    # =========================
    if categories is None:
        categories = []

    # =========================
    # ■ Evidence生成
    # =========================
    return EvidenceDTO(
        utterance_id=utterance.utterance_id,
        speaker_id=utterance.speaker_id,
        start_time=utterance.start_time,
        end_time=utterance.end_time,
        text=utterance.text,
        score=score,
        categories=list(categories)  # コピーして不変性担保
    )