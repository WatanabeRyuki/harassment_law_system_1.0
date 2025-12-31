from pathlib import Path

from hsie.entrypoint.controllers.hsie_controller import HSIEController
from hsie.entrypoint.repository.evidence_repository import EvidenceRepository
from hsie.entrypoint.services.analysis_context_service import AnalysisContextService
from hsie.entrypoint.services.asr_result_structurer import ASRResultStructurer
from hsie.entrypoint.services.audio_metadata_service import AudioMetadataService
from hsie.entrypoint.services.whisper_asr_service import WhisperASRService


def main() -> None:
    # ===== サービス生成 =====
    audio_metadata_service = AudioMetadataService()
    asr_service = WhisperASRService(model_name="base")
    analysis_context_service = AnalysisContextService()
    asr_result_structurer = ASRResultStructurer()
    evidence_repository = EvidenceRepository(base_dir="data/evidence")

    # ===== Controller =====
    controller = HSIEController(
        audio_metadata_service=audio_metadata_service,
        asr_service=asr_service,
        analysis_context_service=analysis_context_service,
        asr_result_structurer=asr_result_structurer,
        evidence_repository=evidence_repository,
    )

    # ===== 入力 =====
    audio_path = Path("/Users/watanaberyuki/Desktop/HSIEフォルダ/imput_demo/会話サンプル.mp3")
    session_id = "session_001"
    speaker_id = "speaker_0"
    language = "ja"

    # ===== 実行 =====
    evidence_id = controller.run(
        audio_path=audio_path,
        session_id=session_id,
        speaker_id=speaker_id,
        language=language,
    )

    print("✅ HSIE EntryPoint completed")
    print("Evidence ID:", evidence_id)


if __name__ == "__main__":
    main()
