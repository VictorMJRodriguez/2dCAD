import subprocess
import os
import random
from datetime import datetime, timedelta

try:
    from holidays import country_holidays
except ImportError:
    raise SystemExit("Please install the holidays library first: pip install holidays")

# ================= Configuration =================
START_DATE = datetime(2018, 10, 11)
END_DATE   = datetime(2021, 11, 11)
COMMITS_PER_DAY = (1, 3)
COMMIT_MSG_PREFIX = "chore: routine update"
# ==========================================

# Preload US holidays for all years in the range (more efficient than per-day queries)
YEARS = list(range(START_DATE.year, END_DATE.year + 1))
US_HOLIDAYS = country_holidays('US', years=YEARS)

# Print the loaded holidays for verification
print("Loaded US federal holidays:")
for d in sorted(US_HOLIDAYS.keys()):
    if START_DATE.date() <= d <= END_DATE.date():
        print(f"  {d} - {US_HOLIDAYS[d]}")
print()

def is_working_day(d: datetime) -> bool:
    """Working day = not weekend and not a US federal holiday"""
    if d.weekday() >= 5:          # Saturday=5, Sunday=6
        return False
    if d.date() in US_HOLIDAYS:   # US federal holiday
        return False
    return True

def make_commit(commit_date: datetime, seq: int):
    filename = "activity_log.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"update {commit_date.isoformat()} #{seq}\n")

    subprocess.run(["git", "add", filename], check=True)

    date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    msg = f"{COMMIT_MSG_PREFIX} ({commit_date.date()})"
    subprocess.run(
        ["git", "commit", "-m", msg],
        env=env,
        check=True,
        stdout=subprocess.DEVNULL
    )

def main():
    if subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                      capture_output=True).returncode != 0:
        raise SystemExit("Error: Please run this script inside a Git repository.")

    current = START_DATE
    total = 0
    skipped_holidays = 0
    skipped_weekends = 0

    while current <= END_DATE:
        if current.weekday() >= 5:
            skipped_weekends += 1
        elif current.date() in US_HOLIDAYS:
            skipped_holidays += 1
        else:
            n = random.randint(*COMMITS_PER_DAY)
            for i in range(n):
                commit_time = current.replace(
                    hour=random.randint(9, 18),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                make_commit(commit_time, i + 1)
                total += 1
                print(f"Created: {commit_time.isoformat()}")
        current += timedelta(days=1)

    print(f"\nDone. Total commits: {total}")
    print(f"Skipped weekends: {skipped_weekends} days")
    print(f"Skipped US holidays: {skipped_holidays} days")
    print("To push: git push origin <branch-name>")

if __name__ == "__main__":
    main()