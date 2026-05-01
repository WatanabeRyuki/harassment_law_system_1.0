# hsie/hsi_result/debug_ui.py

from typing import List
from .hsi_result_analyzer import HSIResultAnalyzer
from .dto.hsi_result_input_dto import HSIResultInputDTO


def print_header(title: str):
    print("\n" + "=" * 50)
    print(f"{title}")
    print("=" * 50)


def print_list(title: str, items: List[str]):
    print(f"\n[{title}]")
    if not items:
        print("  (none)")
        return

    for item in items:
        print(f"  - {item}")


def print_tag_mappings(mappings):
    print("\n[Tag Mappings]")
    if not mappings:
        print("  (none)")
        return

    for m in mappings:
        print(f"\n  ● {m.evidence_text}")
        print(f"    tags: {', '.join(m.derived_tags)}")
        print(f"    reason: {m.reason}")


def render_result(result):
    print_header(f"HSI Result (Speaker: {result.speaker_id})")

    print(f"\nRisk Level: {result.risk_level}")

    print_list("Legal Tags", result.legal_tags)
    print_list("Search Queries", result.search_queries)

    print_tag_mappings(result.tag_mappings)

    print("\n[Summary]")
    print(f"  {result.summary}")


# -----------------------------
# ■ 実行用関数
# -----------------------------

def run_debug(input_dto: HSIResultInputDTO):
    analyzer = HSIResultAnalyzer()
    result = analyzer.execute(input_dto)

    render_result(result)