from pathlib import Path

import fastf1


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))

print("Downloading/loading the 2024 Monaco Grand Prix...")

session = fastf1.get_session(2024, "Monaco", "R")
session.load()

laps = session.laps

print(f"\nEvent: {session.event['EventName']}")
print(f"Total lap records: {len(laps)}")
print(f"Drivers: {sorted(laps['Driver'].dropna().unique())}")

print("\nSample laps:")
print(
    laps[
        [
            "Driver",
            "LapNumber",
            "LapTime",
            "Compound",
            "Stint",
            "TyreLife",
        ]
    ].head(10)
)