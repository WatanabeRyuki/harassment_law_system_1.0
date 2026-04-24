"""
HSIE 統合結果のテキスト整形（ターミナル表示用）。

DTO から L / S / HSI の閲覧用レポート文字列を組み立てるのみ（分析ロジックは持たない）。
"""

from __future__ import annotations


def format_report(language_result, structure_results, analysis_score_result) -> str:
    lines: list[str] = []

    lines.append("=== Language Aggression ===")
    lines.append("")
    lines.append("[speaker_scores]")
    for sid in sorted(language_result.speaker_scores.keys()):
        lines.append(f"  {sid}: {language_result.speaker_scores[sid]}")
    lines.append("")
    lines.append(f"total_score: {language_result.total_score}")
    lines.append("")
    lines.append("[evidences]")
    for ev in language_result.evidences:
        lines.append(f"[{ev.score}] {ev.speaker_id}: {ev.text}")
    lines.append("")

    lines.append("=== Structure Aggression ===")
    lines.append("")
    for sid in sorted(structure_results.keys()):
        sr = structure_results[sid]
        lines.append(f"{sid}:")
        lines.append(f"  final_score: {sr.final_score}")
        lines.append(f"  s_raw: {sr.s_raw}")
        lines.append(f"  c: {sr.c}")
        lines.append(f"  turn_occupancy: {sr.turn_occupancy}")
        lines.append(f"  interruption_rate: {sr.interruption_rate}")
        lines.append(f"  negation_score: {sr.negation_score}")
        lines.append(f"  used_inversion_logic: {sr.used_inversion_logic}")
        lines.append("")

    lines.append("=== Analysis Score ===")
    lines.append("")
    for sid in sorted(analysis_score_result.speaker_results.keys()):
        ar = analysis_score_result.speaker_results[sid]
        lines.append(f"{sid}:")
        lines.append(f"  hsi_score: {ar.hsi_score}")
        lines.append(f"  language_score: {ar.language_score}")
        lines.append(f"  structure_score: {ar.structure_score}")
        lines.append(f"  turn_occupancy: {ar.turn_occupancy}")
        lines.append(f"  interruption_rate: {ar.interruption_rate}")
        lines.append(f"  negation_score: {ar.negation_score}")
        lines.append(f"  sai_score: {ar.sai_score}")
        lines.append(f"  α: {ar.alpha}")
        lines.append(f"  β: {ar.beta}")
        lines.append(f"  condition: {ar.applied_condition}")
        lines.append("  evidences:")
        if not ar.evidences:
            lines.append("    (none)")
        else:
            for ev in ar.evidences:
                categories = ", ".join(ev.categories) if ev.categories else "-"
                lines.append(
                    f"    - [{ev.score}] {ev.text} (categories: {categories})"
                )
        lines.append("")

    return "\n".join(lines)
