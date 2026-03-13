"""
HSIE end-to-end pipeline runner.

Usage:
    python run_hsie.py path/to/audio.wav

Flow:
    Audio path -> EntryPoint processing -> EntryPoint JSON (data/evidence/)
    -> PreprocessedEvidence pipeline -> PreprocessedEvidence JSON (data/after_evidence/)
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from decimal import Decimal
from pathlib import Path

# Librosa check (import-level only) and audio validation helpers
try:
    import librosa
except ImportError as e:
    raise ImportError(
        "librosa is required for audio loading and validation. "
        "Install with: pip install librosa"
    ) from e

try:
    import torchaudio
except Exception:
    torchaudio = None

from hsie.entrypoint.controllers.hsie_controller import HSIEController
from hsie.entrypoint.repository.evidence_repository import EvidenceRepository
from hsie.entrypoint.services.analysis_context_service import AnalysisContextService
from hsie.entrypoint.services.asr_result_structurer import ASRResultStructurer
from hsie.entrypoint.services.audio_metadata_service import AudioMetadataService
from hsie.entrypoint.services.whisper_asr_service import WhisperASRService
from hsie.llm.base import LLMClient
from hsie.llm.ollama_client import OllamaLLMClient
from hsie.llm.passthrough_client import PassthroughLLMClient
from hsie.preprocessed_evidence.adapters.entrypoint_adapter import EntrypointAdapter
from hsie.preprocessed_evidence.asr_postprocess.mapper import ASRResponseMapper
from hsie.preprocessed_evidence.asr_postprocess.prompt import ASRPromptBuilder
from hsie.preprocessed_evidence.asr_postprocess.service import ASRPostprocessService
from hsie.preprocessed_evidence.controller.preprocess_controller import PreprocessController
from hsie.preprocessed_evidence.diarization.mapper import DiarizationMapper
from hsie.preprocessed_evidence.dto.diarization import (
    DiarizationOutputDTO,
    SpeakerSegmentDTO,
)
from hsie.preprocessed_evidence.structuring.aligner import Aligner
from hsie.preprocessed_evidence.structuring.builder import Builder
from hsie.preprocessed_evidence.validators.consistency_checker import ConsistencyChecker
from hsie.preprocessed_evidence.waveform.mapper import WaveformMapper
from hsie.preprocessed_evidence.waveform.service import WaveformService
from hsie.preprocessed_evidence.waveform.ui_converter import WaveformUIConverter


# Output directories (create if missing)
EVIDENCE_DIR = Path("data/evidence")
AFTER_EVIDENCE_DIR = Path("data/after_evidence")
ENTRYPOINT_JSON_NAME = "entrypoint_evidence.json"
PREPROCESSED_JSON_NAME = "preprocessed_evidence.json"


def _parse_args() -> Path:
    if len(sys.argv) < 2:
        print("Usage: python run_hsie.py <audio_file_path>", file=sys.stderr)
        sys.exit(1)
    return Path(sys.argv[1]).resolve()


def _validate_audio_file(audio_path: Path) -> None:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not audio_path.is_file():
        raise ValueError(f"Path is not a file: {audio_path}")


def _validate_librosa(audio_path: Path) -> tuple[float, int]:
    """
    Try to load audio with librosa and return (duration_sec, sample_rate).
    If librosa fails due to environment issues (e.g., missing _lzma),
    fall back to torchaudio-based loading so that the pipeline can proceed.
    """
    # First, attempt standard librosa loading.
    try:
        audio, sr = librosa.load(str(audio_path), sr=None, mono=True)
        duration = librosa.get_duration(y=audio, sr=sr)
        print("librosa load succeeded.")
        return float(duration), int(sr)
    except Exception as e:
        warnings.warn(
            f"librosa failed to load audio from {audio_path}: {e}. "
            "Falling back to torchaudio for duration/sample-rate estimation."
        )

    # Fallback: use torchaudio if available.
    if torchaudio is None:
        raise RuntimeError(
            "librosa failed to load audio and torchaudio is not available "
            "for fallback loading."
        )

    try:
        waveform, sr = torchaudio.load(str(audio_path))
    except Exception as e:
        raise RuntimeError(
            f"Fallback torchaudio failed to load audio from {audio_path}: {e}"
        ) from e

    # waveform shape: (channels, num_samples)
    num_samples = waveform.shape[-1]
    duration_sec = num_samples / float(sr)
    print("Used torchaudio fallback to estimate duration and sample rate.")
    return float(duration_sec), int(sr)


def _ensure_dirs() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    AFTER_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def _build_llm_client() -> LLMClient:
    """
    Build LLM client for ASR postprocess.

    HSIE_LLM_BACKEND 環境変数でバックエンドを切り替え可能:
        - "ollama" (default): OllamaLLMClient を使用
        - "passthrough": PassthroughLLMClient を使用（補正なし）
    追加で以下の環境変数を利用可能:
        - HSIE_OLLAMA_MODEL (default: "qwen2.5:3b")
        - HSIE_OLLAMA_BASE_URL (default: "http://localhost:11434")
        - HSIE_OLLAMA_TEMPERATURE (default: "0.0")
    """
    backend = os.getenv("HSIE_LLM_BACKEND", "ollama").lower()

    if backend == "passthrough":
        return PassthroughLLMClient()

    if backend != "ollama":
        raise ValueError(
            f"Unsupported HSIE_LLM_BACKEND={backend!r}. "
            "Use 'ollama' or 'passthrough'."
        )

    model_name = os.getenv("HSIE_OLLAMA_MODEL", "qwen2.5:3b")
    base_url = os.getenv("HSIE_OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        temperature = float(os.getenv("HSIE_OLLAMA_TEMPERATURE", "0.0"))
    except ValueError:
        temperature = 0.0

    return OllamaLLMClient(
        model_name=model_name,
        base_url=base_url,
        temperature=temperature,
    )


def _build_entrypoint_controller() -> HSIEController:
    audio_metadata_service = AudioMetadataService()
    asr_service = WhisperASRService(model_name="base")
    analysis_context_service = AnalysisContextService()
    asr_result_structurer = ASRResultStructurer()
    evidence_repository = EvidenceRepository(base_dir=str(EVIDENCE_DIR))
    return HSIEController(
        audio_metadata_service=audio_metadata_service,
        asr_service=asr_service,
        analysis_context_service=analysis_context_service,
        asr_result_structurer=asr_result_structurer,
        evidence_repository=evidence_repository,
    )


def _save_entrypoint_json(evidence_id) -> dict:
    """Load saved evidence JSON and write to entrypoint_evidence.json. Return parsed dict."""
    file_path = EVIDENCE_DIR / f"{evidence_id}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"EntryPoint output not found: {file_path}")
    content = file_path.read_text(encoding="utf-8")
    entrypoint_path = EVIDENCE_DIR / ENTRYPOINT_JSON_NAME
    entrypoint_path.write_text(content, encoding="utf-8")
    return json.loads(content)


def _build_preprocess_controller(audio_path: Path) -> PreprocessController:
    adapter = EntrypointAdapter()
    llm_client = _build_llm_client()
    asr_service = ASRPostprocessService(
        prompt_builder=ASRPromptBuilder(),
        mapper=ASRResponseMapper(),
        llm_client=llm_client,
    )
    from hsie.preprocessed_evidence.diarization.config import create_pipeline
    from hsie.preprocessed_evidence.diarization.service import DiarizationService

    pipeline = create_pipeline()
    diarization_service = DiarizationService(pipeline=pipeline)
    diarization_mapper = DiarizationMapper()

    waveform_service = WaveformService()
    waveform_mapper = WaveformMapper(WaveformUIConverter(max_points=2000))
    aligner = Aligner()
    builder = Builder()
    checker = ConsistencyChecker()

    controller = PreprocessController(
        adapter=adapter,
        asr_service=asr_service,
        diarization_service=diarization_service,
        diarization_mapper=diarization_mapper,
        waveform_service=waveform_service,
        waveform_mapper=waveform_mapper,
        aligner=aligner,
        builder=builder,
        checker=checker,
    )

    return controller


def main() -> None:
    audio_path = _parse_args()
    _validate_audio_file(audio_path)

    duration_sec, sample_rate = _validate_librosa(audio_path)
    print(f"Audio: {audio_path} (duration={duration_sec:.2f}s, sr={sample_rate})")

    _ensure_dirs()

    # ----- EntryPoint -----
    print("Running EntryPoint pipeline...")
    controller = _build_entrypoint_controller()

    evidence_id = controller.run(
        audio_path=audio_path,
        session_id="session_001",
        speaker_id="speaker_0",
        language="ja",
    )
    print(f"EntryPoint completed. Evidence ID: {evidence_id}")

    entrypoint_dict = _save_entrypoint_json(evidence_id)
    entrypoint_json_path = EVIDENCE_DIR / ENTRYPOINT_JSON_NAME
    print(f"Saved EntryPoint JSON: {entrypoint_json_path}")

    # ----- PreprocessedEvidence -----
    print("Running PreprocessedEvidence pipeline...")
    preprocess_controller = _build_preprocess_controller(audio_path)
    result = preprocess_controller.execute(entrypoint_dict)

    # Save PreprocessedEvidence JSON with the same name as evidence_id
    out_path = AFTER_EVIDENCE_DIR / f"{evidence_id}.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved PreprocessedEvidence JSON: {out_path}")

    print("Done. Pipeline completed successfully.")


if __name__ == "__main__":
    main()
