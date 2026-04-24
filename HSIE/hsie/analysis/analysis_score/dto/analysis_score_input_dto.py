from dataclasses import dataclass
from typing import Dict, List

# 外部DTO（既存）
from analysis.language.dto.language_result_dto import LanguageResultDTO
from analysis.structure.dto.structure_result_dto import StructureResultDTO


@dataclass
class AnalysisScoreInputDTO:
    language_result: LanguageResultDTO
    structure_results: Dict[str, StructureResultDTO]