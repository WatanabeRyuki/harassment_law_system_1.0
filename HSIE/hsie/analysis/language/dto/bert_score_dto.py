from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BertScoreDTO:
    """
    BERT推論結果（7指標）
    """

    I_dir: float
    I_ind: float
    C_shift: float
    C_block: float
    D_p: float
    D_a: float
    D_v: float

    def __post_init__(self):
        object.__setattr__(self, "I_dir", _safe(self.I_dir))
        object.__setattr__(self, "I_ind", _safe(self.I_ind))
        object.__setattr__(self, "C_shift", _safe(self.C_shift))
        object.__setattr__(self, "C_block", _safe(self.C_block))
        object.__setattr__(self, "D_p", _safe(self.D_p))
        object.__setattr__(self, "D_a", _safe(self.D_a))
        object.__setattr__(self, "D_v", _safe(self.D_v))


# =========================
# ■ 安全化関数
# =========================
def _safe(value: float) -> float:
    # NaN対策
    if value is None or math.isnan(value):
        return 0.0

    # クリップ
    if value < 0:
        return 0.0
    if value > 100:
        return 100.0

    return float(value)