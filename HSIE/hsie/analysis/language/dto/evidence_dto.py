from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class EvidenceDTO:
    """
    言語攻撃性の証拠ユニット（監査・保存対象）
    """

    utterance_id: str
    speaker_id: str

    start_time: float
    end_time: float

    text: str

    score: float  # L_raw

    categories: Tuple[str, ...]  # immutable化

    def __post_init__(self):
        # =========================
        # ■ scoreの安全化
        # =========================
        object.__setattr__(self, "score", _clip(self.score))

        # =========================
        # ■ 時間整合性チェック
        # =========================
        if self.start_time > self.end_time:
            raise ValueError("start_time must be <= end_time")

        # =========================
        # ■ categoriesをtuple化
        # =========================
        object.__setattr__(self, "categories", tuple(self.categories))


# =========================
# ■ 共通ユーティリティ
# =========================
def _clip(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return float(value)