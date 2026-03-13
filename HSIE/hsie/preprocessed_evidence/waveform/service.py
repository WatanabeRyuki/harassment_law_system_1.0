from decimal import Decimal
import warnings

import librosa

from hsie.preprocessed_evidence.dto.waveform import WaveformInputDTO

try:
    import torchaudio
except Exception:
    torchaudio = None


class WaveformService:
    def decode(
        self,
        input_dto: WaveformInputDTO,
    ):
        audio_path = input_dto.audio_path

        # First, try standard librosa loading.
        try:
            waveform, sampling_rate = librosa.load(
                audio_path,
                sr=None,
                mono=True,
            )
            duration_seconds = len(waveform) / sampling_rate
            duration = Decimal(str(duration_seconds))
            waveform_values = waveform.tolist()
            return waveform_values, int(sampling_rate), duration
        except Exception as e:
            warnings.warn(
                f"WaveformService: librosa failed to load audio from {audio_path}: {e}. "
                "Falling back to torchaudio."
            )

        if torchaudio is None:
            raise RuntimeError(
                "WaveformService: librosa failed and torchaudio is not available "
                "for fallback loading."
            )

        # Fallback: use torchaudio to load and compute duration.
        try:
            waveform_tensor, sampling_rate = torchaudio.load(audio_path)
        except Exception as e:
            raise RuntimeError(
                f"WaveformService: torchaudio failed to load audio from {audio_path}: {e}"
            ) from e

        # Convert to mono if multi-channel.
        if waveform_tensor.ndim > 1 and waveform_tensor.shape[0] > 1:
            waveform_tensor = waveform_tensor.mean(dim=0, keepdim=False)

        waveform_1d = waveform_tensor.squeeze()
        num_samples = waveform_1d.shape[-1]
        duration_seconds = num_samples / float(sampling_rate)
        duration = Decimal(str(duration_seconds))
        waveform_values = waveform_1d.tolist()
        return waveform_values, int(sampling_rate), duration
