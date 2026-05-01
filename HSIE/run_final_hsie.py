from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
HSIE_PACKAGE_DIR = PROJECT_ROOT / "hsie"
LEGAL_RETRIEVAL_DIR = PROJECT_ROOT / "hsie" / "legal_retrieval"
if str(HSIE_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(HSIE_PACKAGE_DIR))
if str(LEGAL_RETRIEVAL_DIR) not in sys.path:
    sys.path.insert(0, str(LEGAL_RETRIEVAL_DIR))

from hsie.analysis.analysis_score.analysis_score_analyzer import analyze as analysis_score_analyze
from hsie.analysis.analysis_score.dto.analysis_score_input_dto import AnalysisScoreInputDTO
from hsie.analysis.language.language_analyzer import analyze as language_analyze
from hsie.analysis.structure.structure_analyzer import analyze_structure
from hsie.hsi_result.dto.hsi_result_input_dto import AnalysisEvidenceDTO, HSIResultInputDTO
from hsie.hsi_result.hsi_result_analyzer import HSIResultAnalyzer
from hsie.legal_retrieval.dto.input_dto import LegalRetrievalInputDTO
from hsie.legal_retrieval import legal_retrieval_analyzer as legal_retrieval_analyzer
from run_hsie import (
    _build_entrypoint_controller,
    _build_preprocess_controller,
    _ensure_dirs,
    _save_entrypoint_json,
    _validate_audio_file,
    _validate_librosa,
)

FINAL_EVIDENCE_DIR = Path("data/final_evidence")


class _LanguageInputUtterance:
    __slots__ = ("utterance_id", "speaker_id", "text", "start_time", "end_time")

    def __init__(self, utterance: dict[str, Any]) -> None:
        self.utterance_id = utterance["utterance_id"]
        self.speaker_id = utterance["speaker_id"]
        self.text = utterance["text"]
        self.start_time = utterance["start_time"]
        self.end_time = utterance["end_time"]


class _LanguageInputDTO:
    __slots__ = ("speakers", "conversation_duration", "utterances")

    def __init__(self, data: dict[str, Any]) -> None:
        self.speakers = [speaker["speaker_id"] for speaker in data.get("speakers", [])]
        duration = data.get("conversation_duration")
        if duration is None:
            duration = (data.get("source_reference") or {}).get("duration", 0.0)
        self.conversation_duration = float(duration or 0.0)
        self.utterances = [_LanguageInputUtterance(u) for u in data.get("utterances", [])]


def _current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full HSIE pipeline and save final evidence JSON.")
    parser.add_argument("audio_file", help="Path to input audio file")
    return parser.parse_args()


