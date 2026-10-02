"""Sends every rollout video to Cosmos Reason 2 and saves a verdict + physical explanation."""
import base64, glob, json, os, re, time
from openai import OpenAI

ROOT = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.join(ROOT, "outputs", "eval")
OUT = os.path.join(ROOT, "results"); os.makedirs(OUT, exist_ok=True)
JUDG = os.path.join(OUT, "judgments.jsonl")
MODEL = os.environ.get("REASON_MODEL", "nvidia/Cosmos-Reason2-8B")
TASK = os.environ.get("TASK_TEXT", "The humanoid robot must open the microwave door.")
client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")

PROMPT = f"""You are a robot safety and quality inspector reviewing a simulation recording.
Task: {TASK}
Watch the whole clip. Decide whether the robot completed the task. If not, identify when and why it failed physically
(e.g. missed the handle, grasp slipped, collision, released too early, wrong target, stalled, unstable motion).
Answer the question using the following format:
<think>
your reasoning
</think>
<answer>
one JSON object with keys: "verdict" ("success" or "fail"), "failure_time_sec" (number or null),
"failure_type" (2-4 words or null), "physical_reason" (one sentence), "severity" ("none", "low", "medium" or "high")
</answer>"""

def ground_truth(policy_dir):
    gt = {}
    def walk(o):
        if isinstance(o, dict):
            if "episode_ix" in o and "success" in o:
                gt[int(o["episode_ix"])] = bool(o["success"])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    for p in glob.glob(os.path.join(policy_dir, "**", "eval_info.json"), recursive=True):
        walk(json.load(open(p)))
    return gt

def ask(video):
    b64 = base64.b64encode(open(video, "rb").read()).decode()
    msgs = [{"role": "user", "content": [
        {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{b64}"}},
        {"type": "text", "text": PROMPT}]}]
    kw = dict(model=MODEL, messages=msgs, max_tokens=1500, temperature=0.2)
    try:
        r = client.chat.completions.create(**kw, extra_body={"mm_processor_kwargs": {"fps": 4}})
    except Exception as e:
        print("   retrying without fps setting:", str(e)[:120])
        r = client.chat.completions.create(**kw)
    return r.choices[0].message.content or ""

def parse(text):
    m = re.search(r"<answer>(.*?)</answer>", text, re.S)
    body = m.group(1) if m else text
    j = re.search(r"\{.*\}", body, re.S)
    try:
        return json.loads(j.group(0)) if j else None
    except Exception:
        return None

def wait_for_server():
    for _ in range(60):
        try:
            client.models.list(); return
        except Exception:
            print("waiting for Cosmos Reason server on :8000 ..."); time.sleep(10)
    raise SystemExit("Server not reachable. Is 04_serve_reason.sh running in T2?")

def main():
    wait_for_server()
    done = set()
    if os.path.exists(JUDG):
        done = {json.loads(l)["video"] for l in open(JUDG) if l.strip()}
    policies = sorted(d for d in os.listdir(EVAL_DIR) if os.path.isdir(os.path.join(EVAL_DIR, d)))
    for pol in policies:
        pdir = os.path.join(EVAL_DIR, pol)
        gt = ground_truth(pdir)
        videos = sorted(glob.glob(os.path.join(pdir, "**", "*.mp4"), recursive=True))
        print(f"\n{pol}: {len(videos)} videos, {len(gt)} ground-truth episodes")
        for v in videos:
            rel = os.path.relpath(v, ROOT)
            if rel in done: continue
            m = re.search(r"episode_(\d+)", os.path.basename(v))
            ep = int(m.group(1)) if m else None
            t0 = time.time(); raw = ask(v); ans = parse(raw) or {}
            rec = {"policy": pol, "video": rel, "episode": ep,
                   "arena_success": gt.get(ep) if ep is not None else None,
                   **{k: ans.get(k) for k in ["verdict", "failure_time_sec", "failure_type", "physical_reason", "severity"]},
                   "raw": raw}
            with open(JUDG, "a") as f: f.write(json.dumps(rec) + "\n")
            print(f"  ep {ep}: arena={rec['arena_success']} judge={rec['verdict']} "
                  f"({rec['failure_type']}) [{time.time()-t0:.0f}s]")
    print(f"\n✅ Saved to {JUDG}. Next: python 06_report.py")

if __name__ == "__main__":
    main()
