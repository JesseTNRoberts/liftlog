# liftlog

Jesse's strength log. A static page (`index.html`) on GitHub Pages reads three data files and shows today's workout, progress charts, a 12-week calendar and history. No build step.

## Logging a session

When Jesse says what he lifted ("single-leg press 110 for 5 each leg", "abduction 160 for 5"), append rows to the data files and commit with a message like `Log 2026-10-26 hips`.

**`data/lifts.csv`** — one row per set:

```
date,exercise,side,set,weight,reps,notes
```

- `date`: YYYY-MM-DD, in Jesse's local time (US Eastern).
- `exercise`: use the exact names in `data/plan.json` → `exercises` so the "today" card can find the history. Add a new entry to `plan.json` when he does something new.
- `side`: `L`, `R` or `both`. "Each leg" means two rows per set, one `L` and one `R`.
- `weight`: pounds, number only. For side plank, `weight` is seconds held and `reps` is 1.
- Quote `notes` if it contains a comma.

**`data/sessions.csv`** — one row per gym visit:

```
date,focus,minutes,notes
```

`focus` matches the rotation day name (`Hips`, `Calves & hamstrings`, `Upper body & core`, `Mobility`).

## Today's target

The page suggests the next weight: if the last top set hit `targetReps`, add `step`; otherwise repeat. When Jesse asks "what am I doing today?", answer the same way from these files.

## Plan context

- 10-minute sessions in the middle of his morning run at the campus gym.
- Goal: keep the IT band and hip problems from his 50K away. Hip abduction (glute medius) and single-leg press are the priority.
- No back-loaded lifts (no deadlifts, no barbell squats) because of a past back problem.
- Prefers heavy weight and low reps. Keep abduction slow, with a hold at the widest point.
- Mondays and Fridays are 7-mile run days, so gym work is light then.
- Running is tracked in Strava; it's not part of this repo yet.
