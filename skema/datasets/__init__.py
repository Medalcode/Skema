"""
Dataset generator - crea tickets sintéticos realistas para demostración.
"""

import random
from typing import List

from skema.core.models import Requirement

# Plantillas de tickets realistas por categoría
TICKET_TEMPLATES = {
    "Bug": [
        "The login page throws a 500 error when submitting with special characters",
        "Application crashes on Safari when uploading large files",
        "Database connection timeout after 5 minutes of inactivity",
        "User profile page shows 404 error for some accounts",
        "Email notifications are not being sent after form submission",
        "The export to PDF button does not work on Chrome",
        "Memory leak detected in the background worker process",
        "API returns inconsistent data for concurrent requests",
        "Dashboard graphs not rendering on Firefox",
        "Payment webhook failing with status 422",
    ],
    "Feature": [
        "Implement two-factor authentication for all users",
        "Add bulk user import from CSV files",
        "Create API endpoint for real-time notifications",
        "Enable data export in Excel format",
        "Implement role-based access control (RBAC)",
        "Add multi-language support for the UI",
        "Create dashboard widget for custom analytics",
        "Implement webhook support for integrations",
        "Add advanced search filters with saved searches",
        "Support OAuth2 authentication providers",
    ],
    "Documentation": [
        "Update README with new setup instructions",
        "Create API documentation using OpenAPI/Swagger",
        "Write deployment guide for Kubernetes",
        "Add troubleshooting section to user manual",
        "Document database schema and entity relationships",
        "Create architecture decision record (ADR)",
        "Write integration guide for Jira",
        "Update configuration file examples",
        "Document monitoring and alerting setup",
        "Create migration guide from v1 to v2",
    ],
    "Infrastructure": [
        "Migrate database from MySQL to PostgreSQL",
        "Setup automated backup system with 30-day retention",
        "Implement Docker Compose for local development",
        "Configure CI/CD pipeline with GitHub Actions",
        "Deploy Redis cache cluster for session storage",
        "Setup monitoring with Prometheus and Grafana",
        "Implement load balancing with Nginx",
        "Configure SSL certificates with Let's Encrypt",
        "Setup log aggregation with ELK stack",
        "Create disaster recovery plan and procedures",
    ],
    "Performance": [
        "Database queries are running 10x slower than expected",
        "API response time degraded after latest deployment",
        "Memory usage grew from 500MB to 2GB in production",
        "Optimize image loading on mobile devices",
        "Reduce homepage load time from 8s to under 3s",
        "Implement query caching to improve performance",
        "Reduce bundle size by removing unused dependencies",
        "Optimize database indexes for common queries",
        "Implement pagination for large data sets",
        "Profile and optimize the report generation",
    ],
    "Security": [
        "SQL injection vulnerability in search functionality",
        "Implement rate limiting to prevent brute force attacks",
        "XSS vulnerability in comment section",
        "Sensitive data exposed in error messages",
        "Implement request signing for API calls",
        "Add input validation to all endpoints",
        "Encrypt passwords using bcrypt with salt",
        "Implement CSRF token validation",
        "Audit user permissions and remove unnecessary access",
        "Add security headers (CSP, X-Frame-Options, etc)",
    ],
    "General": [
        "Improve code quality and maintainability",
        "Refactor legacy module X",
        "Update dependencies to latest versions",
        "Add metrics and monitoring",
        "Improve error handling throughout",
        "Implement automated testing",
        "Add code reviews to workflow",
        "Document non-obvious code sections",
        "Standardize naming conventions",
        "Remove technical debt in authentication",
    ]
}


def generate_synthetic_tickets(count: int = 500) -> list[Requirement]:
    """
    Genera N tickets sintéticos realistas.
    Distribución aproximada por categoría:
    - Bug: 30%
    - Feature: 25%
    - Documentation: 10%
    - Infrastructure: 15%
    - Performance: 10%
    - Security: 8%
    - General: 2%
    """
    tickets = []

    # Distribución de categorías
    distribution = {
        "Bug": int(count * 0.30),
        "Feature": int(count * 0.25),
        "Documentation": int(count * 0.10),
        "Infrastructure": int(count * 0.15),
        "Performance": int(count * 0.10),
        "Security": int(count * 0.08),
        "General": int(count * 0.02),
    }

    for category, num_tickets in distribution.items():
        templates = TICKET_TEMPLATES[category]
        for _ in range(num_tickets):
            text = random.choice(templates)
            # Agrega variación minor
            if random.random() > 0.7:
                text += " " + random.choice([
                    "[Urgent]",
                    "[Blocker]",
                    "[P0]",
                    "[Customer Report]",
                    ""
                ])

            ticket = Requirement.create(
                text=text,
                metadata={
                    "source": random.choice(["github", "jira", "email", "slack"]),
                    "priority": random.choice(["low", "medium", "high"]),
                }
            )
            tickets.append(ticket)

    # Mezcla
    random.shuffle(tickets)

    return tickets[:count]


if __name__ == "__main__":
    # Script para generar y ver tickets de ejemplo
    tickets = generate_synthetic_tickets(10)
    for ticket in tickets:
        print(f"✓ {ticket.text[:60]}...")
