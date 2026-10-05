import time
import unittest
from unittest import mock

import server
from pytrainer import ai, db, llm_bridge, runner

USE = """
from pytrainer_llm import llm, embed
print(llm("What is RAG?"))
print(llm([{"role": "user", "content": "hi"}], system="Be brief."))
print(len(embed(["a cat", "a dog"])), len(embed(["x"])[0]))
"""


class BridgeTests(unittest.TestCase):
    def test_calls_reach_the_model_and_are_logged(self):
        seen = []

        def model(prompt, system):
            seen.append((prompt, system))
            return "reply to " + prompt

        r = runner.run_code({"solution.py": USE}, llm=model)
        self.assertEqual(r["stdout"].splitlines(), ["reply to What is RAG?", "reply to user: hi", "2 256"])
        self.assertEqual(seen[0][1], llm_bridge.DEFAULT_SYSTEM)
        self.assertEqual(seen[1], ("user: hi", "Be brief."))
        self.assertEqual([c["error"] for c in r["llm_calls"]], [None, None])

    def test_calls_are_capped_per_run(self):
        code = ("from pytrainer_llm import llm\n"
                f"for i in range({llm_bridge.BUDGET + 2}):\n"
                "    try:\n        llm(f'q{i}')\n    except RuntimeError as e:\n        print('refused')\n")
        r = runner.run_code({"solution.py": code}, llm=lambda p, s: "ok")
        self.assertEqual(r["stdout"].count("refused"), 2)
        self.assertEqual(sum(1 for c in r["llm_calls"] if not c["error"]), llm_bridge.BUDGET)

    def test_model_errors_reach_the_code(self):
        def broken(prompt, system):
            raise ai.AIError("CLI not found")
        code = "from pytrainer_llm import llm\ntry:\n    llm('x')\nexcept RuntimeError as e:\n    print('caught', e)\n"
        r = runner.run_code({"solution.py": code}, llm=broken)
        self.assertIn("caught AIError: CLI not found", r["stdout"])

    def test_waiting_on_the_model_does_not_use_up_the_time_limit(self):
        def slow(prompt, system):
            time.sleep(2.5)
            return "late"
        r = runner.run_code({"solution.py": "from pytrainer_llm import llm\nprint(llm('x'))"}, llm=slow, timeout=2)
        self.assertFalse(r["timed_out"])
        self.assertEqual(r["stdout"], "late\n")

    def test_without_the_option_there_is_no_helper(self):
        r = runner.run_code({"solution.py": "import pytrainer_llm"})
        self.assertIn("ModuleNotFoundError", r["stderr"])
        self.assertNotIn("llm_calls", r)


class OptInTests(unittest.TestCase):
    def setUp(self):
        from pytrainer import content
        self.ex = next(e for e in content.load()["exercises"].values() if e.get("mode", "function") == "function")

    def test_needs_an_ai_connection(self):
        db.set_setting("ai", {"provider": "none", "model": ""})
        with self.assertRaises(server.ApiError):
            server.api_run(self.ex["id"], {"files": {"solution.py": "print(1)"}, "real_llm": True})

    def test_run_with_real_model_calls(self):
        db.set_setting("ai", {"provider": "claude", "model": ""})
        try:
            with mock.patch.object(ai, "complete", return_value="Paris") as call:
                r = server.api_run(self.ex["id"], {"files": {"solution.py": "from pytrainer_llm import llm\nprint(llm('Capital of France?'))"},
                                                   "real_llm": True})
            self.assertEqual(r["stdout"], "Paris\n")
            self.assertEqual(call.call_args.args[1], "Capital of France?")
            plain = server.api_run(self.ex["id"], {"files": {"solution.py": "print(2)"}})
            self.assertNotIn("llm_calls", plain)
        finally:
            db.set_setting("ai", {"provider": "none", "model": ""})


if __name__ == "__main__":
    unittest.main()
