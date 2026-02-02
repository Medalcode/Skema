from skema.core.ports.interfaces import ClasificadorPort
from skema.core.domain.models import Requerimiento, ResultadoClasificacion

class DummyClassifierAdapter(ClasificadorPort):
    """
    Implementación 'Dummy' del clasificador.
    Útil para testing, desarrollo local y validación de contratos.
    """
    def clasificar(self, req: Requerimiento) -> ResultadoClasificacion:
        texto = req.texto.lower()
        categoria = "General"
        
        # Lógica simple de palabras clave (misma que antes, pero encapsulada)
        if "login" in texto or "usuario" in texto:
            categoria = "Autenticación"
        elif "reporte" in texto or "pdf" in texto:
            categoria = "Reportes"
            
        return ResultadoClasificacion(
            requerimiento_id=req.id,
            categoria=categoria,
            confianza=0.85, # Dummy confidence
            modelo_utilizado="DummyAdapter-v1"
        )
