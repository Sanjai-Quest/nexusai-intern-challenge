import pytest
from escalation_engine import should_escalate

class MockContext:
    def __init__(self, crm_data=None, billing_data=None, ticket_history=None, data_complete=True):
        self.crm_data = crm_data
        self.billing_data = billing_data
        self.ticket_history = ticket_history
        self.data_complete = data_complete

# --- Rule Tests ---

def test_rule1_low_confidence():
    """Rule 1: Escalate if confidence is below 0.65. This ensures the AI doesn't give wrong advice."""
    ctx = MockContext()
    should, reason = should_escalate(ctx, 0.60, 0.0, "billing_issue")
    assert should is True
    assert reason == "low_confidence"

def test_rule2_angry_customer():
    """Rule 2: Escalate if sentiment is very negative. Humans handle frustration better than AI."""
    ctx = MockContext()
    should, reason = should_escalate(ctx, 0.90, -0.7, "billing_issue")
    assert should is True
    assert reason == "angry_customer"

def test_rule3_repeat_complaint():
    """Rule 3: Escalate if the same issue happened 3+ times. Indicates a systemic failure that needs human intervention."""
    history = {
        "last_5_complaints": [
            {"intent": "network_issue"},
            {"intent": "network_issue"},
            {"intent": "network_issue"}
        ]
    }
    ctx = MockContext(ticket_history=history)
    should, reason = should_escalate(ctx, 0.90, 0.0, "network_issue")
    assert should is True
    assert reason == "repeat_complaint"

def test_rule4_service_cancellation():
    """Rule 4: Always escalate cancellations. Churn prevention is high priority and requires human persuasion."""
    ctx = MockContext()
    should, reason = should_escalate(ctx, 0.99, 1.0, "service_cancellation")
    assert should is True
    assert reason == "service_cancellation"

def test_rule5_vip_billing_issue():
    """Rule 5: VIPs with billing issues escalate. We can't afford to annoy high-value customers with automated billing errors."""
    ctx = MockContext(
        crm_data={"vip_status": True},
        billing_data={"overdue": True}
    )
    should, reason = should_escalate(ctx, 0.90, 0.0, "billing_issue")
    assert should is True
    assert reason == "vip_billing_issue"

def test_rule6_incomplete_data_low_conf():
    """Rule 6: If data is missing and confidence isn't high, escalate. Safer than guessing without full context."""
    ctx = MockContext(data_complete=False)
    should, reason = should_escalate(ctx, 0.75, 0.0, "billing_issue")
    assert should is True
    assert reason == "incomplete_data_low_confidence"

# --- Edge Case Tests ---

def test_edge_high_confidence_normal_vip():
    """Edge Case: VIP but billing is NOT overdue. AI should handle it to save human resources."""
    ctx = MockContext(
        crm_data={"vip_status": True},
        billing_data={"overdue": False}
    )
    should, _ = should_escalate(ctx, 0.90, 0.0, "billing_issue")
    assert should is False

def test_edge_boundary_confidence():
    """Edge Case: Confidence is exactly 0.65. Boundary check—should not escalate."""
    ctx = MockContext()
    should, _ = should_escalate(ctx, 0.65, 0.0, "billing_issue")
    assert should is False
