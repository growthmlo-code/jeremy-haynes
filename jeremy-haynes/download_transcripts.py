#!/usr/bin/env python3
"""Download transcripts for all Jeremy Haynes videos listed in manifest.json."""
import json, os, re, time, sys
from youtube_transcript_api import YouTubeTranscriptApi

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "raw-transcripts")
os.makedirs(OUT, exist_ok=True)
manifest = json.load(open(os.path.join(BASE, "manifest.json")))
# richest first
manifest.sort(key=lambda r: r.get("views", 0), reverse=True)

def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "-", (s or "")).strip("-").lower()
    return s[:60] or "untitled"

api = YouTubeTranscriptApi()
ok, fail, skip = 0, 0, 0
log = open(os.path.join(BASE, "download.log"), "w")
def say(*a):
    m = " ".join(str(x) for x in a)
    print(m); log.write(m + "\n"); log.flush()

for i, r in enumerate(manifest, 1):
    vid = r["id"]; title = r.get("title", "")
    fname = f"{i:03d}_{slug(title)}__{vid}.txt"
    fpath = os.path.join(OUT, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 200:
        skip += 1; continue
    segs = None
    for attempt in range(3):
        try:
            try:
                segs = [s.text for s in api.fetch(vid, languages=["en", "en-US", "en-GB"])]
            except Exception:
                segs = [s["text"] for s in YouTubeTranscriptApi.get_transcript(vid, languages=["en", "en-US", "en-GB"])]
            break
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
            if attempt == 2:
                say(f"[{i}/260] FAIL {vid} | {title[:50]} | {err}")
            else:
                time.sleep(2 + attempt * 2)
    if not segs:
        fail += 1; continue
    txt = " ".join(segs)
    txt = re.sub(r"\s+", " ", txt).strip()
    header = f"# {title}\n# video_id: {vid} | views: {r.get('views')} | duration_min: {round((r.get('duration') or 0)/60)}\n# url: https://youtu.be/{vid}\n\n"
    open(fpath, "w").write(header + txt)
    ok += 1
    if ok % 10 == 0:
        say(f"[{i}/260] ok={ok} fail={fail} skip={skip} ... last: {title[:40]}")
    time.sleep(0.6)

say(f"DONE. ok={ok} fail={fail} skip={skip} total_files={len(os.listdir(OUT))}")
