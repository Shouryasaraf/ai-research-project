import unittest

from vfw_research.fallback import (
    FallbackController,
    NoValidatedFallback,
    ValidatedConfiguration,
)


class FallbackTests(unittest.TestCase):
    def setUp(self):
        self.source = ValidatedConfiguration("source-v1", "fw-source", "route-source", "p1")
        self.target = ValidatedConfiguration("target-v1", "fw-target", "route-target", "p1")

    def test_fallback_restores_last_validated_configuration(self):
        controller = FallbackController()
        controller.establish_validated(self.source)
        controller.activate_candidate(self.target)
        result = controller.fallback(
            reason="post-commit health failure",
            detected_at_monotonic=10,
            restored_at_monotonic=10.25,
        )
        self.assertEqual(controller.active, self.source)
        self.assertTrue(result.changed)
        self.assertEqual(result.recovery_seconds, 0.25)

    def test_repeated_fallback_is_idempotent(self):
        controller = FallbackController()
        controller.establish_validated(self.source)
        result = controller.fallback(
            reason="repeated signal", detected_at_monotonic=11, restored_at_monotonic=11
        )
        self.assertFalse(result.changed)
        self.assertEqual(controller.active, self.source)

    def test_fallback_without_checkpoint_fails_closed(self):
        controller = FallbackController()
        with self.assertRaises(NoValidatedFallback):
            controller.fallback(reason="failure", detected_at_monotonic=1, restored_at_monotonic=2)


if __name__ == "__main__":
    unittest.main()

