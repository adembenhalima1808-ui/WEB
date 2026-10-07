"""Unit tests for the one-time default-project-card backfill in config_store.

A config.json saved before the Kitsune card existed in DEFAULT_CONFIG never
picked it up on its own: load_config() only fills truly-missing top-level
keys, and 'projects_cards' already existed. These tests cover the migration
that fixes that for already-deployed sites without clobbering later edits.
"""
import json
import os
import tempfile
import unittest

TMP = tempfile.mkdtemp()
os.environ.setdefault("DATA_DIR", TMP)
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("COOKIE_SECURE", "0")
os.environ.setdefault("ENV_FILE", "")

from app import config_store
from app.settings import DATA_DIR

WAREHOUSE_REPO = "Ilias-Mrtd/Projet--GroupeD"
KITSUNE_REPO = "adembenhalima1808-ui/WEB"
CONFIG_PATH = DATA_DIR / "config.json"


def _write_stale_config():
    """Simulate a config.json saved back when only the warehouse-sim card existed."""
    CONFIG_PATH.write_text(json.dumps({"projects_cards": [{"repo": WAREHOUSE_REPO, "title": "Warehouse Robot Traffic Simulator"}]}))


class BackfillDefaultCardsTests(unittest.TestCase):
    def setUp(self):
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()

    def test_stale_config_gains_the_missing_default_card(self):
        _write_stale_config()
        cfg = config_store.load_config()
        repos = {c["repo"] for c in cfg["projects_cards"]}
        self.assertIn(KITSUNE_REPO, repos)
        self.assertIn(WAREHOUSE_REPO, repos)

    def test_backfill_runs_once_and_persists_to_disk(self):
        _write_stale_config()
        config_store.load_config()
        on_disk = json.loads(CONFIG_PATH.read_text())
        self.assertTrue(on_disk["_default_cards_backfilled"])
        self.assertEqual(len(on_disk["projects_cards"]), 2)

    def test_owner_removal_after_backfill_is_not_undone(self):
        _write_stale_config()
        config_store.load_config()  # first load: backfills the Kitsune card
        cfg = config_store.load_config()
        cfg["projects_cards"] = [c for c in cfg["projects_cards"] if c["repo"] != KITSUNE_REPO]
        config_store.save_config(cfg)

        reloaded = config_store.load_config()
        repos = {c["repo"] for c in reloaded["projects_cards"]}
        self.assertNotIn(KITSUNE_REPO, repos)

    def test_fresh_config_already_has_every_default_card(self):
        cfg = config_store.load_config()
        repos = {c["repo"] for c in cfg["projects_cards"]}
        self.assertIn(KITSUNE_REPO, repos)
        self.assertIn(WAREHOUSE_REPO, repos)


if __name__ == "__main__":
    unittest.main()
