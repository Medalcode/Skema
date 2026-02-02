# main.py - Preprocesamiento

def main():

    print("[Preprocesamiento] Procesando requerimientos...")
    pre = Preprocessor()
    requerimientos = [
        {"id": 1, "texto": "El sistema debe permitir login de usuarios."},
        {"id": 2, "texto": "Generar reportes mensuales en PDF."},
    ]
    for req in requerimientos:
        limpio = pre.limpiar_texto(req["texto"])
        print(f"[Preprocesamiento] Req {req['id']}: {limpio}")

import re

class Preprocessor:
    def limpiar_texto(self, texto):
        """Ejemplo de limpieza: minúsculas y eliminación de caracteres especiales."""
        texto = texto.lower()
        texto = re.sub(r'[^a-záéíóúüñ0-9\s]', '', texto)
        return texto.strip()
if __name__ == "__main__":
    main()
