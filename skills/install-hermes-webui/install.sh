#!/usr/bin/env bash
# ==============================================================================
#  _    _                                _          _     _   _ _____ 
# | |  | |                              | |        | |   | | | |_   _|
# | |__| | ___ _ __ _ __ ___   ___  ___ | |  _  _  | |   | | | | | |  
# |  __  |/ _ \ '__| '_ ` _ \ / _ \/ __|| | | || | | |   | | | | | |  
# | |  | |  __/ |  | | | | | |  __/\__ \| | | || | | |___| |_| |_| |_ 
# |_|  |_|\___|_|  |_| |_| |_|\___||___/|_|  \_,_/ |______\___/|_____|
#
#       ✨ Hermes WebUI Standalone Universal Installer & Launcher ✨
# ==============================================================================

set -eo pipefail

BOLD='\033[1m'
C_RESET='\033[0m'
C_CYAN='\033[38;5;51m'
C_SKY='\033[38;5;45m'
C_BLUE='\033[38;5;39m'
C_PURPLE='\033[38;5;141m'
C_GREEN='\033[38;5;48m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_GRAY='\033[38;5;244m'
C_WHITE='\033[38;5;255m'

INSTALL_DIR="${HERMES_WEBUI_DIR:-$HOME/hermes-webui}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

# Temporary file cleanup trap
TMP_FILES=()
cleanup_on_exit() {
    for f in "${TMP_FILES[@]:-}"; do
        [ -f "$f" ] && rm -f "$f" 2>/dev/null || true
    done
}
trap cleanup_on_exit EXIT

TOTAL_STEPS=5
CURRENT_STEP=0

print_banner() {
    [ -t 1 ] && clear 2>/dev/null || true
    echo -e "${C_CYAN}"
    cat << "EOF"
    __  __                                  _       __     __    __  ______
   / / / /___   _____ ____ ___   ___   _____| |     / /___ / /_  / / / /  _/
  / /_/ / _ \ / ___// __ `__ \ / _ \ / ___/| | /| / // _ \ / __ \/ / / // /  
 / __  /  __// /   / / / / / //  __/(__  ) | |/ |/ //  __/ /_/ / /_/ // /   
/_/ /_/\___//_/   /_/ /_/ /_/ \___//____/  |__/|__/ \___/_.___/\____/___/   
EOF
    echo -e "${C_PURPLE}${BOLD}   ──────────  Next-Gen Autonomous Agent Web Interface  ──────────${C_RESET}"
    echo -e "${C_GRAY}               One-Click Universal Standalone Installer            ${C_RESET}"
    echo ""
}

step_header() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo ""
    echo -e "${C_BLUE}${BOLD}┌──[ ${C_CYAN}Step ${CURRENT_STEP}/${TOTAL_STEPS}${C_BLUE} ]───────────────────────────────────────────────────────┐${C_RESET}"
    echo -e "${C_BLUE}${BOLD}│ ${C_WHITE}⚡ $1${C_RESET}"
    echo -e "${C_BLUE}${BOLD}└──────────────────────────────────────────────────────────────────┘${C_RESET}"
}

sub_info() {
    echo -e "  ${C_SKY}➜${C_RESET} ${C_WHITE}$1${C_RESET}"
}

sub_success() {
    echo -e "  ${C_GREEN}${BOLD}✔${C_RESET} ${C_GREEN}$1${C_RESET}"
}

sub_warn() {
    echo -e "  ${C_YELLOW}${BOLD}▲${C_RESET} ${C_YELLOW}$1${C_RESET}"
}

sub_error() {
    echo -e "  ${C_RED}${BOLD}✖${C_RESET} ${C_RED}$1${C_RESET}"
}

