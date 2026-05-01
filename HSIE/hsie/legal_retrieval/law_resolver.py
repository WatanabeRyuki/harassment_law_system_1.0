from dataclasses import dataclass
from typing import List, Set, Dict


@dataclass
class QueryLawMapping:
    """
    クエリと対応法令のマッピングDTO（内部利用）

    Attributes:
        query: 元クエリ
        tokens: 分解済みトークン
        laws: 対応する法令集合
    """
    query: str
    tokens: List[str]
    laws: Set[str]


# 法令辞書（拡張前提）
LAW_DICT: Dict[str, List[str]] = {
    "不法行為": ["民法"],
    "職場": ["労働施策総合推進法"],
    "侮辱": ["刑法"],
    # 必要に応じて追加
}


def resolve(query: str, tokens: List[str]) -> QueryLawMapping:
    """
    トークンから対象法令を辞書ベースで特定する。

    処理内容：
    ・トークンごとに辞書を参照
    ・該当法令を集合として保持

    禁止事項：
    ・直接検索（API/DBアクセス）
    ・採用判断（フィルタリング）

    Args:
        query (str): 元クエリ
        tokens (List[str]): 分解済みトークン

    Returns:
        QueryLawMapping: 法令マッピング結果
    """

    laws: Set[str] = set()

    for token in tokens:
        if token in LAW_DICT:
            for law in LAW_DICT[token]:
                laws.add(law)

    return QueryLawMapping(
        query=query,
        tokens=tokens,
        laws=laws
    )