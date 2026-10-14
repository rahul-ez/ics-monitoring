import io
import json
import unittest
import zipfile
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from prototype.demo import assess, candidates, package, replay, sample_data


class DemoLogicTests(unittest.TestCase):
    def setUp(self):
        self.data = sample_data()

    def test_quality_exclusions_and_source_immutability(self):
        before = self.data.copy(deep=True)
        result = assess(self.data, "timestamp", (pd.Timestamp("2026-09-03"), pd.Timestamp("2026-09-04")))
        self.assertFalse(result["errors"])
        self.assertEqual(result["removed"], 288)
        self.assertEqual(result["channels"]["Use"].sum(), 4)
        self.assertLess(result["days"], 13)
        pd.testing.assert_frame_equal(self.data, before)

    def test_insufficient_duplicate_and_constant_data(self):
        self.assertTrue(assess(self.data.head(50), "timestamp")["errors"])
        duplicate = self.data.copy()
        duplicate.loc[1, "timestamp"] = duplicate.loc[0, "timestamp"]
        self.assertTrue(any("Duplicate" in e for e in assess(duplicate, "timestamp")["errors"]))
        constant = self.data.copy()
        constant.iloc[:, 1:] = 1
        self.assertTrue(assess(constant, "timestamp")["errors"])

    def test_budget_failure_and_export_truthfulness(self):
        _, failed = candidates(.1)
        self.assertIsNone(failed)
        _, chosen = candidates(1)
        self.assertEqual(chosen["Candidate"], "Balanced")
        result = assess(self.data, "timestamp")
        blob, _ = package("Test", result, chosen, 1, result["channels"].loc[result["channels"]["Use"]], "test-hash", "")
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            manifest = json.loads(archive.read("manifest.demo.json"))
            self.assertFalse(manifest["geco_integrated"])
            self.assertEqual(manifest["artifact_type"], "NON_EXECUTABLE_DEMO_PACKAGE")
            self.assertFalse(any(name.endswith(".csv") and "schema" not in name for name in archive.namelist()))

    def test_replay_missing_and_prefix_invariance(self):
        trace, _, _ = replay(self.data, "timestamp", "level_m", self.data, 300, "Missing measurement")
        self.assertTrue(trace.loc[trace["Reading"].isna(), "Alarm"].isna().all())
        full, _, _ = replay(self.data, "timestamp", "level_m", self.data, 300)
        prefix, _, _ = replay(self.data.head(500), "timestamp", "level_m", self.data, 300)
        pd.testing.assert_frame_equal(full.head(500), prefix)


class StreamlitFlowTests(unittest.TestCase):
    def click(self, app, label):
        button = next(b for b in app.button if b.label == label)
        button.click().run()
        self.assertFalse(app.exception, [e.message for e in app.exception])

    def prepare(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=20).run()
        self.assertFalse(app.exception)
        app.checkbox[0].check().run()
        self.click(app, "Create project & check data")
        self.click(app, "Confirm data & continue")
        return app

    def test_complete_flow_and_invalidation(self):
        app = self.prepare()
        self.click(app, "Save requirement & continue")
        self.click(app, "Use balanced profile & continue")
        self.click(app, "Run demo calibration")
        self.click(app, "Review example result")
        self.click(app, "Continue to shadow monitoring")
        self.click(app, "Run recorded-data replay")
        self.assertIsNotNone(app.session_state["replay_result"])
        # Returning to the requirement and saving it discards the previous run.
        next(b for b in app.button if "Monitoring requirement" in b.label).click().run()
        app.number_input[0].set_value(.1).run()
        self.click(app, "Save requirement & continue")
        self.assertIsNone(app.session_state["calibration"])
        self.assertIsNone(app.session_state["replay_result"])
        self.click(app, "Use balanced profile & continue")
        self.click(app, "Run demo calibration")
        self.assertIsNone(app.session_state["calibration"]["selected"])
        self.assertTrue(any("no tested configuration" in e.value for e in app.error))


if __name__ == "__main__":
    unittest.main()
