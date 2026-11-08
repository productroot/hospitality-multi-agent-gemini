from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PermissionDecision:
    allowed: bool
    requires_human_approval: bool
    reason: str


class PermissionGate:
    """
    Deterministic product-level safety boundary between AI agent tool calls
    and hospitality PMS / billing mutations.
    """

    READ_ONLY_TOOLS = {
        "check_room_availability",
        "get_hotel_amenities",
        "search_local_attractions",
    }

    MUTATING_TOOLS = {
        "create_service_request",
        "modify_reservation",
        "issue_compensation_voucher",
    }

    def __init__(self, max_auto_approve_eur: float = 150.0):
        self.max_auto_approve_eur = max_auto_approve_eur

    def evaluate(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        human_approved: bool = False,
    ) -> PermissionDecision:
        if tool_name in self.READ_ONLY_TOOLS:
            return PermissionDecision(
                allowed=True,
                requires_human_approval=False,
                reason="Read-only tool call permitted automatically.",
            )

        if tool_name == "create_service_request":
            return PermissionDecision(
                allowed=True,
                requires_human_approval=False,
                reason="Operational housekeeping/maintenance ticket creation is safe.",
            )

        if tool_name == "issue_compensation_voucher":
            amount = float(arguments.get("amount_eur", 0.0))
            if amount <= self.max_auto_approve_eur or human_approved:
                return PermissionDecision(
                    allowed=True,
                    requires_human_approval=False,
                    reason=f"Voucher amount ({amount} EUR) within policy or human-approved.",
                )
            return PermissionDecision(
                allowed=False,
                requires_human_approval=True,
                reason=(
                    f"Voucher of {amount} EUR exceeds autonomous limit "
                    f"({self.max_auto_approve_eur} EUR). Human manager approval required."
                ),
            )

        if tool_name == "modify_reservation":
            if human_approved:
                return PermissionDecision(
                    allowed=True,
                    requires_human_approval=False,
                    reason="Reservation modification confirmed by guest/operator token.",
                )
            return PermissionDecision(
                allowed=False,
                requires_human_approval=True,
                reason="Reservation modifications require explicit guest/operator confirmation.",
            )

        return PermissionDecision(
            allowed=False,
            requires_human_approval=True,
            reason=f"Unrecognized tool '{tool_name}' blocked by default policy.",
        )
