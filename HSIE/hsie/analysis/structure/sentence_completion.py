from typing import List

from .dto.utterance_dto import MorphToken


# 日本語の格助詞リスト（設計準拠）
CASE_PARTICLES = {"が", "を", "に", "へ", "で", "と", "から", "まで"}


def is_sentence_complete(tokens: List[MorphToken]) -> bool:
    if not tokens:
        return False

    last = tokens[-1]
    last_surface = last.surface
    last_pos = last.pos
    last_pos_detail = getattr(last, 'pos_detail', "")

    # =========================
    # ① 強制未完（言い差し）
    # =========================
    if last_pos == "助詞" and last_surface in {"けど", "ので", "から", "し", "て", "ながら"}:
        return False

    # 接続詞単体で終わる（かなり重要）
    if len(tokens) <= 2 and last_surface in {"だから", "でも", "けど", "で"}:
        return False

    # フィラー系（会話特有）
    if last_surface in {"えっと", "あの", "その"}:
        return False

    # =========================
    # ② 強制完結（会話的成立）
    # =========================

    # 感動詞
    if last_pos == "感動詞":
        return True

    # 疑問（？ or か）
    if last_surface in {"?", "？"}:
        return True

    if last_surface == "か" and last_pos == "助詞":
        return True

    # 終助詞
    if last_surface in {"ね", "よ", "な", "ぞ", "さ"}:
        return True

    # =========================
    # ③ 文末構造チェック（重要）
    # =========================

    if last_pos in {"動詞", "助動詞"}:
        # 連用形っぽい終わりを排除
        if last_pos_detail in {"連用形"}:
            return False
        return True

    # =========================
    # ④ 格助詞終わり → 未完
    # =========================
    if last_surface in CASE_PARTICLES:
        return False

    # =========================
    # ⑤ 名詞止め
    # =========================
    if last_pos == "名詞":
        return True

    # =========================
    # ⑥ 最終保険（弱め）
    # =========================
    return _has_verb(tokens)


# =========================
# 内部関数（本実装）
# =========================

def _has_verb(tokens: List[MorphToken]) -> bool:
    """
    動詞が存在するか判定
    """
    for token in tokens:
        if token.pos == "動詞":
            return True
    return False


def _has_case_particle(tokens: List[MorphToken]) -> bool:
    """
    格助詞が存在するか判定
    """
    for token in tokens:
        if token.surface in CASE_PARTICLES and token.pos == "助詞":
            return True
    return False


def _validate_case_structure(tokens: List[MorphToken]) -> bool:
    """
    格助詞と述語の対応関係を簡易的に検証する（暫定）

    現在のルール：
    ・格助詞があるが動詞がない → 未完
    ・格助詞 + 動詞がある → 成立

    ※ 将来ここをCCGベースに拡張可能
    """

    has_verb = _has_verb(tokens)

    if has_verb:
        return True

    return False