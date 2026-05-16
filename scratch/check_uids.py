import json
import os

logs_path = r'c:\Users\a\Desktop\Agentic_tracking_system\data\fetched\logs_data.jsonl'
uids = set()
with open(logs_path, 'r') as f:
    for line in f:
        if not line.strip(): continue
        data = json.loads(line)
        for log in data.get('logs', []):
            uids.add(log.get('uid'))

print(f"Total UIDs: {len(uids)}")
print(f"Sample UIDs: {list(uids)[:10]}")
