from typing import Any, Dict

from .segmentation import segment_conversation
from .turn_detection import detect_turns
from .interruption import detect_interruptions
from .turn_occupancy import calc_turn_occupancy
from .negation_chain import detect_negation_chain
from .structural_pressure import calc_structural_pressure
from .scoring import calc_s_raw
from .correction import apply_correction
from .final_score import calc_final_score

# 静かな圧を解決するモジュール
from .silent_aggression_resolver import SilentAggressionResolver


def analyze_with_debug(data: Any) -> Dict:
    """
    各モジュールの出力をすべて可視化するデバッグ用関数。
    静かな圧（SAI）による反転プロセスも詳細に記録する。
    """

    debug = {}

    # ① segmentation
    utterances = segment_conversation(data)
    debug["utterance_count"] = len(utterances)
    
    if not utterances:
        return debug

    # 話者リストの特定
    speakers = list(set(u.speaker_id for u in utterances))
    debug["speakers"] = speakers

    # ② turn detection
    turns = detect_turns(utterances)
    debug["turn_count"] = len(turns)

    # ④ interruption
    inter_results = detect_interruptions(turns, speakers)
    debug["interruption_results"] = inter_results

    # ⑤ turn occupancy (反転前の生の値を保持)
    raw_occupancy = calc_turn_occupancy(utterances, speakers)
    debug["raw_occupancy_results"] = raw_occupancy

    # ⑥ negation chain
    negation_results = detect_negation_chain(turns, speakers)
    debug["negation_results"] = negation_results

    # ==========================================
    # 静かな圧（Silent Aggression）のデバッグ記録
    # ==========================================
    speaker_stats = {}
    for sid in speakers:
        speaker_utters = [u for u in utterances if u.speaker_id == sid]
        total_chars = sum(len(u.text) for u in speaker_utters)
        count = len(speaker_utters)
        speaker_stats[sid] = {
            "occupancy": raw_occupancy.get(sid, 0.0),
            "avg_chars": total_chars / count if count > 0 else 0,
            "utterance_count": count
        }

    resolver = SilentAggressionResolver()
    updated_stats, sai_score, aggressor_id = resolver.resolve(speaker_stats, utterances)
    
    debug["sai_score"] = sai_score
    debug["aggressor_id"] = aggressor_id
    debug["is_reversed"] = True if aggressor_id else False

    # 反転後の占有率を確定
    occupancy_results = {sid: updated_stats[sid]["occupancy"] for sid in speakers}
    debug["turn_occupancy_results"] = occupancy_results  # これが以降の計算に使われる

    # ==========================================
    # ⑦ structural pressure (反転後の占有率を使用)
    # ==========================================
    window_data = {
        sid: {
            "turn_occupancy": occupancy_results.get(sid, 0.0),
            "interruption_rate": inter_results[sid].interruption_rate,
            "negation_score": negation_results.get(sid, 0.0)
        } for sid in speakers
    }
    scores_by_window = [window_data]
    debug["scores_by_window"] = scores_by_window
    
    c_results = calc_structural_pressure(scores_by_window, speakers)
    debug["c_results"] = c_results

    # ⑧〜⑩ 最終計算プロセス
    s_raw_results = {}
    x_results = {}
    final_score_results = {}

    for sid in speakers:
        # ⑧ S_raw (反転後の占有率を使用)
        score_params = {
            "turn_occupancy": occupancy_results.get(sid, 0.0),
            "interruption_rate": inter_results[sid].interruption_rate,
            "negation_score": negation_results.get(sid, 0.0)
        }
        s_raw = calc_s_raw(score_params)
        s_raw_results[sid] = s_raw

        # ⑨ correction
        c = c_results.get(sid, 1.0)
        x = apply_correction(s_raw, c)
        x_results[sid] = x

        # ⑩ final score
        final_score = calc_final_score(x)
        final_score_results[sid] = final_score

    debug["s_raw_results"] = s_raw_results
    debug["x_results"] = x_results
    debug["final_score_results"] = final_score_results

    return debug