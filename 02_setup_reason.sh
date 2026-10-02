#!/usr/bin/env bash
# Separate Python env for vLLM + Cosmos Reason 2 (kept apart from Arena's pinned libraries)
set -e
: "${HF_TOKEN:?Run first: export HF_TOKEN=hf_your_token}"
MODEL="${REASON_MODEL:-nvidia/Cosmos-Reason2-8B}"

python3 -m venv ~/reason-venv || (sudo apt-get install -y python3-venv && python3 -m venv ~/reason-venv)
source ~/reason-venv/bin/activate
pip install -U pip
pip install "vllm>=0.11.0" openai huggingface_hub

python -c "from huggingface_hub import snapshot_download; snapshot_download('$MODEL')"
echo "✅ Cosmos Reason ready: $MODEL"
