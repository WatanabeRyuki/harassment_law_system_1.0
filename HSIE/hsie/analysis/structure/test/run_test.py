import json
import os
import sys

# Ensure the repo's `hsie/` directory is on `sys.path` so imports like
# `analysis.structure...` resolve correctly when running this file directly.
current_dir = os.path.dirname(__file__)
hsie_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if hsie_root not in sys.path:
    # Append (not prepend) so a real installed `janome` (if any) still wins.
    sys.path.append(hsie_root)

from analysis.structure.structure_analyzer import analyze_structure
from analysis.structure.debug_analyzer import analyze_with_debug


def run_test(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File not found -> {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n{'='*50}")
    print(f"  TEST EXECUTION: {os.path.basename(file_path)}")
    print(f"{'='*50}")

    # =========================
    # ① DEBUG INFO: 全工程の可視化
    # =========================
    print("\n===== 1. DEBUG INFO (INTERNAL MODULES) =====")
    debug = analyze_with_debug(data)
    
    print(f"Utterance Count : {debug.get('utterance_count')}")
    print(f"Turn Count      : {debug.get('turn_count')}")
    print(f"Speakers        : {', '.join(debug.get('speakers', []))}")

    # SAI (Silent Aggression Indicator) の結果表示
    print(f"\n--- Silent Aggression Analysis ---")
    print(f"  SAI Score     : {debug.get('sai_score'):.4f}")
    if debug.get('is_reversed'):
        print(f"  Status        : [REVERSED] Logic Applied")
        print(f"  Aggressor ID  : {debug.get('aggressor_id')}")
    else:
        print(f"  Status        : [NORMAL] No Inversion")

    for sid in debug.get('speakers', []):
        print(f"\n--- Speaker: {sid} ---")
        
        # interruption (DTO)
        inter = debug["interruption_results"].get(sid)
        print(f"  [Interruption] Count: {inter.interruption_count}, Rate: {inter.interruption_rate:.4f}")
        
        # occupancy (Raw vs Resolved)
        raw_occ = debug["raw_occupancy_results"].get(sid, 0.0)
        resolved_occ = debug["turn_occupancy_results"].get(sid, 0.0)
        if debug.get('is_reversed'):
            print(f"  [Occupancy]    Raw: {raw_occ:.4f} -> Resolved: {resolved_occ:.4f} (*REVERSED*)")
        else:
            print(f"  [Occupancy]    Value: {resolved_occ:.4f}")
        
        # negation
        neg = debug["negation_results"].get(sid, 0.0)
        print(f"  [Negation]     Score: {neg:.4f}")
        
        # structural pressure (c)
        c = debug["c_results"].get(sid, 1.0)
        print(f"  [Pressure (c)] Value: {c:.4f}")
        
        # S_raw / X / Final
        s_raw = debug["s_raw_results"].get(sid, 0.0)
        x_corr = debug["x_results"].get(sid, 0.0)
        final = debug["final_score_results"].get(sid, 0.0)
        print(f"  [S_raw]        Value: {s_raw:.2f}")
        print(f"  [X_corrected]  Value: {x_corr:.2f}")
        print(f"  [FINAL SCORE]  Value: {final:.2f}")

    # =========================
    # ② FINAL RESULTS: DTOの確認
    # =========================
    print("\n===== 2. FINAL RESULTS (StructureResultDTO) =====")
    # 戻り値が (results, sai_score, aggressor_id) に変更されていることに対応
    results, final_sai, final_aggressor = analyze_structure(data)
    
    for sid, dto in results.items():
        # 加害者として判定されている場合にアスタリスクを表示
        is_aggr = " [AGRESSOR]" if sid == final_aggressor else ""
        print(f"--- {sid}{is_aggr} ---")
        print(f"  Speaker ID  : {dto.speaker_id}")
        print(f"  S_raw       : {dto.s_raw:.2f}")
        print(f"  C (Pressure): {dto.c:.4f}")
        print(f"  X (Input)   : {dto.x:.2f}")
        print(f"  FINAL SCORE : {dto.final_score:.2f}")

    print(f"\n{'='*50}")


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    # 静かな圧のテストケース（test_case_high_pressure4.json）を指定
    json_path = os.path.join(current_dir, "test_case_sexual.json")
    
    run_test(json_path)