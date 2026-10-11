"""Read-only, account-neutral AWS engine metadata collection. No resource mutations."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence"
OUT.mkdir(exist_ok=True)
VERSION = "8.4.mysql_aurora.8.4.7"
FAMILY = "aurora-mysql8.4"


def collect(region, kind, args):
    command = ["aws", "rds", *args, "--region", region, "--output", "json",
               "--no-cli-pager", "--cli-connect-timeout", "10", "--cli-read-timeout", "30"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=180)
    if result.returncode:
        # Errors aren't silently converted into empty, apparently successful inventories.
        raise RuntimeError(f"{region}/{kind}: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    path = OUT / f"{region}_{kind}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    count = len(payload.get("Parameters", payload.get("EngineDefaults", {}).get("Parameters", []))) if isinstance(payload, dict) else 0
    return {"region": region, "kind": kind, "file": path.name, "parameter_count": count,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "command": command}


def main():
    jobs = []
    for region in ("ap-northeast-1", "ap-northeast-3"):
        jobs.extend([
            (region, "engine", ["describe-db-engine-versions", "--engine", "aurora-mysql",
             "--engine-version", VERSION]),
            (region, "serverless", ["describe-orderable-db-instance-options", "--engine", "aurora-mysql",
             "--engine-version", VERSION, "--db-instance-class", "db.serverless",
             "--query", "OrderableDBInstanceOptions[].{EngineVersion:EngineVersion,DBInstanceClass:DBInstanceClass,SupportedEngineModes:SupportedEngineModes,SupportsGlobalDatabases:SupportsGlobalDatabases,AvailabilityZoneCount:length(AvailabilityZones)}"]),
            (region, "cluster_defaults", ["describe-engine-default-cluster-parameters", "--db-parameter-group-family", FAMILY]),
            (region, "instance_defaults", ["describe-engine-default-parameters", "--db-parameter-group-family", FAMILY]),
            (region, "cluster_group", ["describe-db-cluster-parameters", "--db-cluster-parameter-group-name", "default." + FAMILY]),
            (region, "instance_group", ["describe-db-parameters", "--db-parameter-group-name", "default." + FAMILY]),
        ])
    manifest = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(collect, *job) for job in jobs]
        for f in as_completed(futures):
            entry = f.result()
            manifest.append(entry)
            print(f"{entry['region']} {entry['kind']}: {entry['parameter_count']}", flush=True)
    (OUT / "manifest.json").write_text(json.dumps(sorted(manifest, key=lambda x: (x['region'], x['kind'])), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
