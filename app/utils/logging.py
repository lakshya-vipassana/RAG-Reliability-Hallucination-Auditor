import json
from datetime import datetime

def log_trace(stage: str, payload: dict, path="storage/trace.log"):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "payload": payload
    }
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
