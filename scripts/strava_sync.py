#!/usr/bin/env python3
"""Pull Jesse's Strava runs into data/runs.csv (summaries only, no GPS).

Calories aren't in Strava's activity list, only in each activity's detail, so
each sync also fetches details for up to DETAIL_BUDGET runs still missing them
(newest first). Strava allows 100 reads per 15 minutes, so a big backfill
finishes over a few syncs. calories "" = not fetched yet, "0" = Strava had none.

Runs in GitHub Actions with three repo secrets:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
First run (empty runs.csv) pulls the whole history; later runs fetch anything
newer than the latest saved run, plus a 7-day overlap so edits get picked up.
"""
import csv, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "runs.csv")
FIELDS = ["date", "start", "name", "type", "distance_mi", "moving_min", "elapsed_min",
          "elev_ft", "avg_hr", "max_hr", "calories", "strava_id"]
DETAIL_BUDGET = 90
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
        "calories": "",
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
    page, added, seen, reads = 1, 0, 0, 1
    while True:
        batch = get(f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=200&page={page}", token)
        reads += 1
        if not batch:
            break
        for a in batch:
            if (a.get("sport_type") or a.get("type")) not in RUN_TYPES:
                continue
            seen += 1
            r = to_row(a)
            old = rows.get(r["strava_id"])
            if old is None:
                added += 1
            elif old.get("distance_mi") == r["distance_mi"] and old.get("moving_min") == r["moving_min"]:
                r["calories"] = old.get("calories", "")  # unchanged run: keep fetched calories
            rows[r["strava_id"]] = r
        page += 1
        time.sleep(1)
    # Fill in calories from activity details, newest runs first, within the rate limit.
    todo = sorted((r for r in rows.values() if not r.get("calories")), key=lambda r: (r["date"], r["start"]), reverse=True)
    filled = 0
    for r in todo[:max(0, DETAIL_BUDGET - reads)]:
        try:
            a = get(f"https://www.strava.com/api/v3/activities/{r['strava_id']}", token)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("Hit Strava's rate limit; the rest will fill in on the next sync.")
                break
            if e.code == 404:
                r["calories"] = "0"
                continue
            raise
        r["calories"] = f'{a.get("calories") or 0:.0f}'
        filled += 1
        time.sleep(0.5)
    left = sum(1 for r in rows.values() if not r.get("calories"))
    print(f"Calories filled for {filled} runs, {left} still to fetch.")

    out = sorted(rows.values(), key=lambda r: (r["date"], r["start"]))
    with open(PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", restval="")
        w.writeheader()
        w.writerows(out)
    print(f"Checked {seen} runs, added {added}, total {len(out)}.")

if __name__ == "__main__":
    sys.exit(main())
