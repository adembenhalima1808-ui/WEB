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
CHURN_REPO = "adembenhalima1808-ui/customer-churn-segmentation"
ALL_DEFAULT_REPOS = {WAREHOUSE_REPO, KITSUNE_REPO, CHURN_REPO}
CONFIG_PATH = DATA_DIR / "config.json"


def _write_stale_config():
    """Simulate a config.json saved back when only the warehouse-sim card existed."""
    CONFIG_PATH.write_text(json.dumps({"projects_cards": [{"repo": WAREHOUSE_REPO, "title": "Warehouse Robot Traffic Simulator"}]}))


class BackfillDefaultCardsTests(unittest.TestCase):
    def setUp(self):
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()

    def test_stale_config_gains_every_missing_default_card(self):
        _write_stale_config()
        cfg = config_store.load_config()
        repos = {c["repo"] for c in cfg["projects_cards"]}
        self.assertEqual(repos, ALL_DEFAULT_REPOS)

    def test_backfill_persists_to_disk(self):
        _write_stale_config()
        config_store.load_config()
        on_disk = json.loads(CONFIG_PATH.read_text())
        self.assertEqual(set(on_disk["_backfilled_card_repos"]), ALL_DEFAULT_REPOS)
        self.assertEqual(len(on_disk["projects_cards"]), len(ALL_DEFAULT_REPOS))

    def test_a_default_card_added_later_still_gets_backfilled(self):
        # Regression: an earlier version tracked one global "has this ever run"
        # flag. Once a site had been migrated for the first two default cards,
        # that flag stayed true forever, so a third card added to
        # DEFAULT_CONFIG later was silently never backfilled on that site.
        _write_stale_config()
        config_store.load_config()  # first load: backfills warehouse + kitsune only, as if churn didn't exist yet

        on_disk = json.loads(CONFIG_PATH.read_text())
        on_disk["projects_cards"] = [c for c in on_disk["projects_cards"] if c["repo"] != CHURN_REPO]
        on_disk["_backfilled_card_repos"] = [r for r in on_disk["_backfilled_card_repos"] if r != CHURN_REPO]
        CONFIG_PATH.write_text(json.dumps(on_disk))

        cfg = config_store.load_config()
        repos = {c["repo"] for c in cfg["projects_cards"]}
        self.assertIn(CHURN_REPO, repos)

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
        self.assertEqual(repos, ALL_DEFAULT_REPOS)


if __name__ == "__main__":
    unittest.main()
