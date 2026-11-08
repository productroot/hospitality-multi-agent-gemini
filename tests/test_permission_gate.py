from agents.permission_gate import PermissionGate


def test_read_only_tool_auto_allowed():
    gate = PermissionGate(max_auto_approve_eur=150.0)
    decision = gate.evaluate("check_room_availability", {"adults": 2})
    assert decision.allowed is True
    assert decision.requires_human_approval is False


def test_voucher_within_policy_allowed():
    gate = PermissionGate(max_auto_approve_eur=150.0)
    decision = gate.evaluate("issue_compensation_voucher", {"amount_eur": 100.0})
    assert decision.allowed is True
    assert decision.requires_human_approval is False


def test_voucher_above_policy_blocked_without_human_approval():
    gate = PermissionGate(max_auto_approve_eur=150.0)
    decision = gate.evaluate("issue_compensation_voucher", {"amount_eur": 350.0})
    assert decision.allowed is False
    assert decision.requires_human_approval is True

    approved_decision = gate.evaluate(
        "issue_compensation_voucher", {"amount_eur": 350.0}, human_approved=True
    )
    assert approved_decision.allowed is True


def test_reservation_modification_requires_confirmation():
    gate = PermissionGate()
    decision = gate.evaluate("modify_reservation", {"reservation_id": "RES-99"})
    assert decision.allowed is False
    assert decision.requires_human_approval is True
