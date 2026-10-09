import tempfile
import unittest
from pathlib import Path
from vfw_research.route_transaction import RouteTransaction


class RouteTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.routes = {"ingress": "source", "egress": "source"}
        self.path = Path(self.temp.name) / "journal"

    def transaction(self, apply=None):
        return RouteTransaction(self.path, apply or self.routes.__setitem__,
                                lambda side, dest: self.routes[side] == dest)

    def test_commit_and_refuse_reuse(self):
        tx = self.transaction()
        tx.commit(lambda: True)
        self.assertEqual(tx.events()[-1]["state"], "COMMITTED")
        with self.assertRaises(ValueError):
            tx.commit(lambda: True)

    def test_second_route_failure_blocks_both(self):
        def apply(side, dest):
            if side == "egress" and dest == "target":
                raise RuntimeError("injected route failure")
            self.routes[side] = dest
        tx = self.transaction(apply)
        with self.assertRaises(RuntimeError):
            tx.commit(lambda: True)
        self.assertEqual(set(self.routes.values()), {"blocked"})

    def test_restart_never_trusts_old_source_state(self):
        tx = self.transaction()
        tx.record("APPLYING", side="ingress", destination="target")
        self.routes["ingress"] = "target"
        self.assertEqual(self.transaction().recover(lambda: False), "BLOCKED")
        self.assertEqual(set(self.routes.values()), {"blocked"})
        self.assertEqual(self.transaction().recover(lambda: True), "RECOVERED")
        self.assertEqual(set(self.routes.values()), {"source"})

    def test_torn_journal_blocks_before_parse(self):
        self.path.mkdir()
        (self.path / "000000.json").write_text('{"sequence":')
        self.assertEqual(self.transaction().recover(lambda: True), "BLOCKED_CORRUPT_JOURNAL")
        self.assertEqual(set(self.routes.values()), {"blocked"})

    def test_source_revalidation_failure_reblocks(self):
        tx = self.transaction()
        tx.record("PREPARED")
        calls = iter([True, True, False])
        with self.assertRaises(RuntimeError):
            tx.recover(lambda: next(calls))
        self.assertEqual(set(self.routes.values()), {"blocked"})

    def test_block_attempts_both_sides_on_error(self):
        attempted = []
        def fail(side, dest):
            attempted.append(side)
            raise RuntimeError("unavailable")
        with self.assertRaisesRegex(RuntimeError, "containment incomplete"):
            self.transaction(fail).block()
        self.assertEqual(attempted, ["ingress", "egress"])

    def test_commit_policy_drift_and_postcheck_failure(self):
        for sequence in ([True, True, False], [True, True, True, False]):
            with tempfile.TemporaryDirectory() as directory:
                validations = iter(sequence)
                tx = RouteTransaction(Path(directory), self.routes.__setitem__,
                                      lambda side, dest: self.routes[side] == dest)
                with self.assertRaises(RuntimeError):
                    tx.commit(lambda: next(validations))
                self.assertEqual(set(self.routes.values()), {"blocked"})
