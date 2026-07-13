#!/bin/bash
# ADTC 2026 Target Hardware Deployment Script
# This script prepares the fresh Ubuntu 22.04 environment, installs native dependencies, and boots the Offline Advisory System.

echo "==============================================="
echo "   Deploying AgriTriage AI (ADTC Hackathon)    "
echo "==============================================="

# 1. Update and install core Linux dependencies
echo "[1/4] Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y curl build-essential libwebkit2gtk-4.0-dev \
    build-essential curl wget file libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# 2. Install Python & uv (Backend)
echo "[2/4] Setting up Python Backend..."
sudo apt-get install -y python3 python3-pip python3-venv
# Install uv natively
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install Rust (Required for Tauri sidecar compilation)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# 3. Install Node.js & pnpm (Frontend)
echo "[3/4] Setting up Node & pnpm..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pnpm

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd advisory-system/app && pnpm install && cd ../..

echo "[4/4] Environment Ready! You can now boot the backend and frontend!"
echo "To start backend: cd advisory-system/api && uv run server.py"
echo "To start frontend: cd advisory-system/app && pnpm tauri dev"
