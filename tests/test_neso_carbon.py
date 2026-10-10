import unittest
from datetime import date, datetime, timedelta, timezone

from vfw_research.neso_carbon import extract_forecasts


def payload():
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    rows = []
    for index in range(-1, 48):
        begin = start + timedelta(minutes=30 * index)
        rows.append({"from": begin.isoformat(),
                     "to": (begin + timedelta(minutes=30)).isoformat(),
                     "intensity": {"forecast": index + 1}})
    return {"data": {"regionid": 1, "shortname": "North Scotland", "data": rows}}


class NesoCarbonTests(unittest.TestCase):
    def test_exact_utc_day_and_region(self):
        name, rows = extract_forecasts(payload(), region_id=1, day=date(2025, 1, 1))
        self.assertEqual(name, "North Scotland")
        self.assertEqual(len(rows), 48)
        self.assertEqual(rows[0][1], 1)
        self.assertEqual(rows[-1][1], 48)

    def test_rejects_region_gaps_duplicates_and_invalid_forecasts(self):
        with self.assertRaisesRegex(ValueError, "region ID"):
            extract_forecasts(payload(), region_id=13, day=date(2025, 1, 1))
        item = payload()
        item["data"]["data"].pop()
        with self.assertRaisesRegex(ValueError, "missing or duplicate"):
            extract_forecasts(item, region_id=1, day=date(2025, 1, 1))
        item = payload()
        item["data"]["data"][1]["intensity"]["forecast"] = -1
        with self.assertRaisesRegex(ValueError, "non-negative"):
            extract_forecasts(item, region_id=1, day=date(2025, 1, 1))


if __name__ == "__main__":
    unittest.main()
