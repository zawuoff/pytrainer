"""PyTrainer's own tests. Run with: python3 -m unittest discover -s tests -t .

Every test uses a throwaway data dir so your real progress database is never touched.
"""

import os
import tempfile

os.environ["PYTRAINER_DATA"] = tempfile.mkdtemp(prefix="pytrainer-test-")
