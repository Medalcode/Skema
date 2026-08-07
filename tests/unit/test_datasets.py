import pytest
from skema.core.models import Requirement
from skema.datasets import generate_synthetic_tickets, TICKET_TEMPLATES


def test_generate_synthetic_tickets_count():
    count = 20
    tickets = generate_synthetic_tickets(count=count)
    
    assert len(tickets) == count
    for ticket in tickets:
        assert isinstance(ticket, Requirement)
        assert len(ticket.text) > 0
        assert ticket.source in ["github", "jira", "email", "slack"]
        assert "priority" in ticket.context


def test_ticket_templates_not_empty():
    assert len(TICKET_TEMPLATES) >= 7
    for category, templates in TICKET_TEMPLATES.items():
        assert len(templates) > 0
