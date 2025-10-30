# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
center() {
    local termwidth
    termwidth=$(tput cols)
    while IFS= read -r line; do
        local padding=$(( (termwidth - ${#line}) / 2 ))
        printf "%*s%s\n" "$padding" "" "$line"
    done }
echo -e  "${GREEN}GITHUB:${NC}" | center
echo -e  "${RED}LINKEDIN:https://www.linkedin.com/in/sharan-kumar-vr-4a287a376?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app${NC}" | center
cowsay -f stegosaurus  "THIS IS PURELY MADE BY SHARANKUMAR VR (VITIAN)" | center | lolcat -s 50
