"""End-to-end: the real HTTP server on a free port, with a scratch database."""

import http.client
import json
import threading
import unittest
from datetime import date, timedelta

import server
from pytrainer import content, db, progress


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.httpd.daemon_threads = True
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        exercises = content.load()["exercises"].values()
        cls.ex = next(e for e in exercises if e.get("mode", "function") == "function"
                      and e["difficulty"] >= 1 and e.get("topic") != "exam")

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=60)
        hdrs = {"Host": f"127.0.0.1:{self.port}"}
        if body is not None:
            hdrs["Content-Type"] = "application/json"
        hdrs.update(headers or {})
        conn.request(method, path, json.dumps(body) if body is not None else None, hdrs)
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        ctype = resp.getheader("Content-Type", "")
        return resp.status, (json.loads(data) if ctype.startswith("application/json") else data)

    def check(self, code, kind="practice", duration_s=300):
        return self.request("POST", f"/api/exercise/{self.ex['id']}/check",
                            {"files": {"solution.py": code}, "kind": kind, "duration_s": duration_s})

    def test_state_reports_sandbox_and_data_dir(self):
        status, state = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertIn(state["sandbox"]["level"], ("bwrap", "netns", "basic"))
        self.assertEqual(state["data_dir"], str(db.DATA_DIR))
        self.assertEqual(len(state["topics"]), 38)

    def test_index_and_modules_are_served(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b'type="module"', body)
        status, body = self.request("GET", "/js/main.js")
        self.assertEqual(status, 200)

    def test_path_traversal_is_refused(self):
        status, _ = self.request("GET", "/../server.py")
        self.assertEqual(status, 404)

    def test_cross_origin_post_is_refused(self):
        status, body = self.request("POST", "/api/run", {"code": "print(1)"},
                                    {"Origin": "https://evil.example"})
        self.assertEqual(status, 403)

    def test_wrong_host_is_refused(self):
        status, _ = self.request("GET", "/api/state", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)

    def test_trace_steps_through_the_learners_file(self):
        status, ex = self.request("GET", f"/api/exercise/{self.ex['id']}")
        self.assertEqual(status, 200)
        self.assertIn("debug_call", ex)
        status, t = self.request("POST", f"/api/exercise/{self.ex['id']}/trace",
                                 {"files": {"solution.py": "x = 1\nx += 1\nprint(x)\n"}, "call": ""})
        self.assertEqual(status, 200)
        self.assertEqual(t["stdout"], "2\n")
        self.assertEqual([s["line"] for s in t["steps"] if s["event"] == "line"], [1, 2, 3])

    def test_a_changed_form_review_counts_for_the_original(self):
        from pytrainer import variants
        exercises = content.load()["exercises"].values()
        ex = next(e for e in exercises if e.get("mode", "function") == "function" and e["difficulty"] >= 1
                  and e.get("topic") != "exam" and e["id"] != self.ex["id"])
        st = progress.get_state(ex["id"]) | {"status": "solved", "next_review": date.today().isoformat(),
                                             "last_review": (date.today() - timedelta(days=4)).isoformat(),
                                             "stability": 3.0, "difficulty": 5.0}
        progress.save_state(st)
        variants.save(ex["id"], {
            "title": "Shout it", "prompt": "Write shout(text).", "starter": "def shout(text):\n    ...\n",
            "solution": "def shout(text):\n    return text.upper() + '!'\n",
            "tests": "from solution import shout\n\ndef test_a():\n    assert shout('hi') == 'HI!'\n",
            "based_on": ex["id"]})
        status, v = self.request("GET", f"/api/exercise/{ex['id']}/variant")
        self.assertEqual(v["variant"]["title"], "Shout it")
        self.assertNotIn("solution", v["variant"])
        self.assertEqual(v["checks"], ["a"])
        status, r = self.request("POST", f"/api/exercise/{ex['id']}/check", {
            "files": {"solution.py": "def shout(text):\n    return text.upper() + '!'\n"},
            "kind": "review", "variant": True, "duration_s": 200})
        self.assertEqual(r["result"]["status"], "passed", r["result"])
        self.assertIn("shout", r["reference"])
        st = progress.get_state(ex["id"])
        self.assertEqual(st["review_count"], 1)
        self.assertGreater(st["next_review"], date.today().isoformat())
        self.assertIsNone(variants.get(ex["id"]), "a used variant is dropped")
        status, r = self.request("POST", f"/api/exercise/{ex['id']}/check", {
            "files": {"solution.py": "x = 1"}, "kind": "review", "variant": True})
        self.assertEqual(status, 400)

    def test_solving_and_reviewing_updates_the_schedule(self):
        status, r = self.check(self.ex["starter"])
        self.assertEqual(status, 200)
        self.assertNotEqual(r["result"]["status"], "passed")
        status, r = self.check(self.ex["solution"])
        self.assertEqual(r["result"]["status"], "passed", r["result"])
        st = progress.get_state(self.ex["id"])
        self.assertEqual(st["status"], "solved")
        self.assertEqual(st["interval_days"], 1)  # it took two tries
        self.assertIsNotNone(st["stability"])

        # Make it due, then fail and pass a review.
        st["last_review"] = (date.today() - timedelta(days=3)).isoformat()
        st["next_review"] = date.today().isoformat()
        progress.save_state(st)
        self.assertIn(self.ex["id"], [d["id"] for d in progress.due_reviews()])
        self.check(self.ex["starter"], kind="review")
        st = progress.get_state(self.ex["id"])
        self.assertEqual((st["lapses"], st["review_count"]), (1, 1))
        self.check(self.ex["solution"], kind="review")
        st = progress.get_state(self.ex["id"])
        self.assertEqual(st["review_count"], 1)
        self.assertGreater(st["next_review"], date.today().isoformat())


if __name__ == "__main__":
    unittest.main()
