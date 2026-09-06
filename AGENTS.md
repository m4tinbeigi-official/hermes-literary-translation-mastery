# Hermes Agent Project Instructions

This repository is the Hermes Literary Book Translation Suite and Desktop Application.
When a user shares this repository or asks Hermes Agent to work on translation or run the app, follow these instructions.

## Capabilities
- Translates complete books, novels, and articles into master-level Persian.
- Enforces Persian orthography: zero em-dash rule, quotes for dialogues, standard half-spaces.
- Uses free Nara Router API (Gemini 3.7 / 2.5 Flash) via https://router.bynara.id/register?ref=NMAP6F9D
- Provides cross-platform desktop UI (macOS DMG / Windows EXE / Web).

## Execution Guide for Hermes Agent

1. To Translate a Book:
   If the user gives a book file or text:
   ```bash
   python3 translate_book.py <book_file> --api-key <NARA_KEY>
   ```
   If no API key is provided, ask the user or guide them to get one for free from https://router.bynara.id/register?ref=NMAP6F9D

2. To Launch Desktop App:
   - macOS: `./run_mac.command` or `python3 app.py`
   - Windows: `run_windows.bat` or `python app.py`

3. To Build Release Packages:
   - macOS DMG: `./build_dmg.sh`
   - Windows EXE: `pyinstaller --noconfirm --onefile --windowed --name "HermesBookTranslator" app.py`
