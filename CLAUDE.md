# liftlog

Jesse's strength log. A static page (`index.html`) on GitHub Pages reads three data files and shows today's workout, progress charts, a 12-week calendar and history. No build step.

## Rules

- **This repo is the only lift log.** Never keep a separate log in a Claude doc, artifact, project doc or memory. "Log it" always means commit and push to this repo.
- **Load the log at the start of every workout.** When Jesse says he's at the gym (or starts a workout), clone/pull this repo first and read `data/plan.json`, `data/lifts.csv` and `data/sessions.csv`. Ask how he's feeling since last session, naming anything in "Current notes" (like the knee). Then tell him today's focus and the target weight for each exercise, worked out the same way the page does (see "Today's target") and adjusted for his answer.
- If the repo can't be reached, say so straight away. Don't fall back to a local log.
- He's usually talking on voice mid-run: keep replies to a sentence or two.
- **10-minute clock.** When he says he's at the gym, note the start time (call the current-time tool if you have one). Before suggesting each next exercise, check the elapsed time: under ~8 minutes, keep going (spare time rule); at 9–10, wrap up. Log the elapsed minutes in `sessions.csv`. If you have no clock (some voice calls), ask him for the time on his watch at the start and when he finishes a set.

## Logging a session

When Jesse says what he lifted ("single-leg press 110 for 5 each leg", "abduction 160 for 5"), append rows to the data files and commit with a message like `Log 2026-10-26 hips`.

**`data/lifts.csv`** — one row per set:

```
date,exercise,side,set,weight,reps,notes
```

- `date`: YYYY-MM-DD, in Jesse's local time (US Eastern).
- `exercise`: use the exact names in `data/plan.json` → `exercises` so the "today" card can find the history. Add a new entry to `plan.json` when he does something new, with a `group` (one of `Quads & glutes`, `Hips`, `Hamstrings`, `Calves`, `Core`, `Chest`, `Shoulders`, `Back`) so the volume chart can colour it.
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

An exercise in `plan.json` can carry `"next": {"weight": 60, "reason": "knee caution"}`, which overrides the suggestion (use it after pain or a deload). For a per-side target use `"next": {"bySide": {"L": 110, "R": 120}, "reason": "..."}`. Remove `next` once he logs a pain-free session at or above that weight.

## Current notes

- The campus gym has no seated calf raise; Tuesday uses `Calf extension` instead.
- Oct 27: pulling on the inside of the left knee during hamstring curl at 80 lb (only under load, fine walking). Nov 3: resolved, lying hamstring curl at 80 × 8 with no pull. Still worth a quick check before hamstring work.
- Oct 28: right inner knee felt tired during the run (sensation, no pain). Ask about it before leg work. Oct 29: knees and hips felt fine.
- Oct 28: very sore from Monday's hips; Wednesday was mostly recovery. If he's sore on a hip day, do one light set and move on.
- Thursday: he dislikes side planks, so use Pallof press (side = the side the machine is on). He does lots of pull-ups, so no seated row; shoulder press instead. Oct 29: Pallof with the machine on his left was much harder than on the right.
- Don't schedule chest press the day after he's done it.
- Nov 1: left hip flexor much tighter than right (fits the weaker left side on Pallof). Give the left extra stretch time.
- Nov 2: left leg weaker on single-leg press (needed help on rep 5 at 120; right fine). Left held at 110, right at 120. Left hip flexor and right knee felt fine. Nov 4: left caught up (130 and 135 × 5 even both sides; 145 was max, L 3 / R 4). Back to one target for both legs.
- **Spare time rule:** legs are guaranteed every session; upper body gets worked in whenever there's time left. If he finishes the planned exercises early, add upper body (chest press, shoulder press) rather than more core. Don't wrap up early.
- Chest press (vertical) and shoulder press are plate-loaded machines. Logged weights include the base (shoulder press base 12 lb, so 2 plates = 102). Suggest weights he can actually load.
- Tuesday hamstrings now on the lying (prone) curl; Nov 3 the right leg pulled harder than the left.
- Nov 4: said lifting every day felt like overworking. If he's tired, offer a lighter day or a different muscle group rather than pushing the plan. He finds the Pallof press boring: at most once a week, on an ab day.
- Single-leg press depth: stop at a 90° knee bend every time so numbers stay comparable. Abduction: sit all the way back (175 is near max that way).
- Mobility: he won't get on the floor, so use standing stretches only. On voice, give one short instruction at a time; he times holds himself.

- Calories on the page are a rough estimate: MET (5 for lifting, 2.3 for mobility) × body weight × minutes, from `plan.json` → `bodyweightLb` and `calories`. Missing minutes count as 10. Update `bodyweightLb` if he gives a new weight (Nov 3: 160 lb).

## Plan context

- 10-minute sessions in the middle of his morning run at the campus gym.
- Goal: keep the IT band and hip problems from his 50K away. Hip abduction (glute medius) and single-leg press are the priority.
- No back-loaded lifts (no deadlifts, no barbell squats) because of a past back problem.
- Prefers heavy weight and low reps. Keep abduction slow, with a hold at the widest point.
- Mondays and Fridays are 7-mile run days, so gym work is light then.
- Running is tracked in Strava; it's not part of this repo yet.
