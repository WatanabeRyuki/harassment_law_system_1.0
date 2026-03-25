from dataclasses import dataclass

@dataclass(frozen=True)
class ScoreDTO:
    """
    話者ごとの中間スコア統合DTO
    """
    speaker_id: str            # 対象話者ID
    turn_occupancy: float      # ターン占有率（0〜1想定）
    interruption_rate: float   # 割り込み率（0〜1想定）
    negation_score: float      # 否定連鎖スコア（0〜1想定）
    s_raw: float               # 正規化後スコア（0〜100）