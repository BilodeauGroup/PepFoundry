#!/bin/bash
set -e
set -o pipefail

ENV_NAME="pepfoundry"

echo "[INFO] Creating conda environment '$ENV_NAME' with Python 3.11..."
conda create -y -n $ENV_NAME python=3.11

echo "[INFO] Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME


echo "[INFO] Installing RDKit + numpy..."
conda install -y -c conda-forge rdkit numpy=1.26


echo "[INFO] Detecting CUDA availability..."

PYTORCH_INSTALL=""

# Allow manual override
if [[ -n "${CUDA_BUILD:-}" ]]; then

    echo "[INFO] Using user-defined CUDA build: $CUDA_BUILD"

    case $CUDA_BUILD in
        cu121)
            PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cu121"
            ;;
        cu118)
            PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cu118"
            ;;
        cpu)
            PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cpu"
            ;;
        *)
            echo "[ERROR] Unsupported CUDA_BUILD=$CUDA_BUILD"
            exit 1
            ;;
    esac


# Detect from nvcc
elif command -v nvcc &> /dev/null; then

    CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release //' | awk '{print $1}' | tr -d ',')

    CUDA_MAJOR=$(echo $CUDA_VERSION | cut -d. -f1)
    CUDA_MINOR=$(echo $CUDA_VERSION | cut -d. -f2)

    echo "[INFO] CUDA toolkit detected: $CUDA_VERSION"


    if (( CUDA_MAJOR == 12 && CUDA_MINOR >= 1 )); then

        echo "[INFO] Installing PyTorch CUDA 12.1"
        PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cu121"

    elif (( CUDA_MAJOR == 11 && CUDA_MINOR >= 8 )); then

        echo "[INFO] Installing PyTorch CUDA 11.8"
        PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cu118"

    else

        echo "[WARNING] CUDA version not supported"
        echo "[INFO] Installing CPU PyTorch"
        PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cpu"

    fi


else

    echo "[INFO] No CUDA toolkit detected"
    echo "[INFO] Installing CPU PyTorch"
    PYTORCH_INSTALL="--index-url https://download.pytorch.org/whl/cpu"

fi


echo "[INFO] Installing PyTorch..."

pip install torch torchvision torchaudio $PYTORCH_INSTALL


echo "[INFO] Installing Python packages..."

pip install \
    openpyxl \
    scikit-learn \
    ipykernel \
    pandas \
    openbabel-wheel


echo "[INFO] Installing PepFoundry..."
pip install git+https://github.com/BilodeauGroup/PepFoundry.git


echo "[INFO] Setup complete."
echo "[INFO] Activate environment with:"
echo "conda activate $ENV_NAME"