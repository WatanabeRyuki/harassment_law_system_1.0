# hsie/hsi_result/legal_mapper.py

from typing import Dict, List


# ■ カテゴリ → 法律タグ変換テーブル
CATEGORY_MAP: Dict[str, List[str]] = {
    "D_p": ["人格権侵害", "人格否定"],
    "D_a": ["人格権侵害", "能力否定"],
    "D_v": ["人格権侵害", "存在価値否定"],
    "I_dir": ["侮辱", "暴言"],
    "I_ind": ["侮辱", "間接的侮辱"],
    "C_block": ["優越的地位の濫用", "強制命令"],
    "C_shift": ["不法行為", "責任転嫁"],
}


def map_to_legal_tags(
    category_count: Dict[str, int],
    turn_occupancy: float,
    interruption_rate: float,
    negation_score: float,
    evidences: List
) -> List[str]:
    """
    カテゴリと構造情報から法律タグを生成する

    Returns
    -------
    List[str] : 法律タグ（重複排除済）
    """

    tags: List[str] = []

    # ■ 3.1 カテゴリ → 法律タグ変換
    for cat in category_count:
        tags.extend(CATEGORY_MAP.get(cat, []))

    # ■ 3.2 構造タグ付与
    if turn_occupancy > 0.7:
        tags.extend(["優越的地位の濫用", "会話支配"])

    if interruption_rate > 0.2:
        tags.append("発言遮断")

    if negation_score > 0.2:
        tags.extend(["心理的圧迫", "否定連鎖"])

    # ■ 3.3 継続・反復補正
    total_evidence = len(evidences)

    if total_evidence >= 4:
        tags.append("反復行為")

    if total_evidence >= 6:
        tags.append("継続的圧力")

    # ■ 3.4 重複排除
    return list(set(tags))