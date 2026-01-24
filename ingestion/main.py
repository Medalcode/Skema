# main.py - Ingesta de datos

def main():

    print("[Ingesta] Inicializando ingesta de requerimientos...")
    ingestor = Ingestor()
    requerimientos = ingestor.recibir_requerimientos()
    for req in requerimientos:
        ingestor.enviar_a_cola(req)
    print(f"[Ingesta] {len(requerimientos)} requerimientos procesados.")

class Ingestor:
    def recibir_requerimientos(self):
        """Simula la recepción de requerimientos desde una fuente externa."""
        # En una implementación real, aquí se conectaría a una API, archivo, Kafka, etc.
        print("[Ingesta] Recibiendo requerimientos...")
        return [
            {"id": 1, "texto": "El sistema debe permitir login de usuarios."},
            {"id": 2, "texto": "Generar reportes mensuales en PDF."},
        ]

    def enviar_a_cola(self, requerimiento):
        """Simula el envío del requerimiento a una cola de procesamiento."""
        # Aquí se integraría con Kafka, RabbitMQ, etc.
        print(f"[Ingesta] Enviando a cola: {requerimiento['id']} - {requerimiento['texto']}")
if __name__ == "__main__":
    main()
