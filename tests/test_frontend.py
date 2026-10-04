"""Static checks on the ES modules in static/js (no browser, no Node needed)."""

import re
import unittest
from pathlib import Path

JS = Path(__file__).resolve().parent.parent / "static" / "js"
IMPORT = re.compile(r'^import \{([^}]*)\} from "([^"]+)";', re.M)
EXPORT = re.compile(r"^export (?:async )?(?:function\*? |const |let |class )([\w$]+)", re.M)


class ModuleGraphTests(unittest.TestCase):
    def setUp(self):
        self.modules = {p: p.read_text(encoding="utf-8") for p in JS.rglob("*.js")}
        self.exports = {p: set(EXPORT.findall(src)) for p, src in self.modules.items()}

    def test_every_import_is_exported_by_its_module(self):
        for path, src in self.modules.items():
            for names, spec in IMPORT.findall(src):
                target = (path.parent / spec).resolve()
                self.assertIn(target, self.exports, f"{path.name} imports missing module {spec}")
                for name in (n.strip() for n in names.split(",") if n.strip()):
                    self.assertIn(name, self.exports[target], f"{path.relative_to(JS)} imports {name} from {spec}, "
                                                              "which doesn't export it")

    def test_nothing_imports_the_entry_module(self):
        for path, src in self.modules.items():
            for _, spec in IMPORT.findall(src):
                self.assertNotEqual((path.parent / spec).resolve(), JS / "main.js", f"{path.name} imports main.js")

    def test_index_loads_the_entry_module(self):
        html = (JS.parent / "index.html").read_text(encoding="utf-8")
        self.assertIn('<script type="module" src="js/main.js"></script>', html)


if __name__ == "__main__":
    unittest.main()
