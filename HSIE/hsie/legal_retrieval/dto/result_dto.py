from dataclasses import dataclass
from typing import List
from .article_dto import LegalArticleDTO


@dataclass
class LegalRetrievalResultDTO:
    """
    Legal Retrieval層の最終出力DTO

    Attributes:
        speaker_id: 対象スピーカーID
        articles: 抽出された条文リスト
    """
    speaker_id: str
    articles: List[LegalArticleDTO]