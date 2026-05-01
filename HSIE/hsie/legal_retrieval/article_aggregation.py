from dataclasses import dataclass
from typing import List, Dict, Tuple, Set
from article_scoring_filter import ScoredArticle


@dataclass
class AggregatedArticle:
    """
    統合後条文（内部利用）

    Attributes:
        law_name: 法令名
        article_number: 条番号
        text: 条文本文
        source_queries: ヒット元クエリ一覧
    """
    law_name: str
    article_number: str
    text: str
    source_queries: List[str]


def aggregate(scored_articles: List[ScoredArticle]) -> List[AggregatedArticle]:
    """
    スコア済み条文を統合し、重複を排除する。

    統合ルール：
        ・(law_name, article_number) をキーに統合
        ・source_queries をマージ
        ・score は最大値を保持（内部のみ・出力しない）

    禁止事項：
        ・全体フロー制御
        ・DTO変換

    Args:
        scored_articles (List[ScoredArticle]): スコア済み条文リスト

    Returns:
        List[AggregatedArticle]: 統合後条文リスト
    """

    aggregation_map: Dict[Tuple[str, str], Dict] = {}

    for article in scored_articles:
        key = (article.law_name, article.article_number)

        if key not in aggregation_map:
            aggregation_map[key] = {
                "law_name": article.law_name,
                "article_number": article.article_number,
                "text": article.text,
                "source_queries": set(),
                "score": article.score  # 内部保持
            }

        aggregation_map[key]["source_queries"].add(article.source_query)

        # 最大スコア保持（内部用）
        if article.score > aggregation_map[key]["score"]:
            aggregation_map[key]["score"] = article.score

    aggregated_results: List[AggregatedArticle] = []

    for value in aggregation_map.values():
        aggregated_results.append(
            AggregatedArticle(
                law_name=value["law_name"],
                article_number=value["article_number"],
                text=value["text"],
                source_queries=list(value["source_queries"])
            )
        )

    return aggregated_results