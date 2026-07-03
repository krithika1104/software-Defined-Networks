#!/bin/bash
# ============================================================
#  SDN Project - Ubuntu Setup Script
#  Run this INSIDE Ubuntu (WSL2) after WSL2 is installed
#  Usage: bash setup_sdn.sh
# ============================================================

set -e  # Exit immediately if any command fails

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  SDN Traffic Monitor - Environment Setup  ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# ---- STEP 1: Update package lists ----
echo -e "${YELLOW}[1/6] Updating Ubuntu package list...${NC}"
sudo apt-get update -y
echo -e "${GREEN}Done.${NC}"

# ---- STEP 2: Install Mininet, Open vSwitch, iperf, net-tools ----
echo ""
echo -e "${YELLOW}[2/6] Installing Mininet, Open vSwitch, iperf, net-tools...${NC}"
sudo apt-get install -y mininet openvswitch-switch iperf net-tools python3 git
echo -e "${GREEN}Done.${NC}"

# ---- STEP 3: Start Open vSwitch service ----
echo ""
echo -e "${YELLOW}[3/6] Starting Open vSwitch service...${NC}"
sudo service openvswitch-switch start
sudo service openvswitch-switch status | head -5
echo -e "${GREEN}Open vSwitch is running.${NC}"

# ---- STEP 4: Clone POX Controller ----
echo ""
echo -e "${YELLOW}[4/6] Cloning POX controller from GitHub...${NC}"
if [ -d "$HOME/pox" ]; then
    echo "POX directory already exists. Pulling latest..."
    cd "$HOME/pox" && git pull
else
    cd "$HOME" && git clone https://github.com/noxrepo/pox.git
fi
echo -e "${GREEN}POX ready at: $HOME/pox${NC}"

# ---- STEP 5: Set up project directory & copy files ----
echo ""
echo -e "${YELLOW}[5/6] Setting up SDN project directory...${NC}"
mkdir -p "$HOME/sdn_project"

# Copy project files from Windows filesystem via WSL path
# Windows path C:\Users\krith\OneDrive\Desktop\sde becomes /mnt/c/Users/krith/OneDrive/Desktop/sde
WINDOWS_PROJECT="/mnt/c/Users/krith/OneDrive/Desktop/sde"

if [ -d "$WINDOWS_PROJECT" ]; then
    echo "Found project files in Windows filesystem. Copying..."
    cp "$WINDOWS_PROJECT/topo.py"        "$HOME/sdn_project/topo.py"
    cp "$WINDOWS_PROJECT/sdn_monitor.py" "$HOME/pox/ext/sdn_monitor.py"
    echo -e "${GREEN}Files copied successfully.${NC}"
    echo "  -> topo.py        : $HOME/sdn_project/topo.py"
    echo "  -> sdn_monitor.py : $HOME/pox/ext/sdn_monitor.py"
else
    echo -e "${RED}Warning: Cannot find Windows project path at $WINDOWS_PROJECT${NC}"
    echo "Please manually copy your topo.py and sdn_monitor.py files."
fi

# ---- STEP 6: Verify Mininet ----
echo ""
echo -e "${YELLOW}[6/6] Verifying Mininet installation...${NC}"
mn --version
echo -e "${GREEN}Mininet is installed correctly.${NC}"

# ---- DONE ----
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup Complete! Here's how to run it:     ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${CYAN}Open TWO Ubuntu terminal windows and run:${NC}"
echo ""
echo -e "${YELLOW}--- Terminal 1 (POX Controller) ---${NC}"
echo "  cd ~/pox"
echo "  python3 pox.py forwarding.l2_learning sdn_monitor --interval=5"
echo ""
echo -e "${YELLOW}--- Terminal 2 (Mininet Network) ---${NC}"
echo "  cd ~/sdn_project"
echo "  sudo python3 topo.py"
echo ""
echo -e "${YELLOW}--- Inside Mininet CLI, run these tests ---${NC}"
echo "  mininet> pingall"
echo "  mininet> h1 ping -c 4 h2"
echo "  mininet> iperf h1 h3"
echo ""
