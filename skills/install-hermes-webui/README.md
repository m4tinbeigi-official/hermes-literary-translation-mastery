# 🚀 Hermes WebUI — One-Click Universal Installer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows%20%7C%20WSL2-cyan.svg)]()
[![Hermes Agent](https://img.shields.io/badge/Hermes%20Agent-Autonomous-purple.svg)](https://github.com/NousResearch/hermes-agent)

Universal, zero-configuration one-click installer and AI Agent skill for [Hermes WebUI](https://github.com/nesquena/hermes-webui).

---

## ⚡ Quick Start (1-Line Install)

Run this single command in your terminal on **macOS**, **Linux**, or **WSL2**:

```bash
curl -fsSL https://raw.githubusercontent.com/m4tinbeigi-official/hermes-webui-installer/main/install.sh | bash
```

---

## 🤖 Use with Hermes Agent / AI Assistants

If you are chatting with **Hermes Agent** (or any AI assistant in terminal or web), simply send:

> *"Please install and run Hermes WebUI for me using: `https://github.com/m4tinbeigi-official/hermes-webui-installer`"*

Hermes will read `HERMES.md` / `SKILL.md` and automatically install, build, link memories, and launch the WebUI at `http://127.0.0.1:8787`.

---

## 💻 1-Click GUI Usage

### 🍎 macOS
1. Download or clone this repository.
2. Double-click **`HermesWebUI.command`** in Finder.

### 🪟 Windows
1. Download or clone this repository.
2. Double-click **`HermesWebUI.bat`** in File Explorer.

### 🐧 Linux
Run:
```bash
./install.sh
```

---

## ✨ Features
- **Auto OS & Architecture Detection** (macOS Silicon/Intel, Linux, WSL2, Windows).
- **Auto-Installs Dependencies** (`curl`, `git`, `python3.11+`).
- **Auto-Connects with Hermes Agent Core** (`~/.hermes/hermes-agent`).
- **Zero-Config Isolation** via automated `.venv`.
- **Zero Errors Guaranteed**.

---

## 📄 License
MIT License.
