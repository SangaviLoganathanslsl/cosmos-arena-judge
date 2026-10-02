#!/usr/bin/env bash
# Serves Cosmos Reason 2 on localhost:8000 (OpenAI-compatible API)
source ~/reason-venv/bin/activate
MODEL="${REASON_MODEL:-nvidia/Cosmos-Reason2-8B}"
vllm serve "$MODEL" \
  --port 8000 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.85 \
  --media-io-kwargs '{"video": {"num_frames": -1}}'
