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


if __name__ == "__main__":
    unittest.main()
