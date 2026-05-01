from dataclasses import dataclass
from typing import List


@dataclass
class LegalRetrievalInputDTO:
    """
    Legal Retrieval層の入力DTO

    Attributes:
        speaker_id: 対象スピーカーID
        search_queries: HSIResultから生成された検索クエリ群
    """
    speaker_id: str
    search_queries: List[str]