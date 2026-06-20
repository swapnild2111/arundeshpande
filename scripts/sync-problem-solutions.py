#!/usr/bin/env python3
"""
Regenerate data/problem-solutions.yaml from YouTube uploads.

Sources (first match wins):
  1. YouTube Data API v3 — set YOUTUBE_API_KEY (recommended for CI)
  2. base44 Video API — fallback when no API key (local dev)

Titles must contain "Problem N" or "Solution N" (case-insensitive).
Missing partners are written as null (site shows Coming Soon).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CHANNEL_ID = "UC5Wiove6pc54zODl8JgUuyg"
BASE44_VIDEO_URL = "https://arun-deshpande-carrom-coach.base44.app/api/entities/Video"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "problem-solutions.yaml"


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "arundeshpande-sync/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def parse_title(title: str) -> tuple[str, int] | None:
    tl = title.lower()
    m = re.search(r"(\d+)", title)
    if not m:
        return None
    num = int(m.group(1))
    if "problem" in tl:
        return ("problem", num)
    if "solution" in tl:
        return ("solution", num)
    return None


def fetch_from_youtube(api_key: str) -> list[dict[str, str]]:
    params = urllib.parse.urlencode(
        {"part": "contentDetails", "id": CHANNEL_ID, "key": api_key}
    )
    channel = fetch_json(f"https://www.googleapis.com/youtube/v3/channels?{params}")
    items = channel.get("items") or []
    if not items:
        raise RuntimeError(f"YouTube channel not found: {CHANNEL_ID}")

    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos: list[dict[str, str]] = []
    page_token = ""

    while True:
        q = urllib.parse.urlencode(
            {
                "part": "snippet",
                "playlistId": uploads,
                "maxResults": 50,
                "key": api_key,
                **({"pageToken": page_token} if page_token else {}),
            }
        )
        data = fetch_json(f"https://www.googleapis.com/youtube/v3/playlistItems?{q}")
        for item in data.get("items") or []:
            snippet = item.get("snippet") or {}
            title = snippet.get("title") or ""
            vid = (snippet.get("resourceId") or {}).get("videoId")
            if title and vid:
                videos.append({"title": title, "youtube_id": vid})
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return videos


def fetch_from_base44() -> list[dict[str, str]]:
    data = fetch_json(BASE44_VIDEO_URL)
    if not isinstance(data, list):
        raise RuntimeError("Unexpected base44 API response")
    return [
        {"title": v["title"], "youtube_id": v["youtube_id"]}
        for v in data
        if v.get("category") == "problem_solution" and v.get("title") and v.get("youtube_id")
    ]


def build_pairs(videos: list[dict[str, str]]) -> list[dict]:
    problems: dict[int, str] = {}
    solutions: dict[int, str] = {}

    for v in videos:
        parsed = parse_title(v["title"])
        if not parsed:
            continue
        kind, num = parsed
        vid = v["youtube_id"]
        if kind == "problem":
            problems[num] = vid
        else:
            solutions[num] = vid

    nums = sorted(set(problems) | set(solutions))
    return [
        {
            "num": n,
            "problem": problems.get(n),
            "solution": solutions.get(n),
        }
        for n in nums
    ]


def render_yaml(pairs: list[dict]) -> str:
    lines = ["pairs:"]
    for p in pairs:
        lines.append(f"  - num: {p['num']}")
        prob = p["problem"]
        sol = p["solution"]
        lines.append(f"    problem: {prob}" if prob else "    problem: null")
        lines.append(f"    solution: {sol}" if sol else "    solution: null")
    return "\n".join(lines) + "\n"


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()

    if api_key:
        print("Fetching from YouTube Data API…")
        videos = fetch_from_youtube(api_key)
        source = "YouTube Data API"
    else:
        print("YOUTUBE_API_KEY not set — using base44 Video API fallback…")
        videos = fetch_from_base44()
        source = "base44 API"

    pairs = build_pairs(videos)
    if not pairs:
        print("No problem/solution pairs found.", file=sys.stderr)
        return 1

    complete = sum(1 for p in pairs if p["problem"] and p["solution"])
    missing_p = [p["num"] for p in pairs if p["solution"] and not p["problem"]]
    missing_s = [p["num"] for p in pairs if p["problem"] and not p["solution"]]

    print(f"Source: {source}")
    print(f"Pairs: {len(pairs)} ({complete} complete)")
    if missing_p:
        print(f"  Missing problem: {missing_p}")
    if missing_s:
        print(f"  Missing solution: {missing_s}")

    new_content = render_yaml(pairs)
    old_content = OUTPUT.read_text() if OUTPUT.exists() else ""

    if new_content == old_content:
        print("No changes.")
        return 0

    print(f"Writing {OUTPUT}")
    if dry_run:
        print("(dry-run — file not written)")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(new_content)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
