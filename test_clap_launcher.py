import queue
import unittest

import numpy as np

from clap_launcher import ClapDetector, Settings, high_frequency_ratio, rms


class SignalProcessingTests(unittest.TestCase):
    def test_rms_returns_expected_energy(self) -> None:
        samples = np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float32)
        self.assertAlmostEqual(rms(samples), 1.0)

    def test_high_frequency_ratio_is_higher_for_bright_tone(self) -> None:
        sample_rate = 44_100
        seconds = 0.05
        t = np.arange(int(sample_rate * seconds)) / sample_rate
        low_tone = np.sin(2 * np.pi * 300 * t).astype(np.float32)
        high_tone = np.sin(2 * np.pi * 3_000 * t).astype(np.float32)

        self.assertGreater(
            high_frequency_ratio(high_tone, sample_rate),
            high_frequency_ratio(low_tone, sample_rate),
        )

    def test_detector_rejects_silence(self) -> None:
        detector = ClapDetector(Settings(), queue.Queue())
        detected, message = detector.analyze_sound(np.zeros(1_024, dtype=np.float32))

        self.assertFalse(detected)
        self.assertEqual(message, "")


if __name__ == "__main__":
    unittest.main()
