# ============================================================
#  WSL2 + Ubuntu + SDN Project - Full Setup Script
#  Run this script in an ELEVATED (Administrator) PowerShell window
#  Right-click PowerShell -> "Run as Administrator" -> paste commands
# ============================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STEP 1: Enabling WSL2 Windows Features   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Enable the Windows Subsystem for Linux feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable the Virtual Machine Platform feature (required for WSL2)
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STEP 2: Setting WSL2 as default version  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Set WSL default version to 2
wsl --set-default-version 2

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  STEP 3: Installing Ubuntu 22.04 LTS      " -ForegroundColor Cyan
Write-Host "  (This will take 5-10 minutes)             " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Install Ubuntu 22.04 LTS without requiring user interaction
wsl --install -d Ubuntu-22.04

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  DONE! Ubuntu 22.04 installed in WSL2      " -ForegroundColor Green
Write-Host "  A RESTART may be required.                " -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "After restart, open 'Ubuntu 22.04' from Start Menu" -ForegroundColor White
Write-Host "Create a username and password when prompted."       -ForegroundColor White
Write-Host "Then run the SDN setup script (setup_sdn.sh)."       -ForegroundColor White
