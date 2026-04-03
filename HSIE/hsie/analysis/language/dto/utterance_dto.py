from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageUtteranceDTO:
    """
    前処理後の発話単位データ（分析用）
    """

    utterance_id: str
    speaker_id: str

    text: str

    start_time: float
    end_time: float

    # =========================
    # ■ 文脈（軽量参照）
    # =========================
    prev_text: str
    next_text: str

    @property
    def context_window(self):
        """
        後方互換: [prev, current, next] で .text 参照可能な形式を返す
        """
        class _Ctx:
            def __init__(self, text: str):
                self.text = text

        prev = _Ctx(self.prev_text) if self.prev_text else None
        curr = _Ctx(self.text)
        nxt = _Ctx(self.next_text) if self.next_text else None
        return [prev, curr, nxt]

    def __post_init__(self):
        # 時間整合性チェック
        if self.start_time > self.end_time:
            raise ValueError("start_time must be <= end_time")