def _to_dict(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _to_dict(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_dict(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_dict(v) for v in value]
    return value


def _with_process_id(payload: Any, process_id: str) -> Any:
    payload_dict = _to_dict(payload)
    if isinstance(payload_dict, dict):
        return {"process_id": process_id, **payload_dict}
    return {"process_id": process_id, "value": payload_dict}


def _convert_to_hsi_input(speaker: Any) -> HSIResultInputDTO:
    evidences = []
    for ev in getattr(speaker, "evidences", []) or []:
        categories = tuple((getattr(ev, "categories", None) or []))
        evidences.append(
            AnalysisEvidenceDTO(
                utterance_id=getattr(ev, "utterance_id", ""),
                speaker_id=getattr(ev, "speaker_id", ""),
                start_time=float(getattr(ev, "start_time", 0.0) or 0.0),
                end_time=float(getattr(ev, "end_time", 0.0) or 0.0),
                text=getattr(ev, "text", ""),
                score=float(getattr(ev, "score", 0.0) or 0.0),
                categories=categories,
            )
        )

    return HSIResultInputDTO(
        speaker_id=getattr(speaker, "speaker_id", ""),
        hsi_score=float(getattr(speaker, "hsi_score", 0.0) or 0.0),
        language_score=float(getattr(speaker, "language_score", 0.0) or 0.0),
        structure_score=float(getattr(speaker, "structure_score", 0.0) or 0.0),
        turn_occupancy=float(getattr(speaker, "turn_occupancy", 0.0) or 0.0),
        interruption_rate=float(getattr(speaker, "interruption_rate", 0.0) or 0.0),
        negation_score=float(getattr(speaker, "negation_score", 0.0) or 0.0),
        sai_score=float(getattr(speaker, "sai_score", 0.0) or 0.0),
        evidences=evidences,
        applied_condition=getattr(speaker, "applied_condition", ""),
        alpha=float(getattr(speaker, "alpha", 0.0) or 0.0),
        beta=float(getattr(speaker, "beta", 0.0) or 0.0),
    )


def _build_final_output(
    process_id: str,
    entry_point_result: dict[str, Any],
    preprocessed_result: dict[str, Any],
    language_result: Any,
    structure_results: dict[str, Any],
    analysis_score_result: Any,
    hsi_results: dict[str, Any],
    legal_results: dict[str, Any],
) -> dict[str, Any]:
    return {
        "metadata": {
            "process_id": process_id,
            "created_at": _current_timestamp(),
            "pipeline_version": "HSIE_v1.0",
        },
        "source": {
            "entry_point": _with_process_id(entry_point_result, process_id),
            "preprocessed_evidence": _with_process_id(preprocessed_result, process_id),
        },
        "analysis": {
            "language": {
                "process_id": process_id,
                "speaker_results": _to_dict(language_result.speaker_scores),
                "total_score": _to_dict(language_result.total_score),
                "evidences": _to_dict(language_result.evidences),
            },
            "structure": {
                "process_id": process_id,
                "speaker_results": _to_dict(structure_results),
            },
            "integration": {
                "process_id": process_id,
                "speaker_results": _to_dict(analysis_score_result.speaker_results),
            },
        },
        "interpretation": {
            "process_id": process_id,
            "speaker_results": _to_dict(hsi_results),
        },
        "legal": {
            "process_id": process_id,
            "speaker_results": _to_dict(legal_results),
        },
    }


def _is_ollama_connection_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "localhost" in message and "11434" in message


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("hsie.final_pipeline")

    args = _parse_args()
    process_id = str(uuid.uuid4())
    audio_path = Path(args.audio_file).resolve()

    logger.info("HSIE final pipeline started. process_id=%s", process_id)

    try:
        _validate_audio_file(audio_path)
        duration_sec, sample_rate = _validate_librosa(audio_path)
        _ensure_dirs()
        FINAL_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logger.exception("Initialization failed: %s", exc)
        raise

    try:
        logger.info("Running EntryPoint layer...")
        entrypoint_controller = _build_entrypoint_controller()
        evidence_id = entrypoint_controller.run(
            audio_path=audio_path,
            session_id=process_id,
            speaker_id="speaker_0",
            language="ja",
        )
        entry_point_result = _save_entrypoint_json(evidence_id)
        logger.info("EntryPoint layer completed.")
    except Exception as exc:
        logger.exception("EntryPoint layer failed: %s", exc)
        raise

    try:
        logger.info("Running PreprocessedEvidence layer...")
        try:
            preprocess_controller = _build_preprocess_controller(audio_path)
            preprocessed_result = preprocess_controller.execute(
                entry_point_result,
                audio_sampling_rate=sample_rate,
                audio_duration=Decimal(str(duration_sec)),
            )
        except Exception as first_exc:
            if os.getenv("HSIE_LLM_BACKEND") is None and _is_ollama_connection_error(first_exc):
                logger.warning(
                    "Ollama connection failed. Retrying with passthrough backend."
                )
                os.environ["HSIE_LLM_BACKEND"] = "passthrough"
                preprocess_controller = _build_preprocess_controller(audio_path)
                preprocessed_result = preprocess_controller.execute(
                    entry_point_result,
                    audio_sampling_rate=sample_rate,
                    audio_duration=Decimal(str(duration_sec)),
                )
            else:
                raise
        logger.info("PreprocessedEvidence layer completed.")
    except Exception as exc:
        logger.exception("PreprocessedEvidence layer failed: %s", exc)
        raise

    try:
        logger.info("Running Analysis layer...")
        language_input = _LanguageInputDTO(preprocessed_result)
        language_result = language_analyze(language_input)
        structure_results, _sai_score, _aggressor_id = analyze_structure(preprocessed_result)
        analysis_score_result = analysis_score_analyze(
            AnalysisScoreInputDTO(
                language_result=language_result,
                structure_results=structure_results,
            )
        )
        logger.info("Analysis layer completed.")
    except Exception as exc:
        logger.exception("Analysis layer failed: %s", exc)
        raise

    try:
        logger.info("Running Interpretation layer...")
        hsi_results: dict[str, Any] = {}
        for speaker_id, speaker_score in analysis_score_result.speaker_results.items():
            hsi_input = _convert_to_hsi_input(speaker_score)
            hsi_result = HSIResultAnalyzer.execute(hsi_input)
            hsi_results[speaker_id] = hsi_result
        logger.info("Interpretation layer completed.")
    except Exception as exc:
        logger.exception("Interpretation layer failed: %s", exc)
        raise

    try:
        logger.info("Running LegalRetrieval layer...")
        legal_results: dict[str, Any] = {}
        for speaker_id, hsi_result in hsi_results.items():
            legal_input = LegalRetrievalInputDTO(
                speaker_id=hsi_result.speaker_id,
                search_queries=hsi_result.search_queries,
            )
            legal_result = legal_retrieval_analyzer.execute(legal_input)
            legal_results[speaker_id] = legal_result
        logger.info("LegalRetrieval layer completed.")
    except Exception as exc:
        logger.exception("LegalRetrieval layer failed: %s", exc)
        raise

    try:
        final_output = _build_final_output(
            process_id=process_id,
            entry_point_result=entry_point_result,
            preprocessed_result=preprocessed_result,
            language_result=language_result,
            structure_results=structure_results,
            analysis_score_result=analysis_score_result,
            hsi_results=hsi_results,
            legal_results=legal_results,
        )
        save_path = FINAL_EVIDENCE_DIR / f"{process_id}.json"
        save_path.write_text(
            json.dumps(final_output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Final evidence JSON saved: %s", save_path)
    except Exception as exc:
        logger.exception("Final output save failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
