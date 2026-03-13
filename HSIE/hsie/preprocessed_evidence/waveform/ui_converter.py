class WaveformUIConverter:
    def __init__(
        self,
        max_points: int = 2000,
    ) -> None:
        self._max_points = max_points

    def convert(
        self,
        waveform_values: list[float],
        sampling_rate: int,
    ) -> list[float]:
        length: int = len(waveform_values)

        if length == 0:
            return []

        if length <= self._max_points:
            return waveform_values

        bin_size: float = length / self._max_points
        downsampled: list[float] = []

        for i in range(self._max_points):
            start: int = int(i * bin_size)
            end: int = int((i + 1) * bin_size)

            if end <= start:
                end = start + 1

            chunk = waveform_values[start:end]

            if not chunk:
                downsampled.append(0.0)
                continue

            average: float = sum(chunk) / len(chunk)
            downsampled.append(average)

        return downsampled