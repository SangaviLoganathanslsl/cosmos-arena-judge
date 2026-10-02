#!/usr/bin/env bash
# Records GR1-microwave rollouts for SmolVLA and pi0.5 with video, headless
set -e
cd "$(dirname "$0")"
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate lerobot-arena
export ACCEPT_EULA=Y PRIVACY_CONSENT=Y

N="${N_EPISODES:-15}"
VLEN="${VIDEO_LENGTH:-300}"

COMMON=(
  --env.type=isaaclab_arena
  --env.hub_path=nvidia/isaaclab-arena-envs
  '--rename_map={"observation.images.robot_pov_cam_rgb": "observation.images.robot_pov_cam"}'
  --policy.device=cuda
  --env.environment=gr1_microwave
  --env.embodiment=gr1_pink
  --env.object=mustard_bottle
  --env.headless=true
  --env.enable_cameras=true
  --env.video=true
  --env.video_length="$VLEN"
  --env.video_interval="$VLEN"
  --env.state_keys=robot_joint_pos
  --env.camera_keys=robot_pov_cam_rgb
  --trust_remote_code=True
  --eval.batch_size=1
  --eval.n_episodes="$N"
)

echo "▶ SmolVLA ($N episodes)"
lerobot-eval --policy.path=nvidia/smolvla-arena-gr1-microwave \
  --output_dir=outputs/eval/smolvla "${COMMON[@]}"

if [ "${SKIP_PI:-0}" != "1" ]; then
  echo "▶ pi0.5 ($N episodes)"
  TORCH_COMPILE_DISABLE=1 TORCHINDUCTOR_DISABLE=1 lerobot-eval \
    --policy.path=nvidia/pi05-arena-gr1-microwave \
    --output_dir=outputs/eval/pi05 "${COMMON[@]}"
fi
echo "✅ Rollouts done. Next: free the GPU, then bash 04_serve_reason.sh in T2"
