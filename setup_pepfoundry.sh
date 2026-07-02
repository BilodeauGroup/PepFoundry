#!/bin/bash
set -e
set -o pipefail

ENV_NAME="pepfoundry"

echo "[INFO] Creating conda environment '$ENV_NAME' with Python 3.11..."
conda create -y -n $ENV_NAME python=3.11
echo "[INFO] Environment created."

echo "[INFO] Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo "[INFO] Installing RDKit + numpy from conda-forge..."
conda install -y -c conda-forge rdkit numpy=1.26

echo "[INFO] Installing PyTorch (compatible with Python 3.11)..."
# Recommended modern CUDA build (adjust if needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

echo "[INFO] Installing Python packages..."
pip install openpyxl
pip install scikit-learn
pip install ipykernel
pip install pandas
pip install openbabel-wheel

echo "[INFO] Installing PepFoundry from GitHub..."
pip install git+https://github.com/BilodeauGroup/PepFoundry.git || {
    echo "[ERROR] PepFoundry installation failed"
    exit 1
}

echo "[INFO] Setup complete."
echo "[INFO] Activate with: conda activate $ENV_NAME"