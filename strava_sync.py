import requests
import json
import os
from datetime import datetime

# Load credentials from file
def load_credentials():
    creds = {}
    with open(os.path.expanduser("~/.strava_credentials")) as f:
        for line in f:
            key, value = line.strip().split("=")
            creds[key] = value
    return creds

# Get a fresh access token using refresh token
def get_access_token(creds):
    response = requests.post(
        "https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": creds["STRAVA_CLIENT_ID"],
            "client_secret": creds["STRAVA_CLIENT_SECRET"],
            "refresh_token": creds["STRAVA_REFRESH_TOKEN"],
            "grant_type": "refresh_token"
        }
    )
    return response.json()["access_token"]

# Fetch recent activities from Strava
def get_activities(access_token, num_activities=20):
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": num_activities}
    )
    return response.json()

# Fetch laps for a single activity
def get_laps(access_token, activity_id):
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/laps",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()

# Fetch full activity detail (includes description)
def get_activity_detail(access_token, activity_id):
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()

# Format a single activity into readable text
def format_activity(a, laps):
    lines = []

    # Header
    date = a["start_date_local"][:10]
    name = a["name"]
    sport = a["sport_type"]
    lines.append(f"\n{'='*60}")
    lines.append(f"Date: {date} | Sport: {sport} | Name: {name}")

    # Description
    description = a.get("description") or ""
    if description:
        lines.append(f"Description: {description}")

    # Distance & time
    distance_miles = round(a["distance"] / 1609.34, 2)
    moving_min = round(a["moving_time"] / 60, 1)
    elapsed_min = round(a["elapsed_time"] / 60, 1)
    elevation_ft = round(a.get("total_elevation_gain", 0) * 3.28084)
    lines.append(f"Distance: {distance_miles} mi | Moving Time: {moving_min} min | Elapsed Time: {elapsed_min} min | Elevation: {elevation_ft} ft")

    # Heart rate
    avg_hr = a.get("average_heartrate")
    max_hr = a.get("max_heartrate")
    if avg_hr:
        lines.append(f"Heart Rate: avg {avg_hr} bpm | max {max_hr} bpm")

    # Pace (for runs)
    if sport == "Run" and a["distance"] > 0:
        pace_sec_per_mile = a["moving_time"] / (a["distance"] / 1609.34)
        pace_min = int(pace_sec_per_mile // 60)
        pace_sec = int(pace_sec_per_mile % 60)
        lines.append(f"Avg Pace: {pace_min}:{pace_sec:02d} /mi")

    # Laps
    if laps and len(laps) > 1:
        lines.append(f"Laps ({len(laps)}):")
        for i, lap in enumerate(laps, 1):
            lap_dist = round(lap["distance"] / 1609.34, 2)
            lap_min = round(lap["moving_time"] / 60, 1)
            lap_elev = round(lap.get("total_elevation_gain", 0) * 3.28084)
            lap_hr = lap.get("average_heartrate")
            hr_str = f" | HR: {lap_hr} bpm" if lap_hr else ""
            lines.append(f"  Lap {i}: {lap_dist} mi | {lap_min} min | {lap_elev} ft{hr_str}")

    return "\n".join(lines)

# Format all activities
def format_activities(activities, access_token):
    lines = [f"STRAVA ACTIVITIES — Last {len(activities)} activities\n"]
    for i, a in enumerate(activities):
        print(f"Fetching details for activity {i+1}/{len(activities)}...")
        detail = get_activity_detail(access_token, a["id"])
        laps = get_laps(access_token, a["id"])
        a["description"] = detail.get("description")
        lines.append(format_activity(a, laps))
    return "\n".join(lines)

# Save to a text file
def save_to_file(text):
    path = os.path.expanduser("~/projects/strava-claude/activities.txt")
    with open(path, "w") as f:
        f.write(text)
    print(f"\nSaved to {path}")

# Main
if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    creds = load_credentials()
    token = get_access_token(creds)
    activities = get_activities(token, num)
    text = format_activities(activities, token)
    save_to_file(text)
    print(text)