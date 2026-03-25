from dataclasses import dataclass

@dataclass(frozen=True)
class InterruptionDTO:
    """
    話者ごとの割り込み分析結果DTO（InterruptionDetectionの出力）
    """
    speaker_id: str               # 対象話者ID（誰の分析結果か）
    total_turns: int              # 会話全体の総ターン数
    interruption_count: int       # この話者が相手の発話を遮った回数
    interruption_rate: float      # この話者の割り込み率（0〜1）