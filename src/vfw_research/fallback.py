"""Idempotent restoration of the last validated vFW configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidatedConfiguration:
    configuration_id: str
    firewall_instance_id: str
    route_id: str
    policy_hash: str


@dataclass(frozen=True)
class FallbackResult:
    restored: ValidatedConfiguration
    previous_configuration_id: str | None
    changed: bool
    reason: str
    recovery_seconds: float


class NoValidatedFallback(RuntimeError):
    pass


class FallbackController:
    def __init__(self) -> None:
        self._last_validated: ValidatedConfiguration | None = None
        self._active: ValidatedConfiguration | None = None

    @property
    def active(self) -> ValidatedConfiguration | None:
        return self._active

    def establish_validated(self, configuration: ValidatedConfiguration) -> None:
        self._last_validated = configuration
        self._active = configuration

    def activate_candidate(self, configuration: ValidatedConfiguration) -> None:
        """Activate a candidate after external invariant validation.

        This does not mark the candidate as the fallback checkpoint. Promotion is
        explicit so a post-commit failure can still restore the prior configuration.
        """
        if self._last_validated is None:
            raise NoValidatedFallback("establish a validated configuration first")
        self._active = configuration

    def promote_active(self) -> None:
        if self._active is None:
            raise NoValidatedFallback("there is no active configuration to promote")
        self._last_validated = self._active

    def fallback(
        self, *, reason: str, detected_at_monotonic: float, restored_at_monotonic: float
    ) -> FallbackResult:
        if self._last_validated is None:
            raise NoValidatedFallback("no validated configuration is available")
        if not reason.strip():
            raise ValueError("fallback reason is required")
        if restored_at_monotonic < detected_at_monotonic:
            raise ValueError("restoration time cannot precede detection time")
        previous_id = self._active.configuration_id if self._active else None
        changed = self._active != self._last_validated
        self._active = self._last_validated
        return FallbackResult(
            restored=self._last_validated,
            previous_configuration_id=previous_id,
            changed=changed,
            reason=reason,
            recovery_seconds=restored_at_monotonic - detected_at_monotonic,
        )

