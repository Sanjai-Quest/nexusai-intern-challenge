def should_escalate(context, confidence_score: float, sentiment_score: float, intent: str) -> tuple[bool, str]:
    """
    Determines if a customer interaction should be escalated to a human agent.
    Returns: (should_escalate: bool, reason: str)
    """
    
    # Rule 4: intent is "service_cancellation" → always escalate, no exceptions
    if intent == "service_cancellation":
        return True, "service_cancellation"

    # Rule 1: confidence below 0.65 → escalate, reason: "low_confidence"
    if confidence_score < 0.65:
        return True, "low_confidence"

    # Rule 2: sentiment below -0.6 → escalate, reason: "angry_customer"
    if sentiment_score < -0.6:
        return True, "angry_customer"

    # Rule 3: same intent appears 3 or more times in ticket history → escalate, reason: "repeat_complaint"
    if context.ticket_history and "last_5_complaints" in context.ticket_history:
        complaints = context.ticket_history["last_5_complaints"]
        repeat_count = sum(1 for c in complaints if c.get("intent") == intent)
        if repeat_count >= 3:
            return True, "repeat_complaint"

    # Rule 5: customer is VIP AND billing is overdue → escalate
    if context.crm_data and context.crm_data.get("vip_status"):
        if context.billing_data and context.billing_data.get("overdue"):
            return True, "vip_billing_issue"

    # Rule 6: data_complete is False AND confidence is below 0.80 → escalate
    if not context.data_complete and confidence_score < 0.80:
        return True, "incomplete_data_low_confidence"

    return False, "auto_resolve"
