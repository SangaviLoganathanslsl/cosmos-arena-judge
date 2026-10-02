"""Builds results/report.html (videos + Arena score + Cosmos Reason explanation) and results.zip."""
import html, json, os, shutil
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "results")
VID = os.path.join(OUT, "videos"); os.makedirs(VID, exist_ok=True)
recs = [json.loads(l) for l in open(os.path.join(OUT, "judgments.jsonl")) if l.strip()]

both = [r for r in recs if r["arena_success"] is not None and r["verdict"] in ("success", "fail")]
agree = sum((r["verdict"] == "success") == r["arena_success"] for r in both)
rate = f"{100*agree/len(both):.0f}% ({agree}/{len(both)})" if both else "n/a"
fails = Counter((r["failure_type"] or "unspecified").lower() for r in recs if r["verdict"] == "fail")

per_pol = {}
for r in recs:
    p = per_pol.setdefault(r["policy"], {"n": 0, "arena": 0, "judge": 0})
    p["n"] += 1; p["arena"] += bool(r["arena_success"]); p["judge"] += r["verdict"] == "success"

rows = []
for r in recs:
    name = f"{r['policy']}_{os.path.basename(r['video'])}"
    shutil.copy(os.path.join(ROOT, r["video"]), os.path.join(VID, name))
    a = {True: "✅ success", False: "❌ fail", None: "–"}[r["arena_success"]]
    ok = "" if r["arena_success"] is None or r["verdict"] is None else ("✔" if (r["verdict"] == "success") == r["arena_success"] else "✘")
    rows.append(f"<tr><td><video src='videos/{html.escape(name)}' controls muted width='220'></video></td>"
                f"<td>{html.escape(r['policy'])}<br>ep {r['episode']}</td><td>{a}</td>"
                f"<td><b>{html.escape(str(r['verdict']))}</b> {ok}<br><small>{html.escape(str(r['severity']))}</small></td>"
                f"<td><b>{html.escape(str(r['failure_type'] or ''))}</b><br>{html.escape(str(r['physical_reason'] or ''))}"
                f"<br><small>at {r['failure_time_sec']} s</small></td></tr>")

pol_rows = "".join(f"<tr><td>{p}</td><td>{v['n']}</td><td>{v['arena']}</td><td>{v['judge']}</td></tr>" for p, v in per_pol.items())
fail_rows = "".join(f"<li>{html.escape(k)}: {v}</li>" for k, v in fails.most_common())

page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cosmos Reason judge for Isaac Lab-Arena</title><style>
body{{font-family:system-ui,sans-serif;margin:24px;background:#0f1115;color:#e8e8e8}} h1{{color:#76b900}}
.cards{{display:flex;gap:16px;flex-wrap:wrap}} .card{{background:#1a1d24;padding:16px;border-radius:10px;min-width:220px}}
.big{{font-size:2em;color:#76b900;font-weight:700}} table{{border-collapse:collapse;width:100%;margin-top:16px}}
td,th{{border-bottom:1px solid #2a2e37;padding:8px;vertical-align:top;text-align:left}} small{{color:#9aa}}
.wrap{{overflow-x:auto}}</style></head><body>
<h1>Cosmos Reason as a neural judge for Isaac Lab-Arena</h1>
<p>Task: GR1 humanoid opens a microwave. Rollouts were recorded in Isaac Lab-Arena, and each video was judged by Cosmos Reason 2.</p>
<div class="cards"><div class="card">Agreement with Arena's scores<div class="big">{rate}</div></div>
<div class="card">Policies<div class="wrap"><table><tr><th>Policy</th><th>Episodes</th><th>Arena successes</th><th>Judge successes</th></tr>{pol_rows}</table></div></div>
<div class="card">Failure types found<ul>{fail_rows}</ul></div></div>
<div class="wrap"><table><tr><th>Rollout</th><th>Policy</th><th>Arena</th><th>Cosmos Reason</th><th>Why (physical reasoning)</th></tr>{''.join(rows)}</table></div>
</body></html>"""
open(os.path.join(OUT, "report.html"), "w").write(page)
shutil.make_archive(os.path.join(ROOT, "results"), "zip", OUT)
print(f"✅ Agreement {rate}. Report: results/report.html  |  Download: results.zip")
