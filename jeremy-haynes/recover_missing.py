#!/usr/bin/env python3
"""Second pass: fetch transcripts for videos still missing, with long backoff + yt-dlp fallback."""
import json, os, re, time, glob, subprocess, tempfile
from youtube_transcript_api import YouTubeTranscriptApi

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "raw-transcripts")
manifest = {r["id"]: r for r in json.load(open(os.path.join(BASE, "manifest.json")))}
order = sorted(manifest.values(), key=lambda r: r.get("views", 0), reverse=True)
idx = {r["id"]: i + 1 for i, r in enumerate(order)}

def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", (s or "")).strip("-").lower()
    return s[:60] or "untitled"

have = set()
for f in glob.glob(os.path.join(OUT, "*.txt")):
    m = re.search(r"__([A-Za-z0-9_-]{6,})\.txt$", f)
    if m and os.path.getsize(f) > 200:
        have.add(m.group(1))

missing = [r for r in order if r["id"] not in have][:150]  # focus top ~150 by views
print("missing (capped 150):", len(missing), flush=True)
print("cooldown 240s before starting (let 429 throttle reset)...", flush=True)
time.sleep(240)
api = YouTubeTranscriptApi()

def via_api(vid):
    for a in range(5):
        try:
            return " ".join(s.text for s in api.fetch(vid, languages=["en", "en-US", "en-GB"]))
        except Exception as e:
            if "429" in str(e) or "Too Many" in str(e) or "blocked" in str(e).lower():
                time.sleep([60, 120, 240, 300, 300][a])
            else:
                time.sleep([5, 15, 35, 70, 90][a])
    return None

def via_ytdlp(vid):
    with tempfile.TemporaryDirectory() as td:
        try:
            subprocess.run(["python3", "-m", "yt_dlp", "--skip-download", "--write-auto-sub",
                            "--write-sub", "--sub-lang", "en.*,en", "--sub-format", "vtt",
                            "-o", os.path.join(td, "%(id)s.%(ext)s"),
                            f"https://youtu.be/{vid}"], capture_output=True, timeout=120)
        except Exception:
            return None
        vtts = glob.glob(os.path.join(td, "*.vtt"))
        if not vtts:
            return None
        raw = open(vtts[0], errors="ignore").read()
        lines = []
        for ln in raw.splitlines():
            if "-->" in ln or ln.strip() == "" or ln.startswith(("WEBVTT", "Kind:", "Language:")):
                continue
            ln = re.sub(r"<[^>]+>", "", ln).strip()
            if ln and (not lines or lines[-1] != ln):
                lines.append(ln)
        return " ".join(lines) if lines else None

ok = 0
for r in missing:
    vid = r["id"]; title = r.get("title", ""); i = idx[vid]
    txt = via_api(vid) or via_ytdlp(vid)
    if not txt:
        print(f"STILL-FAIL {vid} | {title[:50]}"); continue
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt.split()) < 50:
        print(f"TOO-SHORT {vid} | {title[:50]}"); continue
    header = f"# {title}\n# video_id: {vid} | views: {r.get('views')} | duration_min: {round((r.get('duration') or 0)/60)}\n# url: https://youtu.be/{vid}\n\n"
    open(os.path.join(OUT, f"{i:03d}_{slug(title)}__{vid}.txt"), "w").write(header + txt)
    ok += 1
    print(f"RECOVERED [{ok}] {vid} | {title[:45]}", flush=True)
    time.sleep(15)

print(f"RECOVER DONE. recovered={ok} files={len(glob.glob(os.path.join(OUT,'*.txt')))}")
