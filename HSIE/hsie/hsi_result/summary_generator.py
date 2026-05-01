# hsie/hsi_result/summary_generator.py

from typing import List


# ■ 優先的に説明に使うタグ（重要タグ）
PRIORITY_TAGS = [
    "人格否定",
    "能力否定",
    "存在価値否定",
    "侮辱",
    "暴言",
]


# ■ 構造タグ
STRUCTURE_TAGS = [
    "会話支配",
    "優越的地位の濫用",
    "継続的圧力",
    "反復行為",
    "心理的圧迫",
]


# -------------------------------
# ■ タグ抽出
# -------------------------------

def pick_top_tags(legal_tags: List[str]) -> List[str]:
    """
    説明に使う主要タグを抽出（最大2つ）
    """
    selected = [t for t in legal_tags if t in PRIORITY_TAGS]

    if not selected:
        return legal_tags[:2]  # fallback

    return selected[:2]


def pick_structure_tags(legal_tags: List[str]) -> List[str]:
    """
    構造的な問題タグを抽出（最大2つ）
    """
    return [t for t in legal_tags if t in STRUCTURE_TAGS][:2]


# -------------------------------
# ■ テキスト生成
# -------------------------------

def generate_text(template: str, main_tags: List[str], structure_tags: List[str]) -> str:
    """
    テンプレートに応じた文章生成
    """

    # ■ 重複除去（重要）
    structure_tags = [t for t in structure_tags if t not in main_tags]

    main_part = "・".join(main_tags) if main_tags else "一部の発言"
    structure_part = "および".join(structure_tags) if structure_tags else ""

    # ■ structure文を出すかどうか
    structure_sentence = ""
    if structure_part:
        structure_sentence = f"{structure_part}の構造が見られます。"

    # -------------------------------
    # ■ 注意喚起型（gray）
    # -------------------------------
    if template == "注意喚起型":
        return (
            f"{main_part}に関する表現が含まれており、"
            + (f"{structure_part}の傾向が見られる可能性があります。" if structure_part else "")
            + "受け手によっては不快や負担と感じられる場合があるため、"
            "表現には注意が必要です。"
        )

    # -------------------------------
    # ■ 問題提示型（medium）
    # -------------------------------
    elif template == "問題提示型":
        return (
            f"{main_part}を含む発言が確認され、"
            + structure_sentence
            + "これにより、心理的な負担や関係性の悪化につながる可能性があります。"
        )

    # -------------------------------
    # ■ 警告型（high）
    # -------------------------------
    else:
        return (
            f"{main_part}を含む発言が複数確認され、"
            + (f"{structure_part}の状況が認められる可能性があります。" if structure_part else "")
            + "このような言動はハラスメントと受け取られるリスクがあり、"
            "場合によっては法的問題に発展する可能性があります。"
        )


# -------------------------------
# ■ メイン関数
# -------------------------------

def generate_summary(legal_tags: List[str], mode: str) -> str:
    """
    法律タグとリスクレベルからsummaryを生成する
    """

    # ■ タグ抽出
    main_tags = pick_top_tags(legal_tags)
    structure_tags = pick_structure_tags(legal_tags)

    # ■ テンプレ分岐
    if mode == "gray":
        template = "注意喚起型"
    elif mode == "medium":
        template = "問題提示型"
    else:
        template = "警告型"

    # ■ 文章生成
    return generate_text(template, main_tags, structure_tags)