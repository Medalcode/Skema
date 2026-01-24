# main.py - Almacenamiento

def main():

    print("[Almacenamiento] Inicializando almacenamiento...")
    storage = Storage()
    resultado = {"id": 1, "texto": "el sistema debe permitir login de usuarios", "categoria": "Autenticación"}
    storage.guardar_resultado(resultado)
    print("[Almacenamiento] Resultado almacenado.")

class Storage:
    def guardar_resultado(self, resultado):
        """Simula el guardado de un resultado de clasificación."""
        # Aquí se integraría con una base de datos real (MongoDB, SQL, etc.)
        print(f"[Almacenamiento] Guardando: {resultado}")
if __name__ == "__main__":
    main()
