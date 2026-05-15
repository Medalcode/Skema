import re
from skema.core.interfaces import ProcessorPort

class RequirementProcessorSkill(ProcessorPort):
    """
    Super-Skill: Procesa requerimientos de forma paramétrica.
    Fusión de Preprocessor y Formatter.
    """
    
    def process(self, text: str, clean: bool = True, lowercase: bool = True) -> str:
        result = text
        
        if lowercase:
            result = result.lower()
            
        if clean:
            # Elimina caracteres especiales pero mantiene acentos básicos
            result = re.sub(r'[^a-záéíóúüñ0-9\s]', '', result)
            
        return result.strip()
