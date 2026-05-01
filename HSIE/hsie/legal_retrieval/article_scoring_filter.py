from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScoredArticle:
    """
    スコア付き条文（内部利用）

    Attributes:
        law_name: 法令名
        article_number: 条番号
        text: 条文本文
        score: スコア
        source_query: 元クエリ
    """
    law_name: str
    article_number: str
    text: str
    score: int
    source_query: str


# 同義語辞書（簡易版・拡張前提）
# article_scoring_filter.py

SYNONYM_DICT = {
    "侮辱": ["名誉", "信用", "名誉を侵害"],
    "人格否定": ["人格権", "名誉", "精神的損害"],
    "能力否定": ["評価", "信用", "社会的評価"],
    "継続的圧力": ["精神的苦痛", "反復", "継続"],
}


def score_and_filter(
    law_name: str,
    article_number: str,
    text: str,
    tokens: List[str],
    source_query: str
) -> Optional[ScoredArticle]:
    """
    条文に対してスコアリングを行い、閾値を満たす場合のみ返却する。

    スコア式：
        Score = 完全一致数 × 2 + 部分一致数 × 1

    判定：
        score >= 2 → 採用

    禁止事項：
        ・重複排除
        ・他条文との比較
        ・ランキング処理

    Args:
        law_name (str): 法令名
        article_number (str): 条番号
        text (str): 条文本文
        tokens (List[str]): クエリトークン
        source_query (str): 元クエリ

    Returns:
        Optional[ScoredArticle]: 採用された場合のみ返却
    """

    score = 0

    for token in tokens:
        if token in text:
            score += 2
        else:
            synonyms = SYNONYM_DICT.get(token, [])
            for syn in synonyms:
                if syn in text:
                    score += 1
                    break

    if score >= 2:
        return ScoredArticle(
            law_name=law_name,
            article_number=article_number,
            text=text,
            score=score,
            source_query=source_query
        )

    return None