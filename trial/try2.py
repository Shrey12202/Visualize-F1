import fastf1
from fastf1.core import Laps
import os

fastf1.Cache.enable_cache('cache')  # Make sure cache folder exists

SEASONS = [2023, 2024]  # Seasons to fetch
SESSIONS = ["FP1", "FP2", "FP3", "Q", "SQ", "R"]  # All session types

def session_exists(year, gp_name, session_name):
    """Check if session is cached (telemetry + laps)."""
    cache_path = f"cache/{year}/{gp_name}/{session_name}"
    return os.path.exists(cache_path)

def fetch_session_data(year, gp_name, session_name):
    """Download session data if not cached."""
    try:
        print(f"🔄 Checking {year} {gp_name} {session_name}...")
        session = fastf1.get_session(year, gp_name, session_name)
        session.load()
        laps = session.laps
        if not laps.empty:
            print(f"✅ Data loaded for {year} {gp_name} {session_name}")
        else:
            print(f"⚠️ No laps data for {year} {gp_name} {session_name}")
    except Exception as e:
        print(f"❌ Failed for {year} {gp_name} {session_name}: {e}")

# Scan and download
for season in SEASONS:
    schedule = fastf1.get_event_schedule(season)
    for _, event in schedule.iterrows():
        gp_name = event['EventName']
        for session_name in SESSIONS:
            if not session_exists(season, gp_name, session_name):
                fetch_session_data(season, gp_name, session_name)
            else:
                print(f"📦 Cached: {season} {gp_name} {session_name}")

print("\n🎯 All sessions checked. Missing data downloaded.")
