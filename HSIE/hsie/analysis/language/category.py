# -*- coding: utf-8 -*-

"""
category.py

責務：
・I, C, D からカテゴリ判定
・しきい値判定のみ

禁止事項：
・スコア補正
・Evidence操作
・ロジック追加
"""

from typing import List


# =========================
# ■ 定数（将来調整用）
# =========================
THRESHOLD_INSULT = 50.0
THRESHOLD_COMMAND = 50.0
THRESHOLD_DENIAL = 60.0


def detect_categories(I: float, C: float, D: float) -> List[str]:
    """
    入力：
        I, C, D（0〜100）

    出力：
        List[str]（カテゴリ）
    """

    # =========================
    # ■ 安定化（丸め）
    # =========================
    I = round(I, 2)
    C = round(C, 2)
    D = round(D, 2)

    categories: List[str] = []

    # =========================
    # ■ 判定（順序固定）
    # =========================
    if I >= THRESHOLD_INSULT:
        categories.append("Insult")

    if C >= THRESHOLD_COMMAND:
        categories.append("Command")

    if D >= THRESHOLD_DENIAL:
        categories.append("Denial")

    return categories