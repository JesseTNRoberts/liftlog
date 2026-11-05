#!/usr/bin/env python3
"""Pull Jesse's Strava runs into data/runs.csv (summaries only, no GPS).

Runs in GitHub Actions with three repo secrets:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
First run (empty runs.csv) pulls the whole history; later runs fetch anything
newer than the latest saved run, plus a 7-day overlap so edits get picked up.
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "runs.csv")
FIELDS = ["date", "start", "name", "type", "distance_mi", "moving_min", "elapsed_min",
          "elev_ft", "avg_hr", "max_hr", "strava_id"]
RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}

def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def access_token():
    tok = post("https://www.strava.com/oauth/token", {
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
    })
    if tok.get("refresh_token") and tok["refresh_token"] != os.environ["STRAVA_REFRESH_TOKEN"]:
        print("::warning::Strava issued a new refresh token. Update the STRAVA_REFRESH_TOKEN secret.")
    return tok["access_token"]

def to_row(a):
    start = a["start_date_local"]  # local wall-clock time, marked Z by Strava
    return {
        "date": start[:10],
        "start": start[11:16],
        "name": a.get("name", ""),
        "type": a.get("sport_type") or a.get("type"),
        "distance_mi": f'{a["distance"] / 1609.344:.2f}',
        "moving_min": f'{a["moving_time"] / 60:.1f}',
        "elapsed_min": f'{a["elapsed_time"] / 60:.1f}',
        "elev_ft": f'{a.get("total_elevation_gain", 0) * 3.28084:.0f}',
        "avg_hr": f'{a["average_heartrate"]:.0f}' if a.get("average_heartrate") else "",
        "max_hr": f'{a["max_heartrate"]:.0f}' if a.get("max_heartrate") else "",
        "strava_id": str(a["id"]),
    }

def main():
    rows = {}
    if os.path.exists(PATH):
        with open(PATH, newline="") as f:
            rows = {r["strava_id"]: r for r in csv.DictReader(f)}
    after = 0
    if rows:
        latest = max(r["date"] for r in rows.values())
        after = int((datetime.fromisoformat(latest).replace(tzinfo=timezone.utc) - timedelta(days=7)).timestamp())
    token = access_token()
    page, added, seen = 1, 0, 0
    while True:
        batch = get(f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=200&page={page}", token)
        if not batch:
            break
        for a in batch:
            if (a.get("sport_type") or a.get("type")) not in RUN_TYPES:
                continue
            seen += 1
            r = to_row(a)
            if r["strava_id"] not in rows:
                added += 1
            rows[r["strava_id"]] = r
        page += 1
        time.sleep(1)
    out = sorted(rows.values(), key=lambda r: (r["date"], r["start"]))
    with open(PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"Checked {seen} runs, added {added}, total {len(out)}.")

if __name__ == "__main__":
    sys.exit(main())