run_with_status() {
    local msg=$1
    shift
    local log_file
    log_file="$(mktemp "${TMPDIR:-/tmp}/hermes_install_log.XXXXXX")"
    TMP_FILES+=("$log_file")
    local status=0

    if [ -t 1 ]; then
        local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        local i=0
        "$@" >"$log_file" 2>&1 &
        local pid=$!
        while kill -0 "$pid" 2>/dev/null; do
            i=$(( (i+1) % 10 ))
            printf "\r  \033[38;5;51m%s\033[0m \033[38;5;244m%s...\033[0m" "${spin:$i:1}" "$msg"
            sleep 0.08
        done
        wait "$pid" || status=$?
        printf "\r\033[K"
    else
        echo -e "  ${C_SKY}➜${C_RESET} ${C_GRAY}${msg}...${C_RESET}"
        "$@" >"$log_file" 2>&1 || status=$?
    fi

    if [ $status -ne 0 ]; then
        if [ -s "$log_file" ]; then
            echo -e "  ${C_RED}${BOLD}✖ Step failed:${C_RESET} ${C_WHITE}$msg${C_RESET}"
            sed 's/^/    /' "$log_file" | tail -n 20 >&2
        fi
        rm -f "$log_file"
        return $status
    fi
    rm -f "$log_file"
    return 0
}

print_banner

# Step 1: OS Detection
step_header "Detecting Operating System & Architecture"
OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"
case "$OS_NAME" in
    Darwin*) OS_DISPLAY="macOS (Apple Silicon / Intel)" ;;
    Linux*)
        if grep -qi microsoft /proc/version 2>/dev/null; then
            OS_DISPLAY="Windows Subsystem for Linux (WSL2)"
        elif [ -f /etc/os-release ]; then
            OS_DISPLAY="$(grep -E '^PRETTY_NAME=' /etc/os-release | cut -d= -f2 | tr -d '"')"
        else
            OS_DISPLAY="Linux Generic"
        fi
        ;;
    *) OS_DISPLAY="$OS_NAME ($ARCH_NAME)" ;;
esac
sub_info "Platform: ${C_WHITE}${BOLD}${OS_DISPLAY}${C_RESET} [${ARCH_NAME}]"
sub_success "System architecture verified"

# Step 2: System Tools (git, curl)
step_header "Checking System Utilities (Git & Curl)"
install_tool() {
    local tool=$1
    sub_warn "Installing missing tool: ${tool}..."
    if command -v brew >/dev/null 2>&1; then
        run_with_status "Installing $tool via Homebrew" brew install "$tool"
    elif command -v apt-get >/dev/null 2>&1; then
        run_with_status "Installing $tool via APT" sudo apt-get install -y "$tool"
    elif command -v dnf >/dev/null 2>&1; then
        run_with_status "Installing $tool via DNF" sudo dnf install -y "$tool"
    elif command -v pacman >/dev/null 2>&1; then
        run_with_status "Installing $tool via Pacman" sudo pacman -S --noconfirm "$tool"
    fi
}

command -v curl >/dev/null 2>&1 || install_tool "curl"
command -v git >/dev/null 2>&1 || install_tool "git"
sub_success "Git and Curl are ready"

# Step 3: Python 3.11+ Runtime
step_header "Checking Python 3.11+ Runtime"
PYTHON_BIN=""

check_py() {
    local candidate=$1
    if command -v "$candidate" >/dev/null 2>&1; then
        local major minor
        major="$("$candidate" -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo 0)"
        minor="$("$candidate" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo 0)"
        if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; then
            echo "$candidate"
            return 0
        fi
    fi
    return 1
}

for c in python3.13 python3.12 python3.11 python3 python; do
    if found="$(check_py "$c")"; then
        PYTHON_BIN="$found"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    sub_warn "Python 3.11+ not found. Installing..."
    if command -v brew >/dev/null 2>&1; then
        run_with_status "Installing Python 3.12 via Homebrew" brew install python@3.12
        PYTHON_BIN="$(brew --prefix python@3.12)/bin/python3.12"
    elif command -v apt-get >/dev/null 2>&1; then
        run_with_status "Installing Python 3 via APT" sudo apt-get install -y python3 python3-pip python3-venv
        PYTHON_BIN="python3"
    elif command -v dnf >/dev/null 2>&1; then
        run_with_status "Installing Python 3 via DNF" sudo dnf install -y python3 python3-pip
        PYTHON_BIN="python3"
    elif command -v pacman >/dev/null 2>&1; then
        run_with_status "Installing Python via Pacman" sudo pacman -S --noconfirm python python-pip
        PYTHON_BIN="python"
    else
        sub_error "Please install Python 3.11+ manually."
        exit 1
    fi
