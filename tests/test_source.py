import unittest

from book_competition_data.capture import normalize
from book_competition_data.cli import resource, validate


class SourceTests(unittest.TestCase):
    def raw(self):
        return (
            b"<h1>Open Opportunities</h1>"
            b"<h2>2026 NASA Space Apps Challenge</h2>"
            b"<p>Register now for the largest annual global hackathon on November 14-15, 2026.</p>"
            b"<p>This challenge offers opportunities for anyone with an interest in space and science.</p>"
        )

    def test_nasa_source_fixture(self):
        source = resource("source-nasa-space-apps-2026.json")
        data = normalize(self.raw(), source, "2026-09-07T00:00:00Z")
        item = data["items"][0]
        for item in data["items"]:
            item["provenance"].update(
                raw_object_key="landing/test",
                bronze_manifest_key="control/manifests/test",
            )
        self.assertEqual(item["status"], "open")
        self.assertEqual(item["deadline"], {"kind": "rolling", "at": None})
        self.assertEqual(item["category"], "hackathon")
        self.assertEqual(item["eligible_countries"], ["GLOBAL"])
        self.assertTrue(item["terms"]["team_allowed"])
        self.assertEqual(validate(data)["schema_version"], source["schema_version"])

    def test_source_drift_rejected(self):
        with self.assertRaises(ValueError):
            normalize(b"<h1>unrelated page</h1>", resource("source.json"), "2026-09-07T00:00:00Z")

    def test_cassini_source_fixture(self):
        source = resource("source-cassini-challenges-2026.json")
        raw = (
            "<h1>CASSINI Challenges 2026</h1>"
            "<p>12 winners get a €100,000 prize award to accelerate their growth.</p>"
            "<p>Technology Readiness Level (TRL) ≥ 5 and Commercial Readiness Level (CRL) ≥ 4.</p>"
            "<p>September - October 2026</p><p>Rules of contest</p>"
        ).encode()
        data = normalize(raw, source, "2026-09-07T00:00:00Z")
        item = data["items"][0]
        item["provenance"].update(
            raw_object_key="landing/test",
            bronze_manifest_key="control/manifests/test",
        )
        self.assertEqual(item["title"], "CASSINI Challenges 2026")
        self.assertEqual(item["category"], "entrepreneurship")
        self.assertEqual(item["status"], "open")
        self.assertEqual(item["deadline"], {"kind": "unknown", "at": None})
        self.assertEqual(item["value"], {"kind": "cash", "amount": 100000, "currency": "EUR", "guaranteed": False})
        self.assertEqual(validate(data)["schema_version"], source["schema_version"])
        later = normalize(raw, source, "2026-11-01T00:00:00Z")
        self.assertEqual(later["items"][0]["status"], "unknown")

    def cassini_raw(self):
        return (
            "<h1>CASSINI Challenges 2026</h1>"
            "<p>12 winners get a €100,000 prize award to accelerate their growth.</p>"
            "<p>Technology Readiness Level (TRL) ≥ 5 and Commercial Readiness Level (CRL) ≥ 4.</p>"
            "<p>September - October 2026</p><p>Rules of contest</p>"
        ).encode()

    def test_cassini_window_follows_brussels_time_not_the_utc_date(self):
        source = resource("source-cassini-challenges-2026.json")
        cases = {
            # 1 Sep 00:30 in Brussels (CEST) is still 31 Aug in UTC.
            "2026-08-31T22:30:00Z": "open",
            "2026-08-31T21:59:59Z": "unknown",
            "2026-09-01T00:30:00+02:00": "open",
            # 31 Oct 23:30 UTC is already 1 Nov 00:30 in Brussels (CET after 25 Oct).
            "2026-10-31T23:30:00Z": "unknown",
            "2026-10-31T22:59:59Z": "open",
            "2026-11-01T06:00:00+07:00": "unknown",
            "2026-10-31T18:59:59-04:00": "open",
        }
        for checked_at, status in cases.items():
            with self.subTest(checked_at=checked_at):
                item = normalize(self.cassini_raw(), source, checked_at)["items"][0]
                self.assertEqual(item["status"], status)

    def test_nasa_status_boundary_and_offsets(self):
        source = resource("source-nasa-space-apps-2026.json")
        cases = {
            "2026-11-15T23:59:30Z": "open",
            "2026-11-16T00:00:00Z": "unknown",
            "2026-11-16T06:59:00+07:00": "open",
            "2026-11-16T07:00:00+07:00": "unknown",
        }
        for checked_at, status in cases.items():
            with self.subTest(checked_at=checked_at):
                self.assertEqual(normalize(self.raw(), source, checked_at)["items"][0]["status"], status)

    def test_naive_capture_clock_is_rejected_with_value_error(self):
        # A naive clock used to be compared as if it were UTC (CASSINI) or raise
        # TypeError against the aware NASA bound, escaping the runtime's handler.
        for name, raw in (
            ("source-cassini-challenges-2026.json", self.cassini_raw()),
            ("source-nasa-space-apps-2026.json", self.raw()),
        ):
            for checked_at in ("2026-09-07T00:00:00", "2026-09-07"):
                with self.subTest(source=name, checked_at=checked_at), self.assertRaises(ValueError):
                    normalize(raw, resource(name), checked_at)


if __name__ == "__main__":
    unittest.main()
