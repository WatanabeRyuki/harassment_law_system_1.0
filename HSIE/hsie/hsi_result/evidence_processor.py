# hsie/hsi_result/evidence_processor.py

from collections import Counter
from typing import Dict, List, Tuple, TypedDict


class NormalizedEvidence(TypedDict):
    text: str
    categories: List[str]
    score: float


def process_evidence(
    evidences: List
) -> Tuple[Dict[str, int], List[NormalizedEvidence]]:
    """
    Evidenceの前処理を行う

    Parameters
    ----------
    evidences : List[AnalysisEvidenceDTO]
        AnalysisScoreから渡されるEvidenceリスト

    Returns
    -------
    category_count : Dict[str, int]
        カテゴリ出現頻度

    normalized_evidences : List[NormalizedEvidence]
        正規化されたEvidence
    """

    # ■ 2.1 カテゴリ収集
    all_categories: List[str] = []

    for ev in evidences:
        if ev.categories:
            all_categories.extend(ev.categories)

    # ■ 2.2 出現頻度カウント
    category_count: Dict[str, int] = dict(Counter(all_categories))

    # ■ 2.3 Evidence正規化
    normalized_evidences: List[NormalizedEvidence] = []

    for ev in evidences:
        normalized_evidences.append(
            {
                "text": ev.text,
                "categories": ev.categories if ev.categories else [],
                "score": ev.score,
            }
        )

    return category_count, normalized_evidences