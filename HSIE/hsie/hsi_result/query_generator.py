# hsie/hsi_result/query_generator.py

from typing import List


# ■ Level2タグ（法律概念）
LEVEL2_TAGS = {
    "人格権侵害",
    "侮辱",
    "優越的地位の濫用",
    "不法行為",
}


def generate_queries(legal_tags: List[str]) -> List[str]:
    """
    法律タグから検索クエリを生成する

    Parameters
    ----------
    legal_tags : List[str]

    Returns
    -------
    List[str] : 検索クエリ（最大5件）
    """

    queries: List[str] = []

    # ■ タグ分類
    level2 = [t for t in legal_tags if t in LEVEL2_TAGS]
    level3 = [t for t in legal_tags if t not in LEVEL2_TAGS]

    # ■ ① 法律概念 × 行為
    for l2 in level2:
        for l3 in level3:
            queries.append(f"{l2} {l3} 職場")

    # ■ ② ハラスメント文脈強化
    if any(tag in legal_tags for tag in ["人格否定", "能力否定", "暴言"]):
        queries.append("パワーハラスメント 人格否定 職場")

    if "継続的圧力" in legal_tags:
        queries.append("パワーハラスメント 継続的圧力")

    # ■ ③ 構造強化
    if "優越的地位の濫用" in legal_tags:
        queries.append("優越的地位 パワハラ 労働")

    if "会話支配" in legal_tags:
        queries.append("会話支配 ハラスメント")

    # ■ 重複排除
    unique_queries = list(dict.fromkeys(queries))

    # ■ 上限5件
    return unique_queries[:5]