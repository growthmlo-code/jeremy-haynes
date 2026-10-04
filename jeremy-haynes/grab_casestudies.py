#!/usr/bin/env python3
"""Persistent, patient downloader for the MISSING case-study videos (then the rest).
Loops over multiple passes with long cooldowns so it catches windows where YouTube's
IP block eases. Prioritises case studies, then fills the remaining long tail."""
import json, os, re, glob, time, subprocess, tempfile
from youtube_transcript_api import YouTubeTranscriptApi

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "raw-transcripts")
rows = sorted(json.load(open(os.path.join(BASE, "manifest.json"))), key=lambda r: r.get("views", 0), reverse=True)
idx = {r["id"]: i + 1 for i, r in enumerate(rows)}
CS = re.compile(r"(watch me|live|fix|scale this|asked me|went from|scaled from|how he|helping this|breaking down|business update|consult|breakdown|vs 1[0-9]|this \$|took this|\$[0-9].*/mo|rebuilt|bottleneck|roadmap i gave|helped .*business|businesses)", re.I)

def slug(s):
    return (re.sub(r"[^A-Za-z0-9]+", "-", s or "").strip("-").lower()[:60]) or "untitled"

def have_ids():
    h = set()
    for f in glob.glob(os.path.join(OUT, "*.txt")):
        m = re.search(r"__([A-Za-z0-9_-]{6,})\.txt$", f)
        if m and os.path.getsize(f) > 200:
            h.add(m.group(1))
    return h

api = YouTubeTranscriptApi()
log = open(os.path.join(BASE, "grab.log"), "a")
def say(*a):
    m = time.strftime("%H:%M ") + " ".join(str(x) for x in a)
    print(m, flush=True); log.write(m + "\n"); log.flush()

def fetch(vid):
    try:
        return " ".join(s.text for s in api.fetch(vid, languages=["en", "en-US", "en-GB"]))
    except Exception:
        pass
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(["python3", "-m", "yt_dlp", "--skip-download", "--write-auto-sub",
                            "--write-sub", "--sub-lang", "en.*,en", "--sub-format", "vtt",
                            "-o", os.path.join(td, "%(id)s.%(ext)s"), f"https://youtu.be/{vid}"],
                           capture_output=True, timeout=120)
        except Exception:
            return None
        v = glob.glob(os.path.join(td, "*.vtt"))
        if not v:
            return None
        out = []
        for ln in open(v[0], errors="ignore"):
            if "-->" in ln or ln.strip() == "" or ln.startswith(("WEBVTT", "Kind:", "Language:")):
                continue
            ln = re.sub(r"<[^>]+>", "", ln).strip()
            if ln and (not out or out[-1] != ln):
                out.append(ln)
        return " ".join(out) or None

PASSES = 24
for p in range(1, PASSES + 1):
    have = have_ids()
    missing = [r for r in rows if r["id"] not in have]
    cs = [r for r in missing if CS.search(r["title"] or "")]
    rest = [r for r in missing if not CS.search(r["title"] or "")]
    queue = cs + rest  # case studies first
    say(f"=== PASS {p}/{PASSES} | missing={len(missing)} (cs={len(cs)}) ===")
    if not missing:
        say("ALL DONE"); break
    got = 0
    for r in queue:
        vid = r["id"]
        txt = fetch(vid)
        if not txt or len(txt.split()) < 50:
            time.sleep(8); continue
        txt = re.sub(r"\s+", " ", txt).strip()
        i = idx[vid]
        header = f"# {r['title']}\n# video_id: {vid} | views: {r.get('views')} | duration_min: {round((r.get('duration') or 0)/60)}\n# url: https://youtu.be/{vid}\n\n"
        open(os.path.join(OUT, f"{i:03d}_{slug(r['title'])}__{vid}.txt"), "w").write(header + txt)
        got += 1
        say(f"  GOT #{i} {r['title'][:50]}")
        time.sleep(10)
    say(f"PASS {p} got {got}")
    if got == 0:
        say("pass got nothing (IP likely still blocked) — sleeping 15 min")
        time.sleep(900)
    else:
        time.sleep(120)
say("GRAB FINISHED. total files:", len(glob.glob(os.path.join(OUT, "*.txt"))))
