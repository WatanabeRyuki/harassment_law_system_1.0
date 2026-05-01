from dataclasses import dataclass
from typing import List


@dataclass
class LegalArticleDTO:
    """
    条文DTO（最終出力単位）

    Attributes:
        law_name: 法令名
        article_number: 条番号
        text: 条文本文
        source_queries: この条文をヒットさせた検索クエリ一覧
    """
    law_name: str
    article_number: str
    text: str
    source_queries: List[str]