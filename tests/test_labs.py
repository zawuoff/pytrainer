import tempfile
import unittest
from pathlib import Path

from pytrainer import content, labs


class LabTests(unittest.TestCase):
    def test_glob_check(self):
        folder = Path(tempfile.mkdtemp())
        check = {"type": "glob", "label": "wheel", "pattern": str(folder / "dist" / "tokcount-*.whl")}
        self.assertFalse(labs.run_check(check)[0])
        (folder / "dist").mkdir()
        (folder / "dist" / "tokcount-0.1.0-py3-none-any.whl").write_text("x")
        ok, detail = labs.run_check(check)
        self.assertTrue(ok)
        self.assertIn("tokcount-0.1.0", detail)

    def test_ship_lab_is_listed_with_known_check_types(self):
        data = content.load()
        lab = next(lab for lab in data["labs"] if lab["id"] == "lab-ship-package")
        known = {"command", "path", "glob", "absent", "contains", "run"}
        self.assertTrue(all(c["type"] in known for c in lab["checks"]))
        self.assertEqual(lab["order"], max(other["order"] for other in data["labs"]))


if __name__ == "__main__":
    unittest.main()
