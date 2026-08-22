# Hermes Agent Instruction: Auto-Install Hermes WebUI

When the user asks to install, setup, or run Hermes WebUI using this repository, follow these instructions automatically.

## 🎯 Goal
Install and launch **Hermes WebUI** (the browser interface for Hermes Agent) on the user's system without asking unnecessary questions and without errors.

## 🚀 Execution Steps

1. **Run the One-Line Installer Command**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/m4tinbeigi-official/hermes-webui-installer/main/install.sh | bash
   ```
   *Or locally:*
   ```bash
   chmod +x ./install.sh && ./install.sh
   ```

2. **What the script does automatically**:
   - Detects the OS (macOS, Linux, WSL2, Windows).
   - Installs Git, Curl, and Python 3.11+ if missing.
   - Clones `hermes-webui` to `~/hermes-webui` (or uses existing directory).
   - Connects and binds directly with your Hermes Agent core (`~/.hermes/hermes-agent`).
   - Builds `.venv`, installs dependencies (`requirements.txt`), and launches the server.
   - Probes `http://127.0.0.1:8787/health` to confirm it is running.

3. **Report to User**:
   Provide the user with their active dashboard link:
   - URL: **http://127.0.0.1:8787**
   - Confirm that Hermes Agent memories and sessions are linked.
