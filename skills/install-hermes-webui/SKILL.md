---
name: install-hermes-webui
description: Automatically install, configure, and launch Hermes WebUI browser interface connected to Hermes Agent.
---

# Install Hermes WebUI Skill

## Description
This skill enables Hermes Agent to automatically install, build, and launch Hermes WebUI on the user's machine with zero configuration.

## Instructions
1. Run the installer script:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/m4tinbeigi-official/hermes-webui-installer/main/install.sh | bash
   ```
2. Verify the server is live by checking `http://127.0.0.1:8787/health`.
3. Provide the user with the direct link `http://127.0.0.1:8787`.
