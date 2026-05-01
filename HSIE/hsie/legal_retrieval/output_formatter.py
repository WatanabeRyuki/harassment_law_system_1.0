from typing import List
from dto.article_dto import LegalArticleDTO
from dto.result_dto import LegalRetrievalResultDTO
from article_aggregation import AggregatedArticle


def format_to_article_dtos(
    aggregated_articles: List[AggregatedArticle]
) -> List[LegalArticleDTO]:
    """
    AggregatedArticleをLegalArticleDTOへ変換する。

    責務：
    ・内部モデル → DTO変換

    禁止事項：
    ・統合処理
    ・フィルタリング
    ・スコア処理

    Args:
        aggregated_articles (List[AggregatedArticle])

    Returns:
        List[LegalArticleDTO]
    """

    article_dtos: List[LegalArticleDTO] = []

    for article in aggregated_articles:
        article_dtos.append(
            LegalArticleDTO(
                law_name=article.law_name,
                article_number=article.article_number,
                text=article.text,
                source_queries=article.source_queries
            )
        )

    return article_dtos


def format_to_result_dto(
    speaker_id: str,
    article_dtos: List[LegalArticleDTO]
) -> LegalRetrievalResultDTO:
    """
    最終出力DTOを生成する。

    責務：
    ・DTOラップのみ

    禁止事項：
    ・統合処理
    ・ロジック追加

    Args:
        speaker_id (str)
        article_dtos (List[LegalArticleDTO])

    Returns:
        LegalRetrievalResultDTO
    """

    return LegalRetrievalResultDTO(
        speaker_id=speaker_id,
        articles=article_dtos
    )