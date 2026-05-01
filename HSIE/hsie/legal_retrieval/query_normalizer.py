from dataclasses import dataclass
from typing import List


@dataclass
class QueryUnit:
    """
    クエリ分解結果DTO（内部利用）

    Attributes:
        query: 元クエリ文字列
        tokens: 分解されたトークンリスト
    """
    query: str
    tokens: List[str]


def normalize(query: str) -> QueryUnit:
    """
    クエリをスペース区切りで分解し、機械処理可能な形に正規化する。

    処理内容：
    ・スペース分割
    ・トリム処理
    ・空文字除去

    禁止事項：
    ・条件分岐
    ・重複排除
    ・検索処理

    Args:
        query (str): HSIResultで生成された検索クエリ

    Returns:
        QueryUnit: 分解済みクエリ
    """

    tokens = [token.strip() for token in query.split(" ") if token.strip()]

    return QueryUnit(
        query=query,
        tokens=tokens
    )