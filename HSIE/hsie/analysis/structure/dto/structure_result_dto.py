from dataclasses import dataclass


@dataclass(frozen=True)
class StructureResultDTO:
    """
    話者ごとの Structure Aggression 最終結果DTO
    """
    speaker_id: str     # 対象話者ID
    s_raw: float        # 基本スコア（0〜100）
    c: float            # 構造圧力係数（1.0〜1.5）
    x: float            # 補正後入力値（s_raw × c）
    final_score: float  # 最終スコア（0〜100）