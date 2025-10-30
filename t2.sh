#!/usr/bin/env bash
set -euo pipefail

# main_menu.sh
# Place this file in your project root (e.g. ~/WAVE) and run it from there.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETUP_SCRIPT="$PROJECT_ROOT/setup_modules.sh"
VENV_PY="$PROJECT_ROOT/venv/bin/python"
XSS_SCRIPT="$PROJECT_ROOT/XSS/xss1.py"

# If venv doesn't exist, run setup automatically (non-interactive)
if [[ ! -x "$VENV_PY" ]]; then
    echo "Venv python not found. Running setup to create venv and install modules..."
    bash "$SETUP_SCRIPT"
fi

# verify XSS script exists
if [[ ! -f "$XSS_SCRIPT" ]]; then
    echo "Error: XSS script not found at: $XSS_SCRIPT" >&2
    echo "Please ensure XSS/xss1.py exists."
    exit 1
fi

# optional: install basic UI tools (figlet, cowsay, lolcat) if missing
ensure_pkg() {
  if ! command -v "$1" &> /dev/null; then
    echo "Installing $1..."
    sudo apt-get update -y
    sudo apt-get install -y "$1"
  fi
}
# (commented out to avoid sudo automatically; uncomment if you want auto install)
# ensure_pkg figlet
# ensure_pkg cowsay
# ensure_pkg lolcat

# UI header (keep it minimal if those tools aren't installed)
if command -v figlet &> /dev/null && command -v lolcat &> /dev/null; then
  center() {
      local termwidth
      termwidth=$(tput cols)
      while IFS= read -r line; do
          local padding=$(( (termwidth - ${#line}) / 2 ))
          printf "%*s%s\n" "$padding" "" "$line"
      done
  }
  figlet -f big "W A V E" | center | lolcat -a --speed=100
  echo "WEB AUTOMATION vulnerability EXPLORER" | center
fi

echo "GITHUB:"
echo "LINKEDIN:"
echo ""

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

main_options=(
    "1.  CROSS-SITE SCRIPTING (XSS)"
    "2.  SQL INJECTION TESTING (SQLi)"
    "3.  NO SQL INJECTION TESTING"
    "4.  COMMAND INJECTION"
    "5.  BROKEN ACCESS CONTROL"
    "6.  SERVER-SIDE REQUEST FORGERY (SSRF)"
    "7.  SECURITY MISCONFIGURATION (PORT, VULN SCANNING)"
    "8.  SUBDOMAINS / API FINDER"
    "9.  INFORMATION GATHERING / POWERFUL DNS"
    "10. AUTOMATE ALL SCANS"
    "11. SAVED REPORTS"
    "12. CREDITS"
    "13. EXIT"
)

show_main_menu() {
    echo -e "${GREEN}Select an option:${NC}"
    for opt in "${main_options[@]}"; do
        echo -e "${YELLOW}${opt}${NC}"
    done
    echo -ne "${GREEN}Enter number (1-13): ${NC}"
    read -r main_choice
}

# --- XSS runner helper (uses venv python explicitly) ---
run_xss() {
    # ensure venv python is present
    if [[ ! -x "$VENV_PY" ]]; then
        echo -e "${RED}Virtualenv python not found at ${VENV_PY}. Run setup_modules.sh first.${NC}"
        return 1
    fi

    # show --help first using venv python
    echo -e "${GREEN}Showing help for XSS script (${VENV_PY} ${XSS_SCRIPT} --help):${NC}"
    echo "----------------------------------------"
    "$VENV_PY" "$XSS_SCRIPT" --help || {
        echo -e "${YELLOW}Warning: script returned non-zero exit when running --help (it may still work).${NC}"
    }
    echo "----------------------------------------"

    # prompt for URL
    echo -ne "${GREEN}Enter target URL (or type 'back' to return): ${NC}"
    read -r target_url
    if [[ "$target_url" =~ ^[Bb][Aa][Cc][K]$ ]]; then
        echo -e "${YELLOW}Returning to main menu...${NC}"
        return 0
    fi

    # basic URL validation
    if ! [[ "$target_url" =~ ^https?:// ]]; then
        echo -e "${YELLOW}URL doesn't start with http:// or https:// — I'll prepend http:// for you.${NC}"
        target_url="http://${target_url}"
    fi

    echo -e "${GREEN}Running XSS scan on: ${target_url}${NC}"
    "$VENV_PY" "$XSS_SCRIPT" --url "$target_url"
    local rc=$?
    if [[ $rc -ne 0 ]]; then
        echo -e "${RED}XSS script exited with status ${rc}.${NC}"
    else
        echo -e "${GREEN}XSS scan completed.${NC}"
    fi
    return $rc
}

handle_main_choice() {
    case "$main_choice" in
        1)
            while true; do
                run_xss
                echo ""
                echo -ne "${GREEN}Run another XSS test? [y/N]: ${NC}"
                read -r ans
                case "$ans" in
                    [Yy]* ) continue ;;
                    * ) break ;;
                esac
            done
            ;;
        2)
            echo -e "${GREEN}SQL INJECTION TESTING selected.${NC}"
            ;;
        3)
            echo -e "${GREEN}NO SQL INJECTION TESTING selected.${NC}"
            ;;
        4)
            echo -e "${GREEN}COMMAND INJECTION selected.${NC}"
            ;;
        5)
            echo -e "${GREEN}BROKEN ACCESS CONTROL selected.${NC}"
            ;;
        6)
            echo -e "${GREEN}SERVER-SIDE REQUEST FORGERY selected.${NC}"
            ;;
        7)
            echo -e "${GREEN}SECURITY MISCONFIGURATION selected.${NC}"
            ;;
        8)
            echo -e "${GREEN}SUBDOMAINS / API FINDER selected.${NC}"
            ;;
        9)
            echo -e "${GREEN}INFORMATION GATHERING / DNS selected.${NC}"
            ;;
        10)
            echo -e "${GREEN}AUTOMATE ALL SCANS selected.${NC}"
            ;;
        11)
            echo -e "${GREEN}SAVED REPORTS selected.${NC}"
            ;;
        12)
            echo -e "${GREEN}CREDITS selected.${NC}"
            bash "$PROJECT_ROOT/credits.sh"
            ;;
        13)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
}

# Main Execution Loop
while true; do
    show_main_menu
    handle_main_choice
    echo ""
done
