from dataclasses import dataclass
from typing import Dict, List

from .evidence_dto import EvidenceDTO


@dataclass(frozen=True)
class LanguageResultDTO:
    """
    言語攻撃性分析の最終結果
    """

    # =========================
    # ■ スピーカー別スコア
    # =========================
    speaker_scores: Dict[str, float]

    # =========================
    # ■ 全体スコア（最大 or 統合）
    # =========================
    total_score: float

    # =========================
    # ■ Evidence（全体フラット）
    # =========================
    evidences: List[EvidenceDTO]

    # =========================
    # ■ メタ情報
    # =========================
    conversation_duration: float