import pytest
from skema.adapters.processor import RequirementProcessorSkill


def test_requirement_processor_basic():
    processor = RequirementProcessorSkill()
    raw_text = "  ¡El sistema DEBE permitir Login! @2026 #security  "
    processed = processor.process(raw_text, clean=True, lowercase=True)
    
    assert "login" in processed
    assert "!" not in processed
    assert "@" not in processed
    assert "#" not in processed
    assert processed == "el sistema debe permitir login 2026 security"


def test_requirement_processor_without_cleaning():
    processor = RequirementProcessorSkill()
    raw_text = "System Error: #500!"
    processed = processor.process(raw_text, clean=False, lowercase=True)
    assert processed == "system error: #500!"


def test_requirement_processor_without_lowercase():
    processor = RequirementProcessorSkill()
    raw_text = "System Error"
    processed = processor.process(raw_text, clean=False, lowercase=False)
    assert processed == "System Error"


def test_requirement_processor_accents_preservation():
    processor = RequirementProcessorSkill()
    raw_text = "El envío de información debe ser ágil y seguro con contraseña."
    processed = processor.process(raw_text, clean=True, lowercase=True)
    assert "envío" in processed
    assert "información" in processed
    assert "ágil" in processed
    assert "contraseña" in processed
