from abc import ABC, abstractmethod
from typing import List
from .models import Requerimiento, ResultadoClasificacion

class ClasificadorPort(ABC):
    """
    Puerto (Interfaz) para los servicios de clasificación.
    Cualquier adaptador (Dummy, OpenAI, Scikit) debe cumplir este contrato.
    """
    @abstractmethod
    def clasificar(self, req: Requerimiento) -> ResultadoClasificacion:
        pass

class RepositorioResultadosPort(ABC):
    """
    Puerto (Interfaz) para la persistencia de resultados.
    """
    @abstractmethod
    def guardar(self, resultado: ResultadoClasificacion) -> None:
        pass

    @abstractmethod
    def obtener_por_id(self, id: str) -> ResultadoClasificacion:
        pass
