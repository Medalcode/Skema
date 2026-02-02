from typing import Dict
from skema.core.ports.interfaces import ClassifierPort
from skema.core.domain.models import Requirement, ClassificationResult, ConfidenceScore

class DummyClassifierAdapter(ClassifierPort):
    """
    Adaptador 'Rule-Based' simple.
    Implementa ClassifierPort usando reglas de palabras clave.
    Es un reemplazo directo (Drop-in replacement) para modelos de ML complejos.
    """
    
    # Reglas simples: keyword -> categoría
    RULES: Dict[str, str] = {
        "login": "Authentication",
        "password": "Authentication",
        "signin": "Authentication",
        "pdf": "Reporting",
        "report": "Reporting",
        "export": "Reporting",
        "slow": "Performance",
        "latency": "Performance",
        "db": "Infrastructure",
        "sql": "Infrastructure",
        "server": "Infrastructure"
    }

    def classify(self, req: Requirement) -> ClassificationResult:
        text = req.text.lower()
        category = "General"
        confidence_value = 0.30 # Default low confidence

        # Lógica de inferencia heurística
        for keyword, mapped_category in self.RULES.items():
            if keyword in text:
                category = mapped_category
                confidence_value = 0.90 # High confidence on keyword match
                break 

        return ClassificationResult(
            requirement_id=req.id,
            category=category,
            confidence=ConfidenceScore(confidence_value),
            model_version="DummyRules-v2"
        )
