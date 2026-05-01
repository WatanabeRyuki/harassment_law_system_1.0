from typing import List

from dto.input_dto import LegalRetrievalInputDTO
from dto.result_dto import LegalRetrievalResultDTO

from query_normalizer import normalize
from law_resolver import resolve
from article_retrieval import get_articles
from article_scoring_filter import score_and_filter, ScoredArticle
from article_aggregation import aggregate, AggregatedArticle
from output_formatter import (
    format_to_article_dtos,
    format_to_result_dto
)


def execute(input_dto: LegalRetrievalInputDTO) -> LegalRetrievalResultDTO:
    """
    Legal Retrieval層のメイン処理

    責務：
    ・全体フローの制御
    ・各処理の呼び出しと接続

    禁止事項：
    ・ロジック実装
    ・スコア計算
    ・フィルタリング
    ・統合処理

    Args:
        input_dto (LegalRetrievalInputDTO)

    Returns:
        LegalRetrievalResultDTO
    """

    scored_results: List[ScoredArticle] = []

    # --- クエリ単位で処理 ---
    for query in input_dto.search_queries:

        # ① Query Normalizer
        query_unit = normalize(query)

        # ② Law Resolver
        mapping = resolve(query_unit.query, query_unit.tokens)

        # ③ Article Retrieval
        for law_name in mapping.laws:
            articles_dict = get_articles(law_name)
            articles = articles_dict.get(law_name, [])

            # ④ Article Scoring & Filter
            for article in articles:
                scored = score_and_filter(
                    law_name=article.law_name,
                    article_number=article.article_number,
                    text=article.text,
                    tokens=query_unit.tokens,
                    source_query=query_unit.query
                )

                if scored is not None:
                    scored_results.append(scored)

    # ⑤ Article Aggregation
    aggregated_articles: List[AggregatedArticle] = aggregate(scored_results)

    # ⑥ Output Formatter
    article_dtos = format_to_article_dtos(aggregated_articles)
    result_dto = format_to_result_dto(
        speaker_id=input_dto.speaker_id,
        article_dtos=article_dtos
    )

    return result_dto