#!/usr/bin/env bash
# Installs Isaac Sim 5.1 + Isaac Lab 2.3 + Isaac Lab-Arena + LeRobot (per the LeRobot Arena guide)
set -e
export ACCEPT_EULA=Y PRIVACY_CONSENT=Y
mkdir -p ~/work && cd ~/work

sudo apt-get update -y && sudo apt-get install -y libglu1-mesa libxt6 git-lfs || true

if ! command -v conda >/dev/null 2>&1 && [ ! -d ~/miniconda3 ]; then
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/mc.sh
  bash /tmp/mc.sh -b -p ~/miniconda3
fi
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source "$(conda info --base)/etc/profile.d/conda.sh"

conda create -y -n lerobot-arena -c conda-forge --override-channels python=3.11
conda activate lerobot-arena
conda install -y -c conda-forge --override-channels ffmpeg=7.1.1

pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

[ -d IsaacLab ] || git clone https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab && git checkout v2.3.0 && ./isaaclab.sh -i && cd ..

[ -d IsaacLab-Arena ] || git clone https://github.com/isaac-sim/IsaacLab-Arena.git
cd IsaacLab-Arena && git checkout release/0.1.1 && pip install -e . && cd ..

[ -d lerobot ] || git clone https://github.com/huggingface/lerobot.git
cd lerobot && pip install -e ".[smolvla]" && pip install -e ".[pi]" && cd ..

pip install onnxruntime==1.23.2 lightwheel-sdk==1.0.1 "vuer[all]==0.0.70" qpsolvers==4.8.1
pip install numpy==1.26.0

echo "✅ Arena setup done. Next: bash 03_run_rollouts.sh"
