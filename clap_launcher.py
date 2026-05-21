from __future__ import annotations

import argparse
import queue
import subprocess
import sys
import time
from dataclasses import dataclass

try:
    import numpy as np
    import sounddevice as sd
except ModuleNotFoundError as exc:
    print(
        f"Chybi knihovna '{exc.name}'. Spust: python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


DEFAULT_APP = "Visual Studio Code"
CLAP_EVENT = "clap"
DEBUG_EVENT = "debug"


@dataclass(frozen=True)
class Settings:
    app: str = DEFAULT_APP
    device: int | str | None = None
    claps_required: int = 2
    sample_rate: int = 44_100
    block_size: int = 1_024
    calibration_seconds: float = 1.0
    clap_window_seconds: float = 0.75
    min_gap_seconds: float = 0.16
    peak_floor: float = 0.20
    threshold_multiplier: float = 7.0
    min_rms: float = 0.010
    min_crest_factor: float = 3.0
    min_high_frequency_ratio: float = 0.06
    sound_log_interval_seconds: float = 0.15


class ClapDetector:
    def __init__(self, settings: Settings, events: "queue.Queue[str]") -> None:
        self.settings = settings
        self.events = events
        self.noise_floor = 0.01
        self.last_clap_at = 0.0
        self.last_sound_log_at = 0.0
        self.claps: list[float] = []

    def calibrate_noise(self) -> None:
        sample_count = int(self.settings.sample_rate * self.settings.calibration_seconds)
        if sample_count <= 0:
            return

        recording = sd.rec(
            sample_count,
            samplerate=self.settings.sample_rate,
            channels=1,
            dtype="float32",
            device=self.settings.device,
        )
        sd.wait()
        samples = recording[:, 0]
        self.noise_floor = max(rms(samples), 0.001)
        self.debug(f"Noise calibrated: rms={self.noise_floor:.4f}")

    def process_audio(self, indata, frames, time_info, status) -> None:
        if status:
            self.debug(f"Audio warning: {status}")

        samples = indata[:, 0]
        detected, message = self.analyze_sound(samples)
        now = time.monotonic()

        should_log_sound = (
            message
            and now - self.last_sound_log_at >= self.settings.sound_log_interval_seconds
        )
        if should_log_sound:
            self.last_sound_log_at = now
            self.debug(message)

        if not detected:
            return

        if now - self.last_clap_at < self.settings.min_gap_seconds:
            self.debug("Clap ignored: too close to previous clap")
            return

        self.last_clap_at = now
        self.claps = [
            clap_time
            for clap_time in self.claps
            if now - clap_time <= self.settings.clap_window_seconds
        ]
        self.claps.append(now)
        self.debug(f"Clap accepted: {len(self.claps)}/{self.settings.claps_required}")

        if len(self.claps) >= self.settings.claps_required:
            self.claps.clear()
            self.events.put(CLAP_EVENT)

    def analyze_sound(self, samples: np.ndarray) -> tuple[bool, str]:
        peak = float(np.max(np.abs(samples)))
        level = rms(samples)
        threshold = max(
            self.settings.peak_floor,
            self.noise_floor * self.settings.threshold_multiplier,
        )
        sound_threshold = max(0.05, self.noise_floor * 3.0)

        if peak < sound_threshold:
            return False, ""

        prefix = f"Sound detected: peak={peak:.3f}, rms={level:.3f}"

        if peak < threshold or level < self.settings.min_rms:
            return False, f"{prefix} -> not clap (too quiet)"

        crest_factor = peak / max(level, 0.0001)
        if crest_factor < self.settings.min_crest_factor:
            return False, f"{prefix} -> not clap (not sharp enough)"

        high_ratio = high_frequency_ratio(samples, self.settings.sample_rate)
        if high_ratio < self.settings.min_high_frequency_ratio:
            return False, f"{prefix}, high={high_ratio:.2f} -> not clap (too low)"

        return True, f"{prefix}, high={high_ratio:.2f} -> clap"

    def debug(self, message: str) -> None:
        self.events.put(f"{DEBUG_EVENT}:{message}")


def rms(samples: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(samples))))


def high_frequency_ratio(samples: np.ndarray, sample_rate: int) -> float:
    centered = samples - float(np.mean(samples))
    spectrum = np.fft.rfft(centered * np.hanning(len(centered)))
    power = np.abs(spectrum) ** 2
    total_power = float(np.sum(power))
    if total_power == 0.0:
        return 0.0

    frequencies = np.fft.rfftfreq(len(centered), d=1.0 / sample_rate)
    high_power = float(np.sum(power[frequencies >= 2_000]))
    return high_power / total_power


def parse_device(value: str | None) -> int | str | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def open_app(app_name: str) -> None:
    subprocess.Popen(["open", "-a", app_name])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nasloucha mikrofonu a po tlesknuti spusti aplikaci."
    )
    parser.add_argument(
        "--app",
        default=DEFAULT_APP,
        help="Aplikace, ktera se spusti po tlesknuti.",
    )
    clap_mode = parser.add_mutually_exclusive_group()
    clap_mode.add_argument(
        "--double-clap",
        action="store_true",
        help="Vychozi chovani: spusteni az po dvojitem tlesknuti.",
    )
    clap_mode.add_argument(
        "--single-clap",
        action="store_true",
        help="Spusteni uz po jednom tlesknuti.",
    )
    parser.add_argument(
        "--device",
        help="Volitelny nazev nebo cislo mikrofonu.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Vypise dostupna audio zarizeni.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return 0

    claps_required = 2 if args.double_clap else 1 if args.single_clap else 2
    settings = Settings(
        app=args.app,
        device=parse_device(args.device),
        claps_required=claps_required,
    )
    events: "queue.Queue[str]" = queue.Queue()
    detector = ClapDetector(settings, events)

    print("Listening for clap...")
    print(
        f"Debug: waiting for {settings.claps_required} clap(s). "
        "Detected sounds will be printed here."
    )

    try:
        detector.calibrate_noise()
        with sd.InputStream(
            device=settings.device,
            channels=1,
            samplerate=settings.sample_rate,
            blocksize=settings.block_size,
            callback=detector.process_audio,
        ):
            while True:
                event = events.get()
                if event == CLAP_EVENT:
                    break
                if event.startswith(f"{DEBUG_EVENT}:"):
                    print(event.split(":", 1)[1])

        print("Clap detected!")
        if settings.app == DEFAULT_APP:
            print("Starting VS Code...")
        else:
            print(f"Starting {settings.app}...")
        open_app(settings.app)
        return 0
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
