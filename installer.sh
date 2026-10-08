#!/bin/bash
# WiFi Automation Toolkit - Complete Installer

echo "=========================================="
echo "WiFi Security Automation Toolkit Installer"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./installer.sh)"
    exit 1
fi

echo "[*] Updating package lists..."
#apt update

echo "[*] Installing Aircrack-ng suite..."
#apt install -y aircrack-ng iw wireless-tools

echo "[*] Installing Python and dependencies..."
apt install -y python3 python3-pip python3-pyqt5

echo "[*] Installing Python packages..."
pip3 install PyQt5

echo "[*] Installing common wordlists..."
#apt install -y wordlists
echo "[*] Wordlists installed to /usr/share/wordlists/"

echo "[*] Creating desktop entry..."
cat > /usr/share/applications/wifi-toolkit.desktop << EOF
[Desktop Entry]
Name=WiFi Security Toolkit
Comment=Automated WiFi Security Testing
Exec=sudo python3 $(pwd)/main.py
Icon=network-wireless
Terminal=false
Type=Application
Categories=Network;Security;
EOF

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo ""
echo "To run:"
echo "  python3 main.py"
echo ""
echo "Or from the Applications menu: 'WiFi Security Toolkit'"
echo "=========================================="