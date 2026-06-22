import asyncio
import logging
from functools import lru_cache

from skema.core.interfaces import ClassifierPort
from skema.core.models import Requirement, ClassificationResult, ConfidenceScore

logger = logging.getLogger(__name__)


class DummyClassifierAdapter(ClassifierPort):
    RULES: dict[str, str] = {
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

    async def classify(self, req: Requirement) -> ClassificationResult:
        text = req.text.lower()
        category = "General"
        confidence_value = 0.30

        for keyword, mapped_category in self.RULES.items():
            if keyword in text:
                category = mapped_category
                confidence_value = 0.90
                break

        return ClassificationResult(
            requirement_id=req.id,
            category=category,
            confidence=ConfidenceScore(confidence_value),
            model_version="DummyRules-v2"
        )


class HybridClassifierAdapter(ClassifierPort):
    CATEGORIES = [
        "Bug", "Feature", "Documentation", "Infrastructure",
        "Performance", "Security", "General"
    ]

    KEYWORD_RULES: dict[str, list[str]] = {
        "Bug": ["bug", "error", "crash", "broken", "not working", "issue", "defect", "fail"],
        "Feature": ["add", "implement", "create", "new feature", "enhancement", "support", "allow"],
        "Documentation": ["doc", "readme", "guide", "manual", "wiki", "tutorial", "help"],
        "Infrastructure": ["deploy", "devops", "ci/cd", "docker", "kubernetes", "infra", "server", "db"],
        "Performance": ["slow", "latency", "speed", "optimize", "lag", "throughput", "memory"],
        "Security": ["security", "vulnerability", "cve", "auth", "token", "password", "encrypt", "exploit"],
    }

    SEMANTIC_TEMPLATES: dict[str, list[str]] = {
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
        "Documentation": [
            "update the api documentation",
            "write a guide for new users",
            "add comments to the codebase",
            "create a readme file"
        ],
        "Infrastructure": [
            "set up a new server environment",
            "configure the deployment pipeline",
            "update infrastructure as code",
            "scale the application horizontally"
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
        self.embedder = None
        self.semantic_enabled = False
        self._template_embeddings: dict[str, any] = {}

    @classmethod
    def create(cls) -> 'HybridClassifierAdapter':
        instance = cls()
        instance._load_model()
        return instance

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.semantic_enabled = True
            self._precompute_template_embeddings()
            logger.info("Embeddings model loaded successfully")
        except Exception as e:
            logger.warning(f"Embeddings not available, using keyword-only mode. Error: {e}")

    def _precompute_template_embeddings(self):
        for category, templates in self.SEMANTIC_TEMPLATES.items():
            self._template_embeddings[category] = self.embedder.encode(
                templates, convert_to_tensor=True
            )

    async def classify(self, req: Requirement) -> ClassificationResult:
        text = req.text.lower()

        keyword_result = self._classify_by_keywords(text)
        if keyword_result[1] > 0.85:
            return ClassificationResult(
                requirement_id=req.id,
                category=keyword_result[0],
                confidence=ConfidenceScore(keyword_result[1]),
                model_version="HybridClassifier-v1"
            )

        if self.semantic_enabled:
            semantic_result = await asyncio.to_thread(self._classify_by_embeddings, req.text)
            return ClassificationResult(
                requirement_id=req.id,
                category=semantic_result[0],
                confidence=ConfidenceScore(semantic_result[1]),
                model_version="HybridClassifier-v1-Semantic"
            )

        return ClassificationResult(
            requirement_id=req.id,
            category=keyword_result[0] if keyword_result[1] > 0.3 else "General",
            confidence=ConfidenceScore(max(keyword_result[1], 0.3)),
            model_version="HybridClassifier-v1"
        )

    def _classify_by_keywords(self, text: str) -> tuple[str, float]:
        scores = {cat: 0 for cat in self.CATEGORIES}

        for category, keywords in self.KEYWORD_RULES.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1

        if not any(scores.values()):
            return ("General", 0.3)

        best_category = max(scores, key=scores.get)
        match_count = scores[best_category]
        confidence = min(0.75 + (match_count * 0.1), 0.95)

        return (best_category, confidence)

    def _classify_by_embeddings(self, text: str) -> tuple[str, float]:
        try:
            from sentence_transformers import util

            text_embedding = self.embedder.encode(text, convert_to_tensor=True)

            max_similarity = 0.0
            best_category = "General"

            for category, template_embeddings in self._template_embeddings.items():
                similarities = util.pytorch_cos_sim(text_embedding, template_embeddings)[0]
                avg_similarity = float(similarities.mean())

                if avg_similarity > max_similarity:
                    max_similarity = avg_similarity
                    best_category = category

            confidence = max(0.4, min(max_similarity, 0.9))
            return (best_category, confidence)

        except Exception as e:
            logger.error(f"Embedding error: {e}, falling back to keywords")
            return ("General", 0.3)
