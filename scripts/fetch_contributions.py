import json
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from profile_config import USERNAME

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "contributions.json"


def fetch_days():
    response = requests.get(
        f"https://github.com/users/{USERNAME}/contributions",
        headers={"User-Agent": "profile-readme"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    counts = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        match = re.match(r"(\d+|No) contribution", tip.get_text(strip=True))
        if target and match:
            counts[target] = 0 if match.group(1) == "No" else int(match.group(1))

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append(
            {
                "date": cell["data-date"],
                "level": int(cell.get("data-level", 0)),
                "count": counts.get(cell.get("id"), 0),
            }
        )
    days.sort(key=lambda day: day["date"])
    return days


def streaks(days):
    longest = current = run = 0
    for day in days:
        run = run + 1 if day["count"] > 0 else 0
        longest = max(longest, run)
    today = date.fromisoformat(days[-1]["date"]) if days else date.today()
    by_date = {day["date"]: day["count"] for day in days}
    cursor = today if by_date.get(today.isoformat(), 0) > 0 else today - timedelta(days=1)
    while by_date.get(cursor.isoformat(), 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def main():
    days = fetch_days()
    current, longest = streaks(days)
    best = max(days, key=lambda day: day["count"]) if days else None
    data = {
        "username": USERNAME,
        "total": sum(day["count"] for day in days),
        "currentStreak": current,
        "longestStreak": longest,
        "bestDay": best,
        "days": days,
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{len(days)} days, {data['total']} contributions")


if __name__ == "__main__":
    main()
