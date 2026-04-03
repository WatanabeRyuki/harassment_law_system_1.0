# debug_analyzer.py

from .preprocessing import preprocess
from .bert_inference import run_bert
from .rule_based_adjustment import apply_rules
from .subscore import calc_subscores
from .l_raw import calc_l_raw
from .category import detect_categories
from .evidence_extractor import extract
from .evidence_builder import build
from .sorter import sort_by_score
# calc_total を直接呼ぶか、内部で同様の計算を再現して表示します
from .total_score import calc_total 


def debug_analyze(input_dto):
    print("======================================")
    print("      HSIE DEBUG ANALYSIS START")
    print("======================================")

    utterances = preprocess(input_dto)
    
    # 全体の録音時間を取得（input_dto の仕様に合わせて調整してください）
    # 一般的には最後のアタランスの end_time や、DTOの duration 属性から取得します
    duration_sec = getattr(input_dto, 'duration', 0.0)
    if duration_sec <= 0 and utterances:
        duration_sec = utterances[-1].end_time if hasattr(utterances[-1], 'end_time') else 0.0

    evidences = []

    # =========================
    # 発話単位解析 (変更なし)
    # =========================
    for idx, u in enumerate(utterances):
        print("\n--------------------------------------")
        print(f"[Utterance {idx}]")
        print(f"Speaker: {u.speaker_id}")
        print(f"Text   : {u.text}")

        bert = run_bert(u)
        adjusted = apply_rules(u, bert)
        sub = calc_subscores(adjusted)
        l_raw = calc_l_raw(sub.I, sub.C, sub.D)
        
        print(f"\n[L_raw]: {l_raw:.2f}")
        categories = detect_categories(sub.I, sub.C, sub.D)
        print(f"[Categories]: {categories}")

        ev = extract(u, l_raw, categories)
        if ev:
            print("\n>>> Evidence DETECTED <<<")
            print(f"Score      : {ev.score:.2f}")
            print(f"Categories : {ev.categories}")
            evidences.append(ev)
        else:
            print("\n(No Evidence)")

    # =========================
    # Evidence集約
    # =========================
    print("\n======================================")
    print("      EVIDENCE SUMMARY")
    print("======================================")
    print(f"Total Duration: {duration_sec:.2f} sec")
    print(f"Time Factor (unit=30s): {max(duration_sec / 30.0, 1.0):.2f}")

    grouped = build(evidences)
    speaker_scores = {}

    for speaker, ev_list in grouped.items():
        print(f"\n[Speaker: {speaker}]")

        # 単純加算なのでソートの必要性は薄いですが、見やすさのため残します
        sorted_list = sort_by_score(ev_list)

        print("\n-- Detected Evidences --")
        raw_total = 0.0
        for i, e in enumerate(sorted_list):
            print(f"{i+1}. Score={e.score:.2f} | Text={e.text}")
            raw_total += e.score

        # =========================
        # 時間正規化の可視化 (ここが重要な変更点)
        # =========================
        print("\n-- Time Normalization Analysis --")
        print(f"Raw Total Score : {raw_total:.2f}")
        
        # total_score.py と同じロジックを再現
        time_factor = max(duration_sec / 30.0, 1.0)
        normalized_score = raw_total / time_factor
        
        print(f"Calculation     : {raw_total:.2f} / {time_factor:.2f} (Time Factor)")
        print(f"Normalized      : {normalized_score:.2f}")

        # 最終的な calc_total の結果を取得
        final_score = calc_total(ev_list, duration_sec)
        speaker_scores[speaker] = final_score

        print(f"[Final Score]   : {final_score:.2f}")

    print("\n======================================")
    print("      FINAL RESULT")
    print("======================================")

    for speaker, score in speaker_scores.items():
        # デザイン部門としての視点: 簡易的なバーチャート表示などを追加すると直感的です
        bar = "█" * int(score / 5)
        print(f"{speaker:10}: {score:6.2f} {bar}")

    print("\n======================================")
    print("      DEBUG END")
    print("======================================")

    return {
        "speaker_scores": speaker_scores,
        "evidences": evidences
    }