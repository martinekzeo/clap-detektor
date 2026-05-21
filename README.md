<div align="center">

```text
   ________  __          ___      ____ 
  / ____/ / / /   ____  /   |    / __ \
 / /   / /_/ /   / __ \/ /| |   / /_/ /
/ /___/ __  /   / /_/ / ___ |  / ____/
\____/_/ /_/   / .___/_/  |_| /_/
               /_/

      mic  ->  clap clap  ->  VS Code
```

# clap-detektor

**Dvakrát tleskni. Otevře se Visual Studio Code.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![sounddevice](https://img.shields.io/badge/audio-sounddevice-111827?style=flat-square)
![NumPy](https://img.shields.io/badge/signal-NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-open--a-000000?style=flat-square&logo=apple&logoColor=white)

</div>

## Ukázka

```bash
$ python clap_launcher.py
Listening for clap...
Debug: waiting for 2 clap(s). Detected sounds will be printed here.
Noise calibrated: rms=0.0042

Sound detected: peak=0.381, rms=0.033, high=0.18 -> clap
Clap accepted: 1/2

Sound detected: peak=0.402, rms=0.035, high=0.21 -> clap
Clap accepted: 2/2

Clap detected!
Starting VS Code...
```

## Co umí

- poslouchá mikrofon
- detekuje dvojité tlesknutí
- vypisuje debug informace o zachycených zvucích
- po detekci spustí Visual Studio Code
- umí spustit i jinou aplikaci přes `--app`

## Instalace

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Na macOS povol mikrofon pro aplikaci, ze které program spouštíš:

`System Settings -> Privacy & Security -> Microphone`

## Spuštění

```bash
python clap_launcher.py
```

## Příkazy

| Akce | Příkaz |
| --- | --- |
| Výchozí spuštění | `python clap_launcher.py` |
| Jedno tlesknutí | `python clap_launcher.py --single-clap` |
| Jiná aplikace | `python clap_launcher.py --app "Safari"` |
| Seznam mikrofonů | `python clap_launcher.py --list-devices` |
| Výběr mikrofonu | `python clap_launcher.py --device 1` |

## Soubory

```text
clap_launcher.py   # aplikace
requirements.txt   # závislosti
README.md          # návod
```

## Když něco nejde

| Problém | Co zkusit |
| --- | --- |
| Program neslyší mikrofon | Zkontroluj povolení mikrofonu v macOS. |
| Tlesknutí se nezachytí | Tleskni blíž k mikrofonu. |
| Nevíš, který mikrofon použít | Spusť `python clap_launcher.py --list-devices`. |
