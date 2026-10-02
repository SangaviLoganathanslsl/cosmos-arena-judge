# Arena × Cosmos Reason: a neural judge for robot policies

Isaac Lab-Arena records robot rollouts → Cosmos Reason 2 watches each video and explains *why* it failed → a report compares its verdicts with Arena's own success scores.

## Where each step happens

| Mark | Place |
|---|---|
| 📱 | Your phone (GitHub, Hugging Face, Claude) |
| 💻 | Org laptop browser: the Brev web console and JupyterLab file browser |
| 🖥️ T1 / T2 | Org laptop browser: **Terminal 1 / Terminal 2** inside JupyterLab on the GPU instance |

Everything that runs code happens on the GPU instance. The org laptop is only the screen you use to reach it.

---

## A. Before the clock starts (📱, do today)

1. 📱 **Hugging Face:** sign in at huggingface.co, open the page `nvidia/Cosmos-Reason2-8B`, and accept the license if asked. Then go to Settings → Access Tokens → create a **Read** token. Save it in your notes app.
2. 📱 **GitHub:** create a new **public** repo called `arena-cosmos-judge`. Use *Add file → Upload files* and upload all 7 files from this folder. (Public is fine: there are no secrets in it, and Devpost needs a repo link anyway.)
3. 📱 Note your repo URL, e.g. `https://github.com/<you>/arena-cosmos-judge`.

## B. Start the GPU (💻, minute 0)

4. 💻 Open the Brev web console → start the RTX 6000 Ada instance → open **Jupyter / Notebook**.
5. 💻 In JupyterLab: *File → New → Terminal*. Do it twice. These are **T1** and **T2**.

## C. Install, both terminals in parallel (0:00–0:35)

6. 🖥️ **T1**
   ```bash
   cd ~ && git clone https://github.com/<you>/arena-cosmos-judge.git
   cd arena-cosmos-judge && bash 01_setup_arena.sh
   ```
   Takes ~20–30 min. Leave it running.
7. 🖥️ **T2**, at the same time
   ```bash
   cd ~/arena-cosmos-judge
   export HF_TOKEN=hf_paste_your_token_here
   bash 02_setup_reason.sh
   ```
   This installs vLLM in a separate environment and downloads Cosmos Reason. It must stay separate from Arena's environment, because the two need different library versions.

## D. Record robot rollouts (0:35–1:20)

8. 🖥️ **T1** (after step 6 finishes)
   ```bash
   bash 03_run_rollouts.sh
   ```
   This runs SmolVLA, then π0.5, on the GR1 microwave task (15 episodes each by default). If time is short: `SKIP_PI=1 bash 03_run_rollouts.sh`.
9. 💻 **Check after the first few episodes:** in the JupyterLab file browser, go to `arena-cosmos-judge/outputs/eval/smolvla/` and open one `.mp4`. It should show a full attempt, not a 1-second clip. If it's too short, stop with Ctrl+C and rerun with `VIDEO_LENGTH=600 bash 03_run_rollouts.sh`.

## E. Free the GPU (1:20)

10. 🖥️ **T1**: `nvidia-smi` → there should be no Isaac or python process using memory. If one is still there: `pkill -f lerobot-eval`.

## F. Run the Cosmos Reason judge (1:25–2:15)

11. 🖥️ **T2**
    ```bash
    bash 04_serve_reason.sh
    ```
    Wait until you see `Application startup complete`, then leave it running.
    If it runs out of memory: Ctrl+C, then `REASON_MODEL=nvidia/Cosmos-Reason2-2B bash 04_serve_reason.sh`.
12. 🖥️ **T1**
    ```bash
    source ~/reason-venv/bin/activate
    python 05_judge.py
    ```
    If you switched to 2B in step 11, put `REASON_MODEL=nvidia/Cosmos-Reason2-2B` before `python`. The script is safe to rerun: it skips videos already judged.

## G. Report and save (2:15–3:00)

13. 🖥️ **T1**: `python 06_report.py` → creates `results/report.html` and `results.zip`.
14. 💻 JupyterLab file browser: right-click `results.zip` → **Download**. Unzip it on the org laptop and open `report.html` in the browser.
15. 💻 Screen-record a 2-minute walkthrough of the report on the org laptop.
16. 💻 Brev console: **stop the instance**, but only after the zip is safely on your laptop.

## If something breaks
📱 Photograph the error and send it to Claude on your phone. Arena's setup steps follow the official LeRobot × Isaac Lab-Arena guide. Version pins may need a small tweak.
