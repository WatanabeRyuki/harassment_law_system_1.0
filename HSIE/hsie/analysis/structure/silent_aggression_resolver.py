import re

class SilentAggressionResolver:
    def __init__(self, threshold_sai=0.45):
        self.threshold_sai = threshold_sai
        # 問い詰めキーワード
        self.prompt_keywords = ["で", "だから", "それで", "意味ない", "違う", "自分で考えろ", "説明して", "どうするの","甘い","話にならない","それだけ"]
        # 防御（謝罪）キーワード
        self.defense_keywords = ["すみません", "申し訳", "失礼します", "反省", "私のミス", "ええと", "あ、はい"]

    def resolve(self, speaker_stats, utterances):
        """
        speaker_stats: {speaker_id: {"occupancy": float, "avg_chars": float, "utterance_count": int}}
        utterances: List of dicts with "speaker_id" and "text"
        """
        speaker_ids = list(speaker_stats.keys())
        if len(speaker_ids) != 2:
            return speaker_stats, 0.0, None

        def _speaker_id(u):
            # Accept both legacy dicts and current UtteranceDTO objects.
            return u["speaker_id"] if isinstance(u, dict) else u.speaker_id

        def _text(u):
            return u["text"] if isinstance(u, dict) else u.text

        s1, s2 = speaker_ids[0], speaker_ids[1]
        
        # 占有率が高い方を A、低い方を B とする
        if speaker_stats[s1]["occupancy"] > speaker_stats[s2]["occupancy"]:
            p_high, p_low = s1, s2
        else:
            p_high, p_low = s2, s1

        occ_high = speaker_stats[p_high]["occupancy"]
        occ_low = speaker_stats[p_low]["occupancy"]
        avg_high = speaker_stats[p_high]["avg_chars"]
        avg_low = speaker_stats[p_low]["avg_chars"]

        # --- 第1段階: 反転トリガー (ゲート制限) ---
        # 1. 占有率の乖離が 0.5 以上
        # 2. 平均文字数が 5倍以上の差（被害者が長く喋らされている）
        if (occ_high - occ_low < 0.5) or (avg_low == 0 or (avg_high / avg_low < 5.0)):
            return speaker_stats, 0.0, None

        # --- 第2段階: SAIスコアの算出 ---
        # A. 促し・切り捨て指数 (S_prompt) : 低占有者側をチェック
        low_utters = [_text(u) for u in utterances if _speaker_id(u) == p_low]
        s_prompt_count = 0
        for text in low_utters:
            is_short = len(text) <= 12
            has_kw = any(kw in text for kw in self.prompt_keywords)
            has_q = text.endswith("？") or text.endswith("?")
            if is_short and (has_kw or has_q):
                s_prompt_count += 1
        s_prompt = s_prompt_count / len(low_utters) if low_utters else 0

        # B. 防御姿勢指数 (S_defense) : 高占有者側をチェック
        high_utters = [_text(u) for u in utterances if _speaker_id(u) == p_high]
        s_defense_count = 0
        for text in high_utters:
            if any(kw in text for kw in self.defense_keywords):
                s_defense_count += 1
        s_defense = s_defense_count / len(high_utters) if high_utters else 0

        # SAI最終計算
        sai_score = (0.6 * s_prompt) + (0.4 * s_defense)

        # --- 第3段階: 占有率の反転 ---
        is_reversed = False
        if sai_score >= self.threshold_sai:
            is_reversed = True
            # 占有率をスワップ
            speaker_stats[p_high]["occupancy"], speaker_stats[p_low]["occupancy"] = occ_low, occ_high

        return speaker_stats, sai_score, (p_low if is_reversed else None)