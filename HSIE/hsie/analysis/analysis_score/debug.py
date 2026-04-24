def debug_print_result(result_dto, input_dto=None):
    print("\n===== AnalysisScore Debug =====")

    if input_dto is not None and input_dto.structure_results:
        sample = next(iter(input_dto.structure_results.values()))
        print(f"\n[Structure / SAI]")
        print(f"  SAI Score              : {sample.sai_score:.4f}")
        print(f"  Inversion logic applied: {sample.used_inversion_logic}")

    for speaker_id, data in result_dto.speaker_results.items():
        print("\n------------------------------")
        print(f"Speaker       : {speaker_id}")
        print(f"HSI           : {data.hsi_score:.2f}")
        print(f"L (Language)  : {data.language_score:.2f}")
        print(f"S (Structure) : {data.structure_score:.2f}")
        print(f"SAI           : {data.sai_score:.4f}")
        print(f"Condition     : {data.applied_condition}")
        print(f"α, β          : {data.alpha}, {data.beta}")
        print(f"Evidence Count: {len(data.evidences)}")

        print("Evidences:")
        if not data.evidences:
            print("  (none)")
        else:
            for e in data.evidences:
                categories = ", ".join(e.categories) if e.categories else "-"
                print(f"  - [{e.score:.2f}] {e.text} (categories: {categories})")