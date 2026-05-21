<div align="center">

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

## Princip

Detekce není založená jen na hlasitosti. Program u každého krátkého bloku zvuku počítá:

- `RMS` - průměrnou energii zvuku
- `peak` - nejvyšší okamžitou špičku
- `crest factor` - poměr špičky vůči RMS, pomáhá najít ostré zvuky
- podíl vysokých frekvencí pomocí `FFT`, protože tlesknutí bývá krátké a jasné

Na začátku se krátce změří okolní šum. Audio callback pak posílá výsledky přes `queue.Queue` do hlavní smyčky, aby v callbacku neběžely pomalé operace jako vypisování nebo spouštění aplikace.

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
| Citlivější peak threshold | `python clap_launcher.py --peak-floor 0.15` |
| Přísnější filtrování šumu | `python clap_launcher.py --threshold-multiplier 9` |

## Testy

```bash
python -m unittest
```

## Omezení

- Primárně je cílený na macOS, kde se aplikace spouští přes `open -a`.
- Ostré zvuky jako bouchnutí nebo cvaknutí se mohou podobat tlesknutí.
- Jiný mikrofon nebo hlučná místnost může vyžadovat úpravu thresholdů.
- Mikrofony s automatickým potlačením šumu mohou změnit charakter tlesknutí.

## Soubory

```text
clap_launcher.py   # aplikace
test_clap_launcher.py
requirements.txt   # závislosti
README.md          # návod
```

## Když něco nejde

| Problém | Co zkusit |
| --- | --- |
| Program neslyší mikrofon | Zkontroluj povolení mikrofonu v macOS. |
| Tlesknutí se nezachytí | Tleskni blíž k mikrofonu. |
| Nevíš, který mikrofon použít | Spusť `python clap_launcher.py --list-devices`. |
