"""Bernie facade for the diary confirm-affordance gate.

Re-exports from the diary domain; callers outside the diary domain should
import confirm-gate types through ``app.services.bernie`` (or this module),
never from ``app.services.diary.confirm_gate`` directly.
"""

from app.services.diary.confirm_gate import (
    ConfirmAffordanceDecision,
    ConfirmAffordanceGate,
    evaluate_confirm_affordance,
)

__all__ = [
    "ConfirmAffordanceDecision",
    "ConfirmAffordanceGate",
    "evaluate_confirm_affordance",
]
