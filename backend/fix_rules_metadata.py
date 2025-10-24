import json
from datetime import datetime

filename = "rules.json"

with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

rules = data.get("rules", {})
rule_metadata = data.get("rule_metadata", {})

now = datetime.now().isoformat()

for rule_id in rules:
    if rule_id not in rule_metadata:
        rule_metadata[rule_id] = {
            "created_at": now,
            "updated_at": now,
            "author": "Expert System",
            "version": "1.0",
            "status": "active",
            "usage_count": 0,
            "success_rate": 0.0,
            "tags": []
        }

data["rule_metadata"] = rule_metadata

with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Semua rule sudah diberikan metadata aktif.")