fi
PY_VER="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
sub_success "Python Active: v${PY_VER} (${PYTHON_BIN})"

# Step 4: Clone / Update Hermes WebUI & Hermes Agent Core
step_header "Cloning & Connecting Hermes WebUI + Agent"

if [ ! -d "$INSTALL_DIR/.git" ]; then
    sub_info "Cloning Hermes WebUI into ${INSTALL_DIR}..."
    run_with_status "Cloning repo" git clone https://github.com/nesquena/hermes-webui.git "$INSTALL_DIR"
else
    sub_info "Updating Hermes WebUI in ${INSTALL_DIR}..."
    (cd "$INSTALL_DIR" && git pull --quiet 2>/dev/null || true)
fi

mkdir -p "$HERMES_HOME" 2>/dev/null || true

find_agent_dir() {
    local candidates=(
        "${HERMES_WEBUI_AGENT_DIR:-}"
        "$HERMES_HOME/hermes-agent"
        "$INSTALL_DIR/../hermes-agent"
        "$HOME/.hermes/hermes-agent"
        "$HOME/hermes-agent"
        "/usr/local/lib/hermes-agent"
    )
    for c in "${candidates[@]}"; do
        if [ -n "$c" ] && [ -f "$c/run_agent.py" ]; then
            echo "$c"
            return 0
        fi
    done
    return 1
}

AGENT_DIR="$(find_agent_dir || echo "")"

if [ -n "$AGENT_DIR" ] && [ -f "$AGENT_DIR/run_agent.py" ]; then
    sub_success "Hermes Agent Linked: ${AGENT_DIR}"
    AGENT_STATUS_STR="${C_GREEN}Active & Linked${C_RESET}"
else
    sub_info "Hermes Agent runtime discovery will be managed by bootstrap engine"
    AGENT_STATUS_STR="${C_SKY}Runtime Discovery${C_RESET}"
fi

# Step 5: Setup Virtual Environment & Run
step_header "Building Virtual Environment & Starting WebUI"

cd "$INSTALL_DIR"
VENV_DIR="$INSTALL_DIR/.venv"

if [ ! -f "$VENV_DIR/bin/python" ] && [ ! -f "$VENV_DIR/Scripts/python.exe" ]; then
    rm -rf "$VENV_DIR" 2>/dev/null || true
    "$PYTHON_BIN" -m venv "$VENV_DIR" 2>/dev/null || "$PYTHON_BIN" -m venv --symlinks "$VENV_DIR" 2>/dev/null || true
fi

if [ -f "$VENV_DIR/bin/python" ]; then
    VENV_PYTHON="$VENV_DIR/bin/python"
else
    VENV_PYTHON="$PYTHON_BIN"
fi

run_with_status "Upgrading pip & build tools" env -u PYTHONPATH "$VENV_PYTHON" -m pip install --quiet --upgrade pip setuptools wheel
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    run_with_status "Installing requirements" env -u PYTHONPATH "$VENV_PYTHON" -m pip install --quiet -r "$INSTALL_DIR/requirements.txt"
fi
run_with_status "Installing optional companion parsers" env -u PYTHONPATH "$VENV_PYTHON" -m pip install --quiet psutil edge-tts python-docx openpyxl python-pptx || true

echo ""
echo -e "${C_GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_GREEN}${BOLD}║   ✨  Hermes WebUI Installation Finished Successfully!  ✨      ║${C_RESET}"
echo -e "${C_GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════╝${C_RESET}"
echo ""
echo -e "  ${C_SKY}${BOLD}● Web Interface :${C_RESET} ${C_WHITE}http://127.0.0.1:8787${C_RESET}"
echo -e "  ${C_SKY}${BOLD}● Agent Status  :${C_RESET} $AGENT_STATUS_STR"
echo -e "  ${C_SKY}${BOLD}● Location      :${C_RESET} ${C_GRAY}$INSTALL_DIR${C_RESET}"
echo ""
echo -e "${C_PURPLE}${BOLD}Starting server...${C_RESET}"
echo ""

exec "$VENV_PYTHON" "$INSTALL_DIR/bootstrap.py" "$@"
