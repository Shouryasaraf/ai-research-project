"""Validated migration state machine."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import MigrationState


class InvalidTransition(ValueError):
    """Raised when the orchestrator attempts an undefined transition."""


_ALLOWED: dict[MigrationState, frozenset[MigrationState]] = {
    MigrationState.OBSERVE: frozenset(
        {MigrationState.WAIT, MigrationState.PREWARM, MigrationState.ABORT, MigrationState.FALLBACK}
    ),
    MigrationState.WAIT: frozenset(
        {MigrationState.OBSERVE, MigrationState.PREWARM, MigrationState.ABORT, MigrationState.FALLBACK}
    ),
    MigrationState.PREWARM: frozenset(
        {MigrationState.SYNC, MigrationState.WAIT, MigrationState.ABORT, MigrationState.FALLBACK}
    ),
    MigrationState.SYNC: frozenset(
        {MigrationState.VALIDATE, MigrationState.PREWARM, MigrationState.ABORT, MigrationState.FALLBACK}
    ),
    MigrationState.VALIDATE: frozenset(
        {MigrationState.COMMIT, MigrationState.SYNC, MigrationState.ABORT, MigrationState.FALLBACK}
    ),
    MigrationState.COMMIT: frozenset({MigrationState.DRAIN, MigrationState.FALLBACK}),
    MigrationState.DRAIN: frozenset({MigrationState.COMPLETE, MigrationState.FALLBACK}),
    MigrationState.COMPLETE: frozenset({MigrationState.OBSERVE}),
    MigrationState.ABORT: frozenset({MigrationState.OBSERVE}),
    MigrationState.FALLBACK: frozenset({MigrationState.OBSERVE}),
}


@dataclass
class MigrationStateMachine:
    state: MigrationState = MigrationState.OBSERVE
    history: list[tuple[MigrationState, MigrationState, str]] = field(default_factory=list)

    def transition(self, target: MigrationState, reason: str) -> None:
        if target not in _ALLOWED[self.state]:
            raise InvalidTransition(f"invalid migration transition: {self.state.value} -> {target.value}")
        if not reason.strip():
            raise ValueError("transition reason is required")
        previous = self.state
        self.state = target
        self.history.append((previous, target, reason))

