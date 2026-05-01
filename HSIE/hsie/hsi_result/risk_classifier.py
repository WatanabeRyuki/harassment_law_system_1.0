# analysis/hsi_result/risk_classifier.py

from typing import Literal

RiskLevel = Literal["low", "gray", "medium", "high"]


def classify_hsi(hsi_score: float) -> RiskLevel:
    """
    HSIスコアをリスクレベルに分類する

    Parameters
    ----------
    hsi_score : float
        AnalysisScoreで算出されたHSIスコア（0〜100想定）

    Returns
    -------
    RiskLevel
        "low" | "gray" | "medium" | "high"
    """

    if hsi_score <= 40:
        return "low"
    elif hsi_score <= 60:
        return "gray"
    elif hsi_score <= 85:
        return "medium"
    else:
        return "high"
