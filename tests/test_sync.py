import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import server
from pytrainer import content, sync


def a_step():
    return next(e for e in content.load()["exercises"].values()
                if e.get("mode", "function") == "function" and not e.get("extra") and e.get("topic") != "exam")


class SyncTests(unittest.TestCase):
    def setUp(self):
        root = Path(tempfile.mkdtemp())
        self.patches = [mock.patch.object(sync, "PROJECTS_DIR", root / "projects"),
                        mock.patch.object(sync, "STEPS_DIR", root / "steps"),
                        mock.patch.object(sync, "find_editor", return_value=None)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_open_step_writes_files_and_falls_back_to_a_link(self):
        ex = a_step()
        r = server.api_sync_open({"kind": "step", "id": ex["id"], "files": {"solution.py": "print(1)\n", "evil.py": "x"}})
        folder = Path(r["folder"])
        self.assertEqual((folder / "solution.py").read_text(), "print(1)\n")
        self.assertFalse((folder / "evil.py").exists(), "only the item's own files are written")
        self.assertTrue((folder / "STEP.md").is_file())
        self.assertIsNone(r["opened"])
        self.assertTrue(r["url"].startswith("vscode://file/"))
        self.assertEqual(r["kept"], [])

    def test_changed_work_on_disk_is_kept(self):
        ex = a_step()
        folder = sync.STEPS_DIR / ex["id"]
        folder.mkdir(parents=True)
        (folder / "solution.py").write_text("# my own work\n")
        r = server.api_sync_open({"kind": "step", "id": ex["id"], "files": {"solution.py": "browser version\n"}})
        self.assertEqual(r["kept"], ["solution.py"])
        self.assertEqual(r["files"]["solution.py"], "# my own work\n")
        # A file still equal to the starter isn't "work": the browser's version replaces it.
        (folder / "solution.py").write_text(ex["starter"])
        r = server.api_sync_open({"kind": "step", "id": ex["id"], "files": {"solution.py": "browser version\n"}})
        self.assertEqual(r["files"]["solution.py"], "browser version\n")

    def test_poll_returns_only_changed_files(self):
        ex = a_step()
        r = server.api_sync_open({"kind": "step", "id": ex["id"], "files": {"solution.py": "a = 1\n"}})
        stamp = r["stamp"]
        same = server.api_sync_poll({"kind": "step", "id": ex["id"], "names": ["solution.py"], "stamp": stamp})
        self.assertEqual(same["changed"], {})
        path = Path(r["folder"]) / "solution.py"
        path.write_text("a = 2\n")
        os.utime(path, ns=(time.time_ns(), stamp["solution.py"] + 5_000_000))
        moved = server.api_sync_poll({"kind": "step", "id": ex["id"], "names": ["solution.py", "other.py"], "stamp": stamp})
        self.assertEqual(moved["changed"], {"solution.py": "a = 2\n"})
        path.unlink()
        gone = server.api_sync_poll({"kind": "step", "id": ex["id"], "names": ["solution.py"], "stamp": moved["stamp"]})
        self.assertEqual(gone["missing"], ["solution.py"])

    def test_project_open_launches_the_editor(self):
        launched = []
        with mock.patch.object(sync, "find_editor", return_value=("/usr/bin/code", "VS Code")), \
                mock.patch.object(sync, "_launch", side_effect=lambda path, args: launched.append((path, args))):
            r = server.api_sync_open({"kind": "project", "id": "chunker", "files": {}, "file": "chunker.py"})
        self.assertEqual(r["opened"], "VS Code")
        folder = Path(r["folder"])
        self.assertTrue((folder / "BRIEF.md").is_file())
        self.assertEqual(launched[0][1][0], str(folder))
        project = content.load()["projects_by_id"]["chunker"]
        self.assertEqual(set(r["files"]), set(project["starter_files"]))

    def test_bad_requests(self):
        with self.assertRaises(server.ApiError):
            server.api_sync_open({"kind": "folder", "id": "x"})
        with self.assertRaises(server.ApiError):
            server.api_sync_open({"kind": "project", "id": "../../etc"})
        predict = next((e for e in content.load()["exercises"].values() if e.get("mode") == "predict"), None)
        if predict:
            with self.assertRaises(server.ApiError):
                server.api_sync_open({"kind": "step", "id": predict["id"]})
        with self.assertRaises(ValueError):
            sync._safe(Path("/tmp"), "../x")


if __name__ == "__main__":
    unittest.main()
