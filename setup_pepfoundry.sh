#!/bin/bash
set -e
set -o pipefail

ENV_NAME="pepfoundry"

echo "[INFO] Creating conda environment '$ENV_NAME' with Python 3.11..."
conda create -y -n $ENV_NAME python=3.11

echo "[INFO] Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo "[INFO] Installing RDKit + numpy from conda-forge..."
conda install -y -c conda-forge rdkit numpy=1.26

echo "[INFO] Installing PyTorch..."

if command -v nvidia-smi &> /dev/null; then
    echo "[INFO] NVIDIA GPU detected. Installing CUDA version..."
    pip install torch --index-url https://download.pytorch.org/whl/cu117
else
    echo "[INFO] No NVIDIA GPU detected. Installing CPU version..."
    pip install torch --index-url https://download.pytorch.org/whl/cpu
fi

echo "[INFO] Installing Python packages..."
pip install openpyxl
pip install scikit-learn
pip install ipykernel
pip install pandas
pip install openbabel-wheel

echo "[INFO] Installing PepFoundry from GitHub..."
pip install git+https://github.com/BilodeauGroup/PepFoundry.git

echo "[INFO] Setup complete."
echo "[INFO] Activate with: conda activate $ENV_NAME"