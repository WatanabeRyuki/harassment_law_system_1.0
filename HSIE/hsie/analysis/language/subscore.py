# -*- coding: utf-8 -*-

"""
subscore.py

責務：
・BertScoreDTO → SubScoreDTOへ変換
・I / C / D の算出のみ

禁止事項：
・スコア補正禁止
・文脈参照禁止
・副作用禁止
"""

from .dto.subscore_dto import SubScoreDTO
from .dto.bert_score_dto import BertScoreDTO


def calc_subscores(score: BertScoreDTO) -> SubScoreDTO:
    """
    入力：
        BertScoreDTO

    出力：
        SubScoreDTO（I, C, D）
    """

    # =========================
    # ■ サブスコア算出
    # =========================
    I = max(score.I_dir, score.I_ind)
    C = max(score.C_shift, score.C_block)
    D = max(score.D_p, score.D_a, score.D_v)

    # =========================
    # ■ 安全処理（0〜100保証）
    # =========================
    I = _clip(I)
    C = _clip(C)
    D = _clip(D)

    # =========================
    # ■ DTO返却
    # =========================
    return SubScoreDTO(
        I=float(I),
        C=float(C),
        D=float(D)
    )


# =========================
# ■ 内部ユーティリティ
# =========================
def _clip(value: float) -> float:
    """
    0〜100に制限
    """
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return value