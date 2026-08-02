from datetime import datetime, timedelta, timezone

from mlb.api import MLBApiClient
from mlb.database import get_connection, init_db

init_db()
with get_connection() as c:
    m = {
        int(r["team_id"]): r["abbreviation"]
        for r in c.execute("SELECT team_id, abbreviation FROM teams")
    }

now = datetime.now(timezone.utc)
hn_now = now - timedelta(hours=6)
print("Ahora UTC", now.strftime("%Y-%m-%d %H:%M"), "| Honduras", hn_now.strftime("%H:%M"))

client = MLBApiClient()
data = client._get(
    "/schedule",
    params={
        "sportId": 1,
        "startDate": now.strftime("%Y-%m-%d"),
        "endDate": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
    },
)

for day in data.get("dates", []):
    for g in day["games"]:
        st = g["status"]["abstractGameState"]
        if st not in ("Preview", "Live"):
            continue
        away = m.get(g["teams"]["away"]["team"]["id"], "?")
        home = m.get(g["teams"]["home"]["team"]["id"], "?")
        gdt = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
        hn = (gdt - timedelta(hours=6)).strftime("%H:%M")
        mins = (gdt - now).total_seconds() / 60
        det = g["status"].get("detailedState")
        ok = st == "Preview" and mins > 15
        flag = "SI apostar" if ok else "NO"
        print(f"{flag:10} | HN {hn} | {away}@{home} | {det}")
