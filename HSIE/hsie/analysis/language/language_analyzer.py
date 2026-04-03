from .preprocessing import preprocess
from .bert_inference import run_bert
from .rule_based_adjustment import apply_rules
from .subscore import calc_subscores
from .l_raw import calc_l_raw
from .category import detect_categories
from .evidence_extractor import extract
from .evidence_builder import build
from .sorter import sort_by_score
from .total_score import calc_total
from .finalizer import finalize

from .dto.language_result_dto import LanguageResultDTO


def analyze(input_dto):
    # =========================
    # ■ 前処理
    # =========================
    utterances = preprocess(input_dto)

    evidences = []

    # =========================
    # ■ 発話単位処理
    # =========================
    for u in utterances:
        bert = run_bert(u)
        adjusted = apply_rules(u, bert)
        sub = calc_subscores(adjusted)

        l_raw = calc_l_raw(sub.I, sub.C, sub.D)
        categories = detect_categories(sub.I, sub.C, sub.D)

        ev = extract(u, l_raw, categories)
        if ev:
            evidences.append(ev)

    # =========================
    # ■ speaker別グルーピング
    # =========================
    grouped = build(evidences)

    speaker_scores = {}

    # 全speakerを保証（攻撃ゼロも含む）
    for speaker in input_dto.speakers:
        ev_list = grouped.get(speaker, [])

        sorted_list = sort_by_score(ev_list)
        total = calc_total(sorted_list, input_dto.conversation_duration)
        speaker_scores[speaker] = finalize(total)

    # =========================
    # ■ 全体スコア算出（最大値採用）
    # =========================
    total_score = max(speaker_scores.values()) if speaker_scores else 0.0

    # =========================
    # ■ evidence全体ソート
    # =========================
    evidences_sorted = sort_by_score(evidences)

    # =========================
    # ■ 最終DTO
    # =========================
    return LanguageResultDTO(
        speaker_scores=speaker_scores,
        total_score=total_score,
        evidences=evidences_sorted,
        conversation_duration=input_dto.conversation_duration
    )