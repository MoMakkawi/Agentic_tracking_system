"""
Synthetic Log Generator for Agentic Tracking System.

Generates realistic RFID check-in logs aligned with the ICS schedule,
filling the data gap that occurred after 2026-01-09.

Attendance behavior profiles:
  - Group 1 & 2: Mixed — some on time, some late, some skip sessions
  - Group 3: Fully present until March 2026, then ABSENT for the last 2 months

Output: data/fetched/generated_logs.jsonl
"""

import json
import random
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from icalendar import Calendar

# ─── Configuration ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_PATH = os.path.join(BASE_DIR, "data", "fetched", "logs_data.jsonl")
ICS_PATH = os.path.join(BASE_DIR, "data", "fetched", "pass.ics")
GROUPS_PATH = os.path.join(BASE_DIR, "data", "grouped", "groups.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "fetched", "generated_logs.jsonl")

DEVICE_ID = "Incubateur"
CUTOFF_DATE = datetime(2026, 1, 10)  # Generate for events after this date
MIN_UID_LENGTH = 7                    # Filter out corrupted short UIDs
SCAN_INTERVAL_SEC = (2, 8)            # Seconds between consecutive scans

# Group 3 stops attending after this date (last 2 months = March 2026 onwards)
GROUP3_CUTOFF_DATE = datetime(2026, 3, 10)

# Lateness threshold from config is 10 minutes
LATENESS_THRESHOLD_MINUTES = 10

random.seed(42)  # Reproducible results


# ─── DST Simulation Helper ──────────────────────────────────────────────────
def simulate_dst_offset(dt: datetime) -> datetime:
    """
    Simulate a device stuck in Summer Time (CEST).
    - If DST (Summer): Keep as is.
    - If NOT DST (Winter): Add 1 hour to simulate being ahead.
    """
    # Localize to Paris to check DST status
    dt_with_tz = dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
    
    # Check if DST is active
    dst_offset = dt_with_tz.dst()
    is_dst = dst_offset is not None and dst_offset != timedelta(0)
    
    if is_dst:
        return dt  # Summer -> Already correct
    else:
        return dt + timedelta(hours=1)  # Winter -> Simulate 1h ahead


# ─── Step 1: Load groups ────────────────────────────────────────────────────
def load_groups(groups_path: str) -> dict:
    """Return hardcoded group definitions based on user input, ignoring the file."""
    return {
      "group_1": [ 
        "884131e81", "8841f28bb", "8842155f8", "88421ab6", "88422228c",  
        "8842759f2", "88427bf14", "884321aa4", "88444a860", "88444ae66"
      ],
      "group_3": [ 
        "884527ca2", "8845c7dad", "8845e75a7", "884603ad6", "88461806d",
        "884669f75", "884697c99", "8847220de"
      ],
      "group_2": [ 
        "88472a658", "884828d83", "88484151d", "884879d96", "884891e1b",
        "8849cafbf", "8849cb0a0", "884bc5f6f", "884bf6350", "884bf6a59",
        "884bf7a49", "c3eb3f475", "8841342dd", "884139c3", "8841736ad",
        "884173ea5", "884174ed5", "884227bd5", "88425b41d", "8842a17b1",
        "8842b46e1", "8845fa675", "884604aa6", "8846051bd", "884605ab6",
        "8846146ab", "88462b25c", "88471bc41", "8847954a1", "8847a6f99",
        "884a16944", "884a184a9", "884bf7241", "884bf8cbf", "884bf94a7"
      ]
    }


# ─── Step 2: Extract valid UIDs from existing logs ──────────────────────────
def extract_valid_uids(logs_path: str) -> list:
    """Extract unique, valid UIDs from the Incubateur device logs."""
    uids = set()
    with open(logs_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("device_id") != DEVICE_ID:
                continue
            for log in record.get("logs", []):
                uid = log.get("uid", "")
                if len(uid) >= MIN_UID_LENGTH and uid.isalnum():
                    uids.add(uid)
    return sorted(uids)


# ─── Step 3: Parse ICS events after cutoff ───────────────────────────────────
def parse_future_events(ics_path: str, cutoff: datetime) -> list:
    """Parse ICS file and return events starting after the cutoff date."""
    with open(ics_path, "rb") as f:
        cal = Calendar.from_ical(f.read())

    events = []
    holidays = [datetime(2026, 4, 13).date()]  # Configured holiday
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dtstart = component.get("dtstart")
        if dtstart is None:
            continue

        dt = dtstart.dt
        if not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)

        dtend = component.get("dtend")
        if dtend:
            dte = dtend.dt
            if not isinstance(dte, datetime):
                dte = datetime.combine(dte, datetime.max.time())
            if dte.tzinfo is not None:
                dte = dte.replace(tzinfo=None)
        else:
            dte = dt + timedelta(hours=2)

        if dt > cutoff:
            # Prevent alerts by skipping weekends and holidays
            if dt.weekday() >= 5 or dt.date() in holidays:
                continue
            summary = str(component.get("summary", ""))
            events.append({"start": dt, "end": dte, "summary": summary})

    events.sort(key=lambda e: e["start"])
    return events


# ─── Step 4: Assign attendance profiles to members ──────────────────────────
def assign_profiles(groups: dict) -> dict:
    """
    Assign attendance behavior profiles to each member.
    
    Profiles:
      - "on_time":     Arrives within 0-8 min of session start (always attends)
      - "sometimes_late": Arrives on time ~60% of sessions, late (11-25 min) ~30%, misses ~10%
      - "always_late": Arrives 11-30 min late in most sessions, misses ~15%
      - "sometimes_absent": Misses ~40% of sessions, on time when present
      - "group3_cutoff": Attends normally until GROUP3_CUTOFF_DATE, then never
    """
    profiles = {}
    
    group1_members = [uid.lower() for uid in groups.get("group 1", groups.get("group_1", []))]
    group2_members = [uid.lower() for uid in groups.get("group 2", groups.get("group_2", []))]
    group3_members = [uid.lower() for uid in groups.get("group 3", groups.get("group_3", []))]
    
    # Group 1 (10 members): Mix of 4 cases
    for i, uid in enumerate(group1_members):
        if i < 3:
            profiles[uid] = "on_time"
        elif i < 6:
            profiles[uid] = "late"
        elif i < 8:
            profiles[uid] = "always_absent"
        else:
            profiles[uid] = "sometimes_absent"
    
    # Group 2 (35 members): Mix of 4 cases
    for i, uid in enumerate(group2_members):
        if i < 10:
            profiles[uid] = "on_time"
        elif i < 20:
            profiles[uid] = "late"
        elif i < 25:
            profiles[uid] = "always_absent"
        else:
            profiles[uid] = "sometimes_absent"
    
    # Group 3 (8 members): All attend normally until March, then stop completely
    for uid in group3_members:
        profiles[uid] = "group3_cutoff"
    
    return profiles


def get_arrival_offset(profile: str, event_start: datetime) -> int | None:
    """
    Return arrival offset in seconds relative to event start, or None to skip.
    
    Returns:
      int: seconds after event start the member arrives
      None: member does not attend this session
    """
    if profile == "on_time":
        # Always attends, arrives 1-8 min after start
        return random.randint(60, 480)
    
    elif profile == "late":
        roll = random.random()
        if roll < 0.10:
            return None  # 10% miss
        else:
            # 90% late (11-30 min)
            return random.randint(
                (LATENESS_THRESHOLD_MINUTES + 1) * 60,
                30 * 60
            )
            
    elif profile == "always_absent":
        return None
    
    elif profile == "sometimes_absent":
        roll = random.random()
        if roll < 0.40:
            return None  # 40% miss
        else:
            # 60% on time (1-8 min)
            return random.randint(60, 480)
    
    elif profile == "group3_cutoff":
        if event_start >= GROUP3_CUTOFF_DATE:
            return None  # Completely absent after cutoff
        # Before cutoff: behave like a mix (mostly on time, some late)
        roll = random.random()
        if roll < 0.05:
            return None  # 5% miss before cutoff
        elif roll < 0.20:
            # 15% late
            return random.randint(
                (LATENESS_THRESHOLD_MINUTES + 1) * 60,
                20 * 60
            )
        else:
            # 80% on time
            return random.randint(60, 480)
    
    return random.randint(60, 480)


# ─── Step 5: Generate synthetic log entries ──────────────────────────────────
def generate_logs_for_event(
    event_start: datetime,
    event_end: datetime,
    uid_pool: list,
    profiles: dict,
) -> dict | None:
    """Generate a single JSONL log entry for one scheduled event."""
    logs = []
    
    for uid in uid_pool:
        uid_lower = uid.lower()
        profile = profiles.get(uid_lower, "on_time")
        offset = get_arrival_offset(profile, event_start)
        
        if offset is None:
            continue  # Member skips this session
        
        ts = event_start + timedelta(seconds=offset)
        logs.append({
            "ts": ts,
            "uid": uid
        })
    
    if not logs:
        return None  # No one attended
    
    # Sort logs by timestamp (natural scan order)
    logs.sort(key=lambda l: l["ts"])
    
    # Enforce scan interval to prevent timestamp alerts
    for i in range(1, len(logs)):
        min_ts = logs[i-1]["ts"] + timedelta(seconds=random.randint(SCAN_INTERVAL_SEC[0], SCAN_INTERVAL_SEC[1]))
        if logs[i]["ts"] < min_ts:
            logs[i]["ts"] = min_ts
            
    # Clamp to university hours and event ranges to prevent alerts
    min_univ = event_start.replace(hour=7, minute=50, second=0)
    max_univ = event_start.replace(hour=17, minute=59, second=59)
    
    min_allowed = max(event_start, min_univ)
    max_allowed = min(event_end, max_univ)
    
    if logs[-1]["ts"] > max_allowed:
        excess = logs[-1]["ts"] - max_allowed
        for log in logs:
            log["ts"] -= excess
            
    if logs[0]["ts"] < min_allowed:
        shortfall = min_allowed - logs[0]["ts"]
        for log in logs:
            log["ts"] += shortfall
            
    # Squash any remaining overflow if event is extremely short
    for log in logs:
        if log["ts"] > max_allowed:
            log["ts"] = max_allowed
            
    # Final DST simulation (simulates device clock)
    for log in logs:
        log["ts"] = simulate_dst_offset(log["ts"])

    # Format timestamps
    for log in logs:
        log["ts"] = log["ts"].strftime("%Y-%m-%dT%H:%M:%S")
    
    # Build the record
    received_at = (event_start + timedelta(minutes=random.randint(30, 90))).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )
    
    return {
        "count": len(logs),
        "device_id": DEVICE_ID,
        "logs": logs,
        "received_at": received_at,
    }


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    print(f"[1/5] Loading groups from {GROUPS_PATH}...")
    groups = load_groups(GROUPS_PATH)
    for gname, members in groups.items():
        print(f"       {gname}: {len(members)} members")
    
    print(f"[2/5] Extracting valid UIDs from {LOGS_PATH}...")
    uid_pool = extract_valid_uids(LOGS_PATH)
    print(f"       Found {len(uid_pool)} valid UIDs.")
    
    print(f"[3/5] Assigning attendance profiles...")
    profiles = assign_profiles(groups)
    profile_counts = {}
    for p in profiles.values():
        profile_counts[p] = profile_counts.get(p, 0) + 1
    for p, c in sorted(profile_counts.items()):
        print(f"       {p}: {c} members")
    
    print(f"[4/5] Parsing ICS events after {CUTOFF_DATE.date()}...")
    events = parse_future_events(ICS_PATH, CUTOFF_DATE)
    print(f"       Found {len(events)} future events.")
    
    # Filter to only UIDs that are in groups (we want predictable behavior)
    all_group_uids = set()
    for members in groups.values():
        for m in members:
            all_group_uids.add(m.lower())
    
    # Use all UIDs from pool but prioritize group members for profile matching
    grouped_pool = [uid for uid in uid_pool if uid.lower() in all_group_uids]
    ungrouped_pool = [uid for uid in uid_pool if uid.lower() not in all_group_uids]
    
    print(f"       Grouped UIDs: {len(grouped_pool)}, Ungrouped: {len(ungrouped_pool)}")
    
    print(f"[5/5] Generating synthetic log entries...")
    generated = []
    events_after_g3_cutoff = 0
    
    for event in events:
        # For ungrouped UIDs: random 50-80% attendance
        ungrouped_attendees = random.sample(
            ungrouped_pool,
            max(1, int(len(ungrouped_pool) * random.uniform(0.50, 0.80)))
        ) if ungrouped_pool else []
        
        # Combine grouped + ungrouped attendees
        full_pool = grouped_pool + ungrouped_attendees
        
        entry = generate_logs_for_event(event["start"], event["end"], full_pool, profiles)
        if entry:
            generated.append(entry)
        
        if event["start"] >= GROUP3_CUTOFF_DATE:
            events_after_g3_cutoff += 1
    
    print(f"\n       Writing {len(generated)} entries to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for record in generated:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    # Summary
    total_scans = sum(r["count"] for r in generated)
    first_ts = generated[0]["logs"][0]["ts"] if generated else "N/A"
    last_ts = generated[-1]["logs"][-1]["ts"] if generated else "N/A"
    
    print(f"\n{'='*60}")
    print(f"  Generation complete!")
    print(f"  Entries:                {len(generated)}")
    print(f"  Total scans:            {total_scans}")
    print(f"  Date range:             {first_ts} -> {last_ts}")
    print(f"  Events after G3 cutoff: {events_after_g3_cutoff}")
    print(f"  G3 cutoff date:         {GROUP3_CUTOFF_DATE.date()}")
    print(f"  Output:                 {OUTPUT_PATH}")
    print(f"{'='*60}")
    
    # Profile summary per group
    print(f"\n  Profile assignments:")
    for gname, members in groups.items():
        print(f"  {gname}:")
        for uid in members:
            p = profiles.get(uid.lower(), "unknown")
            print(f"    {uid}: {p}")


if __name__ == "__main__":
    main()
