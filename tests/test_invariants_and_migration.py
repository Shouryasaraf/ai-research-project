import unittest

from vfw_research.invariants import validate_security_invariants
from vfw_research.migration import InvalidTransition, MigrationStateMachine
from vfw_research.models import MigrationState, SecuritySnapshot


def safe_snapshot(**changes):
    values = dict(
        source_policy_hash="p1",
        target_policy_hash="p1",
        expected_policy_hash="p1",
        traffic_path_enforced=True,
        default_deny_enabled=True,
        target_allowed=True,
        target_healthy=True,
        capacity_sufficient=True,
        state_mismatch_fraction=0,
        maximum_state_mismatch_fraction=0.01,
        audit_available=True,
    )
    values.update(changes)
    return SecuritySnapshot(**values)


class InvariantAndMigrationTests(unittest.TestCase):
    def test_safe_snapshot_has_no_violations(self):
        self.assertEqual(validate_security_invariants(safe_snapshot()), ())

    def test_policy_and_state_failures_are_reported(self):
        violations = validate_security_invariants(
            safe_snapshot(target_policy_hash="wrong", state_mismatch_fraction=0.2)
        )
        self.assertIn("target_policy_mismatch", violations)
        self.assertIn("state_mismatch_above_tolerance", violations)

    def test_valid_warm_migration_path(self):
        machine = MigrationStateMachine()
        for target in (
            MigrationState.PREWARM,
            MigrationState.SYNC,
            MigrationState.VALIDATE,
            MigrationState.COMMIT,
            MigrationState.DRAIN,
            MigrationState.COMPLETE,
        ):
            machine.transition(target, "test progression")
        self.assertEqual(machine.state, MigrationState.COMPLETE)
        self.assertEqual(len(machine.history), 6)

    def test_commit_cannot_skip_validation(self):
        machine = MigrationStateMachine()
        with self.assertRaises(InvalidTransition):
            machine.transition(MigrationState.COMMIT, "unsafe skip")


if __name__ == "__main__":
    unittest.main()

