"""
Dashboard - UI mínima usando Jinja2 templates.
"""

import os

from jinja2 import Environment, FileSystemLoader

# Configuración de templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def get_template(name: str):
    """Carga un template por nombre"""
    return env.get_template(name)
