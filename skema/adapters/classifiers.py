from typing import Dict, List, Tuple
from abc import abstractmethod
from skema.core.interfaces import ClassifierPort
from skema.core.models import Requirement, ClassificationResult, ConfidenceScore
import numpy as np

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


class HybridClassifierAdapter(ClassifierPort):
    """
    Clasificador Híbrido: Reglas + Embeddings + Confidence Scoring.
    
    Estrategia:
    1. Aplica reglas keyword-based (rápido, determinístico)
    2. Si confianza baja, usa embeddings para búsqueda semántica
    3. Retorna score de confianza real
    4. Si no es confiable, requiere revisión humana
    
    Modelo de categorías:
    - Bug: Defectos, errores, crashes
    - Feature: Nuevas funcionalidades, mejoras
    - Documentation: Docs, wikis, manuales
    - Infrastructure: DevOps, deployment, CI/CD
    - Performance: Optimización, escalabilidad
    - Security: Vulnerabilidades, acceso
    - General: Otros
    """
    
    # Categorías disponibles
    CATEGORIES = [
        "Bug",
        "Feature", 
        "Documentation",
        "Infrastructure",
        "Performance",
        "Security",
        "General"
    ]
    
    # Palabras clave por categoría (confidence > 0.85)
    KEYWORD_RULES: Dict[str, List[str]] = {
        "Bug": ["bug", "error", "crash", "broken", "not working", "issue", "defect", "fail"],
        "Feature": ["add", "implement", "create", "new feature", "enhancement", "support", "allow"],
        "Documentation": ["doc", "readme", "guide", "manual", "wiki", "tutorial", "help"],
        "Infrastructure": ["deploy", "devops", "ci/cd", "docker", "kubernetes", "infra", "server", "db"],
        "Performance": ["slow", "latency", "speed", "optimize", "lag", "throughput", "memory"],
        "Security": ["security", "vulnerability", "cve", "auth", "token", "password", "encrypt", "exploit"],
    }
    
    # Términos semánticamente similares (descritos por ejemplos)
    SEMANTIC_TEMPLATES: Dict[str, List[str]] = {
        "Bug": [
            "the application crashes when I click submit",
            "data is not saving correctly",
            "unexpected error on page load",
            "function returns wrong value"
        ],
        "Feature": [
            "we need a way to export to excel",
            "please add user roles support",
            "implement batch processing",
            "allow filtering by date range"
        ],
        "Performance": [
            "queries are running too slowly",
            "application takes forever to load",
            "memory usage is too high",
            "response time needs improvement"
        ],
        "Security": [
            "sensitive data should be encrypted",
            "we need two-factor authentication",
            "prevent unauthorized access",
            "implement rate limiting"
        ]
    }
    
    def __init__(self):
        """Inicializa embeddings (lazy loading si es posible)"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast
            self.semantic_enabled = True
        except Exception:
            print("⚠️  Embeddings not available, using keyword-only mode")
            self.embedder = None
            self.semantic_enabled = False
    
    def classify(self, req: Requirement) -> ClassificationResult:
        """
        Ejecuta clasificación híbrida con confianza real.
        """
        text = req.text.lower()
        
        # 1. Intenta keywords primero
        keyword_result = self._classify_by_keywords(text)
        if keyword_result[1] > 0.85:
            return ClassificationResult(
                requirement_id=req.id,
                category=keyword_result[0],
                confidence=ConfidenceScore(keyword_result[1]),
                model_version="HybridClassifier-v1"
            )
        
        # 2. Si confianza baja, usa embeddings
        if self.semantic_enabled:
            semantic_result = self._classify_by_embeddings(req.text)
            return ClassificationResult(
                requirement_id=req.id,
                category=semantic_result[0],
                confidence=ConfidenceScore(semantic_result[1]),
                model_version="HybridClassifier-v1-Semantic"
            )
        
        # 3. Fallback a keyword result o General
        category = keyword_result[0] if keyword_result[1] > 0.3 else "General"
        confidence = max(keyword_result[1], 0.3)
        
        return ClassificationResult(
            requirement_id=req.id,
            category=category,
            confidence=ConfidenceScore(confidence),
            model_version="HybridClassifier-v1"
        )
    
    def _classify_by_keywords(self, text: str) -> Tuple[str, float]:
        """
        Busca palabras clave en el texto.
        Retorna (categoría, confianza)
        """
        scores = {cat: 0 for cat in self.CATEGORIES}
        
        for category, keywords in self.KEYWORD_RULES.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        if not any(scores.values()):
            return ("General", 0.3)
        
        best_category = max(scores, key=scores.get)
        # Normaliza confianza: 1 match=0.75, 2=0.85, 3+=0.95
        match_count = scores[best_category]
        confidence = min(0.75 + (match_count * 0.1), 0.95)
        
        return (best_category, confidence)
    
    def _classify_by_embeddings(self, text: str) -> Tuple[str, float]:
        """
        Usa embeddings para encontrar la categoría más similar.
        Retorna (categoría, confianza)
        """
        try:
            from sentence_transformers import util
            # Embeding del texto del usuario
            text_embedding = self.embedder.encode(text, convert_to_tensor=True)
            
            max_similarity = 0.0
            best_category = "General"
            
            # Compara contra cada categoría
            for category, templates in self.SEMANTIC_TEMPLATES.items():
                template_embeddings = self.embedder.encode(templates, convert_to_tensor=True)
                similarities = util.pytorch_cos_sim(text_embedding, template_embeddings)[0]
                avg_similarity = float(similarities.mean())
                
                if avg_similarity > max_similarity:
                    max_similarity = avg_similarity
                    best_category = category
            
            # Usa similitud como confianza (0.4 a 0.9)
            confidence = max(0.4, min(max_similarity, 0.9))
            return (best_category, confidence)
            
        except Exception as e:
            print(f"❌ Embedding error: {e}, falling back to keywords")
            return ("General", 0.3)
