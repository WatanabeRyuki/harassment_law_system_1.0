from dataclasses import dataclass


@dataclass(frozen=True)
class SubScoreDTO:
    """
    サブスコア（意味統合後）

    I: 侮辱度
    C: 命令度
    D: 否定度
    """

    I: float
    C: float
    D: float

    def __post_init__(self):
        object.__setattr__(self, "I", _clip(self.I))
        object.__setattr__(self, "C", _clip(self.C))
        object.__setattr__(self, "D", _clip(self.D))


# =========================
# ■ 内部ユーティリティ
# =========================
def _clip(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0
    return float(value)