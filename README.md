# Lift Log

A one-page strength log on GitHub Pages. Tell Claude what you lifted; Claude appends it to the CSVs in `data/` and the page updates.

- `data/lifts.csv` — every set
- `data/sessions.csv` — every gym visit, with minutes
- `data/plan.json` — weekly rotation, exercise targets and progression steps

To publish: Settings → Pages → Deploy from branch → `main`, folder `/`.

## Strava runs

`data/runs.csv` is filled by the **Sync Strava runs** workflow (every hour, or run it by hand from the Actions tab). It stores summaries only: date, distance, time, elevation, heart rate. No GPS. The first run pulls your whole history.

One-time setup:
1. Create an app at https://www.strava.com/settings/api (Authorization Callback Domain: `localhost`).
2. Open this link with your Client ID filled in, and click Authorize:
   `https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all`
   The page that follows won't load. That's expected. Copy the `code=` value from the address bar.
3. In a terminal, swap the code for a refresh token:
   `curl -s -X POST https://www.strava.com/oauth/token -d client_id=CLIENT_ID -d client_secret=CLIENT_SECRET -d code=CODE -d grant_type=authorization_code`
   and copy `refresh_token` from the reply.
4. Repo → Settings → Secrets and variables → Actions → New repository secret: add `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`.
5. Actions → Sync Strava runs → Run workflow.
