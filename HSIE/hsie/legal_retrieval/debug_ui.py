from typing import List
from dto.result_dto import LegalRetrievalResultDTO
from dto.article_dto import LegalArticleDTO


def print_result(result: LegalRetrievalResultDTO) -> None:
    """
    LegalRetrievalResultDTOを人間可読な形式で表示する

    責務：
    ・DTO構造の可視化
    ・スピーカー単位の表示

    禁止事項：
    ・HSIResultの生出力
    ・単純な結果羅列
    """

    print("=" * 50)
    print(f"[Legal Retrieval Result] Speaker: {result.speaker_id}")
    print("=" * 50)

    if not result.articles:
        print("No articles found.")
        return

    for idx, article in enumerate(result.articles, 1):
        _print_article(article, idx)


def _print_article(article: LegalArticleDTO, index: int) -> None:
    """
    条文DTOの詳細表示
    """

    print(f"\n[{index}] {article.law_name} {article.article_number}")
    print("-" * 50)

    print("■ 条文本文:")
    print(article.text)

    print("\n■ ヒット元クエリ:")
    for q in article.source_queries:
        print(f"  - {q}")

    print("-" * 50)


def print_multiple_results(results: List[LegalRetrievalResultDTO]) -> None:
    """
    複数スピーカーの結果表示
    """

    print("\n" + "=" * 70)
    print("        Legal Retrieval Debug View")
    print("=" * 70)

    for result in results:
        print_result(result)

    print("\n" + "=" * 70)
    print("End of Debug Output")
    print("=" * 70)