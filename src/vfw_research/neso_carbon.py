"""Validate a NESO regional forecast response into the external carbon contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("NESO interval timestamp must be explicit UTC")
    return parsed.astimezone(timezone.utc)


def extract_forecasts(payload: dict, *, region_id: int, day: date) -> tuple[str, list[tuple[datetime, int]]]:
    region = payload.get("data")
    if not isinstance(region, dict) or type(region.get("regionid")) is not int or region["regionid"] != region_id:
        raise ValueError("NESO region ID mismatch")
    name = region.get("shortname")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("NESO region name missing")
    source_rows = region.get("data")
    if not isinstance(source_rows, list):
        raise ValueError("NESO regional data missing")
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    rows = []
    for item in source_rows:
        begin, finish = _utc(item["from"]), _utc(item["to"])
        if finish - begin != timedelta(minutes=30):
            raise ValueError("NESO interval is not 30 minutes")
        if start <= begin and finish <= end:
            value = item["intensity"].get("forecast")
            if type(value) is not int or value < 0:
                raise ValueError("NESO forecast must be a non-negative integer")
            rows.append((begin, value))
    rows.sort()
    if len(rows) != 48 or [begin for begin, _ in rows] != [start + timedelta(minutes=30 * i) for i in range(48)]:
        raise ValueError("NESO requested UTC day has missing or duplicate intervals")
    return name, rows


def convert(response: Path, csv_path: Path, sidecar_path: Path, *, region_id: int,
            day: date, source: str) -> dict:
    expected = ("https://api.carbonintensity.org.uk/regional/intensity/"
                f"{day.isoformat()}T00:00Z/{(day + timedelta(days=1)).isoformat()}T00:00Z/regionid/{region_id}")
    if source != expected:
        raise ValueError("source must be the exact official NESO day/region API URL")
    if csv_path.exists() or sidecar_path.exists():
        raise FileExistsError("output exists; preserve immutable provenance")
    name, rows = extract_forecasts(json.loads(response.read_text(encoding="utf-8")),
                                   region_id=region_id, day=day)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("timestamp_utc", "value"))
        for begin, value in rows:
            writer.writerow((begin.isoformat(), value))
    metadata = {
        "kind": "carbon", "unit": "gCO2/kWh", "source": source,
        "license": "NESO Carbon Intensity API, CC BY 4.0; attribution required",
        "version": f"{day.isoformat()} regional forecast, region {region_id} ({name})",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "preprocessing": "Selected exact 48 half-hour UTC forecast interval starts for requested day; no interpolation or actual values",
        "missing_data_policy": "Reject missing, duplicate, non-UTC, or non-half-hour intervals",
        "sha256": _digest(csv_path), "sampling_interval_seconds": 1800,
        "publisher_response_sha256": _digest(response), "region_id": region_id,
        "region_name": name, "series_type": "regional_forecast_not_metered_actual",
    }
    with sidecar_path.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--region-id", type=int, required=True)
    parser.add_argument("--day", type=date.fromisoformat, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    args = parser.parse_args()
    result = convert(args.response, args.csv, args.provenance, region_id=args.region_id,
                     day=args.day, source=args.source)
    print(json.dumps({"csv": str(args.csv), "provenance": str(args.provenance),
                      "region": result["region_name"], "csv_sha256": result["sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
