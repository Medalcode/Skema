import unittest
from datetime import datetime
from skema.core.domain.models import Requirement, ConfidenceScore

class TestDomainModels(unittest.TestCase):
    
    def test_confidence_score_invariants(self):
        """Value Object integrity checks"""
        # Valid range
        self.assertEqual(ConfidenceScore(0.0).value, 0.0)
        self.assertEqual(ConfidenceScore(1.0).value, 1.0)
        self.assertEqual(ConfidenceScore(0.5).value, 0.5)

        # Invalid range (Too high)
        with self.assertRaises(ValueError):
            ConfidenceScore(1.01)
        
        # Invalid range (Negative)
        with self.assertRaises(ValueError):
            ConfidenceScore(-0.01)

    def test_requirement_creation(self):
        """Entity factory method validation"""
        req = Requirement.create("  Valid Text  ")
        
        # Check stripping/cleaning logic if any (currently none strict, but good to test)
        self.assertEqual(req.text, "  Valid Text  ")
        self.assertIsInstance(req.timestamp, datetime)
        self.assertIsNotNone(req.id) # UUID generated

    def test_requirement_empty_text(self):
        """Invariant: Requirement cannot be empty"""
        with self.assertRaises(ValueError):
            Requirement.create("")
        
        with self.assertRaises(ValueError):
            Requirement.create("   ") # Whitespace only
