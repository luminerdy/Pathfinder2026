#!/bin/bash
# Install Pathfinder2026 systemd services for auto-start on boot

set -e

echo "=================================================="
echo "Pathfinder2026 Auto-Start Installation"
echo "=================================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo:"
    echo "  sudo bash install_services.sh"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_DIR="/etc/systemd/system"

echo "Installing services..."

# Copy boot startup service. Web control is started manually during the event.
cp "${SCRIPT_DIR}/systemd/pathfinder-startup.service" "$SERVICE_DIR/"

echo "[OK] Service file copied"

# Reload systemd
systemctl daemon-reload
echo "[OK] Systemd reloaded"

# Enable services
systemctl enable pathfinder-startup.service
echo "[OK] Startup service enabled"

# Start services now (optional)
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start pathfinder-startup.service
    echo "[OK] Startup service started"
fi

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Services installed:"
echo "  - pathfinder-startup.service - Robot initialization"
echo ""
echo "Web control is started manually when needed:"
echo "  cd /home/robot/pathfinder"
echo "  python3 web/web_control.py"
echo "  Open http://<ROBOT_IP>:8080"
echo ""
echo "On next boot, robot will:"
echo "  1. Initialize hardware"
echo "  2. Position arm forward"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status pathfinder-startup"
echo "  sudo journalctl -u pathfinder-startup -f"
echo ""
echo "To uninstall:"
echo "  sudo systemctl disable pathfinder-*.service"
echo "  sudo rm /etc/systemd/system/pathfinder-*.service"
echo "  sudo systemctl daemon-reload"
echo ""
