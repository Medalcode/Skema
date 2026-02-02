import unittest
import sys
import os
from datetime import datetime

# Hack de entorno SOLO para testing sin virtualenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skema.core.domain.models import Requerimiento, ResultadoClasificacion
from skema.adapters.classifiers.dummy_adapter import DummyClassifierAdapter
from skema.adapters.storage.memory_adapter import InMemoryStorageAdapter

class TestHexagonalArchitecture(unittest.TestCase):
    
    def setUp(self):
        # Setup: Inyección de Dependencias Manual
        self.classifier = DummyClassifierAdapter()
        self.storage = InMemoryStorageAdapter()

    def test_flujo_completo_sin_api(self):
        """
        Verifica que podemos recibir, clasificar y guardar un requerimiento
        usando puramente objetos de dominio y adaptadores, sin HTTP.
        """
        # 1. Crear Requerimiento (Domain Factory)
        texto_input = "El sistema debe generar reportes PDF diarios"
        req = Requerimiento.crear_nuevo(texto=texto_input)
        
        # Validación de Entidad
        self.assertIsNotNone(req.id)
        self.assertIsInstance(req.timestamp, datetime)
        self.assertEqual(req.texto, texto_input)

        # 2. Clasificar (Inferencia Pura)
        resultado = self.classifier.clasificar(req)
        
        # Validación de Contrato
        self.assertIsInstance(resultado, ResultadoClasificacion)
        self.assertEqual(resultado.categoria, "Reportes")
        self.assertEqual(resultado.requerimiento_id, req.id)

        # 3. Persistencia (Storage Adapter)
        self.storage.guardar(resultado)
        
        # 4. Verificación de lectura
        guardado = self.storage.obtener_por_id(req.id)
        self.assertIsNotNone(guardado)
        self.assertEqual(guardado.requerimiento_id, req.id)
        self.assertEqual(guardado.categoria, "Reportes")

if __name__ == '__main__':
    unittest.main()
