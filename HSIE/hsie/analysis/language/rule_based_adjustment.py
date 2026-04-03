# -*- coding: utf-8 -*-

from .dto.bert_score_dto import BertScoreDTO


# =========================
# ■ メイン
# =========================
def apply_rules(utterance, score: BertScoreDTO) -> BertScoreDTO:
    """
    スコア補正のみ（加算限定）
    """

    text = utterance.text

    # コピー（immutable DTO を mutable dict として扱う）
    new_score = {
        "I_dir": score.I_dir,
        "I_ind": score.I_ind,
        "C_shift": score.C_shift,
        "C_block": score.C_block,
        "D_p": score.D_p,
        "D_a": score.D_a,
        "D_v": score.D_v,
    }

    # =========================
    # ■ 各ルール適用
    # =========================
    _apply_insult_rules(text, utterance, new_score)
    _apply_command_rules(text, new_score)
    _apply_denial_rules(text, new_score)

    # 0〜100クリップ
    _clip_scores(new_score)

    return BertScoreDTO(**new_score)


# =========================
# ■ 侮辱補強（I_ind）
# =========================
def _apply_insult_rules(text, utterance, score):

    # ■ 婉曲表現
    insult_patterns = [
        "普通は",
        "なんでできない",
        "なんで分からない",
        "そういうところ",
        "さすがだね",  # 皮肉
    ]

    for p in insult_patterns:
        if p in text:
            score["I_ind"] += 10

    # ■ 疑問 + 否定（例：なんでできないの？）
    if "?" in text or "？" in text:
        if any(n in text for n in ["ない", "できない", "無理"]):
            score["I_ind"] += 15

    # ■ 文脈による皮肉（前文あり）
    if utterance.context_window:
        prev = utterance.context_window[0]
        if prev and any(n in prev.text for n in ["ミス", "失敗"]):
            if any(p in text for p in ["すごいね", "さすが"]):
                score["I_ind"] += 20


# =========================
# ■ 命令補強（C_block / C_shift）
# =========================
def _apply_command_rules(text, score):

    # ■ 強制語
    strong_commands = [
        "今すぐ",
        "早く",
        "すぐやれ",
        "黙って",
        "いいから",
    ]

    for cmd in strong_commands:
        if cmd in text:
            score["C_block"] += 15

    # ■ imperative（〜しろ）
    if text.endswith("しろ") or text.endswith("やれ"):
        score["C_block"] += 20

    # ■ 責任転嫁
    shift_patterns = [
        "お前のせい",
        "お前が悪い",
        "自分でなんとかしろ",
    ]

    for p in shift_patterns:
        if p in text:
            score["C_shift"] += 20


# =========================
# ■ 否定補強（D系）
# =========================
def _apply_denial_rules(text, score):

    # ■ 人格否定
    personality_denials = [
        "ダメな人間",
        "性格が悪い",
        "終わってる",
    ]

    for p in personality_denials:
        if p in text:
            score["D_p"] += 20

    # ■ 能力否定
    ability_denials = [
        "できない",
        "向いてない",
        "無能",
    ]

    for p in ability_denials:
        if p in text:
            score["D_a"] += 10

    # ■ 価値否定
    value_denials = [
        "意味ない",
        "無駄",
        "いらない",
    ]

    for p in value_denials:
        if p in text:
            score["D_v"] += 15

    # ■ 否定連鎖（強化）
    neg_count = sum(text.count(n) for n in ["ない", "無理", "ダメ"])

    if neg_count >= 2:
        score["D_p"] += 10
        score["D_a"] += 10


# =========================
# ■ クリップ処理
# =========================
def _clip_scores(score):
    score["I_dir"] = min(score["I_dir"], 100)
    score["I_ind"] = min(score["I_ind"], 100)
    score["C_shift"] = min(score["C_shift"], 100)
    score["C_block"] = min(score["C_block"], 100)
    score["D_p"] = min(score["D_p"], 100)
    score["D_a"] = min(score["D_a"], 100)
    score["D_v"] = min(score["D_v"], 100)