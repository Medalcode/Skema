# main.py - Monitoreo

def main():

    print("[Monitoreo] Inicializando monitoreo...")
    monitoring = Monitoring()
    monitoring.exponer_metricas()

from prometheus_client import start_http_server, Counter

class Monitoring:
    def __init__(self):
        self.reqs_procesados = Counter('requerimientos_procesados_total', 'Total de requerimientos procesados')

    def exponer_metricas(self):
        print("[Monitoreo] Exponiendo métricas en http://localhost:8001")
        start_http_server(8001)
        # Simulación de procesamiento
        for _ in range(5):
            self.reqs_procesados.inc()

if __name__ == "__main__":
    main()
