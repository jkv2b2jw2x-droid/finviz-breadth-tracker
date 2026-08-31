import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import finviz_breadth_updater as updater


SAMPLE_VALUES = {
    "New High": {"count": "68", "percent": "26.1%"},
    "New Low": {"count": "193", "percent": "73.9%"},
    "Advancing": {"count": "1975", "percent": "35.1%"},
    "Declining": {"count": "3397", "percent": "60.4%"},
}


class MarketSessionDateTests(unittest.TestCase):
    def test_monday_morning_uses_friday_session(self) -> None:
        now = datetime(2026, 8, 31, 2, 30, tzinfo=updater.NY_TZ)
        self.assertEqual(
            updater.latest_completed_market_session_date(now),
            "2026-08-28",
        )

    def test_market_holiday_is_skipped(self) -> None:
        now = datetime(2026, 9, 8, 2, 30, tzinfo=updater.NY_TZ)
        self.assertEqual(
            updater.latest_completed_market_session_date(now),
            "2026-09-04",
        )

    def test_weekend_is_skipped(self) -> None:
        now = datetime(2026, 9, 5, 10, 0, tzinfo=updater.NY_TZ)
        self.assertEqual(
            updater.latest_completed_market_session_date(now),
            "2026-09-04",
        )

    def test_completed_current_session_is_used_after_close(self) -> None:
        now = datetime(2026, 8, 31, 16, 15, tzinfo=updater.NY_TZ)
        self.assertEqual(
            updater.latest_completed_market_session_date(now),
            "2026-08-31",
        )

    def test_intraday_delayed_run_fails_instead_of_mislabeling_data(self) -> None:
        now = datetime(2026, 8, 31, 10, 12, tzinfo=updater.NY_TZ)
        with self.assertRaisesRegex(updater.FinvizBreadthError, "session is in progress"):
            updater.latest_completed_market_session_date(now)


class UpsertTests(unittest.TestCase):
    def test_upsert_replaces_existing_session_without_duplicate(self) -> None:
        existing = [
            {
                "Date": "2026-08-28",
                "New High": "1",
                "New High %": "1.0%",
                "New Low": "2",
                "New Low %": "2.0%",
                "Advancing": "3",
                "Advancing %": "3.0%",
                "Declining": "4",
                "Declining %": "4.0%",
            }
        ]
        with patch.object(updater, "read_existing_rows", return_value=existing):
            rows = updater.upsert_market_session_row(SAMPLE_VALUES, "2026-08-28")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Date"], "2026-08-28")
        self.assertEqual(rows[0]["Advancing"], "1975")


class ParserTests(unittest.TestCase):
    def test_current_finviz_breadth_shape_parses(self) -> None:
        html = """
        <html><body>
          <p>Advancing</p><p>35.1% (1975)</p>
          <p>Declining</p><p>(3397) 60.4%</p>
          <p>New High</p><p>26.1% (68)</p>
          <p>New Low</p><p>(193) 73.9%</p>
          <p>Above</p><p>46.9% (2633) SMA50</p>
        </body></html>
        """
        self.assertEqual(updater.extract_breadth_values(html), SAMPLE_VALUES)


class WorkflowTests(unittest.TestCase):
    def test_workflow_uses_timezone_schedule_without_runtime_skip_guard(self) -> None:
        workflow_path = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "update-finviz.yml"
        )
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn('cron: "30 9 * * 1-5"', workflow)
        self.assertIn('timezone: "Asia/Amman"', workflow)
        self.assertNotIn("skip_update", workflow)
        self.assertEqual(workflow.count("cron:"), 1)


if __name__ == "__main__":
    unittest.main()
