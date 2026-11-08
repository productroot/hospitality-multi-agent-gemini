from typing import Any, Dict, List


TOOL_DECLARATIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "name": "check_room_availability",
        "description": "Check live hotel room availability, rate plans (flexible vs non-refundable), and direct booking perks.",
        "parameters": {
            "type": "object",
            "properties": {
                "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                "adults": {"type": "integer", "description": "Number of adult guests"},
                "children_ages": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Ages of children for age-band pricing calculation",
                },
            },
            "required": ["check_in", "check_out", "adults"],
        },
    },
    {
        "type": "function",
        "name": "modify_reservation",
        "description": "Modify dates or room category of an existing guest reservation (requires permission gate confirmation).",
        "parameters": {
            "type": "object",
            "properties": {
                "reservation_id": {"type": "string"},
                "new_check_out": {"type": "string"},
                "upgrade_room_type": {"type": "string"},
            },
            "required": ["reservation_id"],
        },
    },
    {
        "type": "function",
        "name": "create_service_request",
        "description": "Dispatch a housekeeping, room service, or maintenance task to hotel staff.",
        "parameters": {
            "type": "object",
            "properties": {
                "room_number": {"type": "string"},
                "department": {
                    "type": "string",
                    "enum": ["housekeeping", "maintenance", "concierge", "spa"],
                },
                "request_summary": {"type": "string"},
            },
            "required": ["room_number", "department", "request_summary"],
        },
    },
    {
        "type": "function",
        "name": "issue_compensation_voucher",
        "description": "Issue a direct-booking spa or dining voucher to resolve a guest issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "reservation_id": {"type": "string"},
                "amount_eur": {"type": "number"},
                "reason": {"type": "string"},
            },
            "required": ["reservation_id", "amount_eur", "reason"],
        },
    },
]


def execute_hospitality_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Reference PMS & Hotel Operations adapter."""
    if name == "check_room_availability":
        children = arguments.get("children_ages", [])
        return {
            "status": "available",
            "check_in": arguments["check_in"],
            "check_out": arguments["check_out"],
            "adults": arguments["adults"],
            "children_count": len(children),
            "offers": [
                {
                    "room_type": "Deluxe Panorama Suite",
                    "flexible_rate_eur": 240,
                    "non_refundable_rate_eur": 205,
                    "direct_booking_perks": [
                        "Complimentary thermal spa access",
                        "Late check-out until 14:00",
                        "Welcome artisan chocolate & wine",
                    ],
                },
                {
                    "room_type": "Superior King Room",
                    "flexible_rate_eur": 165,
                    "non_refundable_rate_eur": 142,
                    "direct_booking_perks": ["Complimentary parking", "15% Spa discount"],
                },
            ],
        }
    if name == "create_service_request":
        return {
            "ticket_id": "OPS-2026-8841",
            "status": "dispatched",
            "department": arguments["department"],
            "room_number": arguments["room_number"],
        }
    if name == "modify_reservation":
        return {
            "reservation_id": arguments["reservation_id"],
            "status": "modified",
            "new_check_out": arguments.get("new_check_out"),
        }
    if name == "issue_compensation_voucher":
        return {
            "voucher_code": "DIRECT-CARE-2026",
            "amount_eur": arguments["amount_eur"],
            "status": "issued",
        }
    return {"error": f"Unknown tool: {name}"}
