# main.py - Clasificador Batch (Simulación)
import sys
import os

# Ajuste de path para poder importar skema sin instalarlo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skema.core.domain.models import Requerimiento
from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter

def main():
    print("[Clasificador Batch] Iniciando proceso por lotes...")
    
    # Instanciamos el MISMO adaptador que usa la API
    classifier = DummyClassifierAdapter()
    
    raw_requerimientos = [
        {"texto": "el sistema debe permitir login de usuarios"},
        {"texto": "generar reportes mensuales en pdf"},
        {"texto": "la base de datos debe ser postgresql"}
    ]
    
    for raw in raw_requerimientos:
        # Convertimos a Dominio
        req = Requerimiento.crear_nuevo(texto=raw["texto"])
        
        # Clasificamos
        resultado = classifier.clasificar(req)
        
        print(f"[Batch] Req {req.id[:8]}... -> {resultado.categoria} (Conf: {resultado.confianza})")

if __name__ == "__main__":
    main()
