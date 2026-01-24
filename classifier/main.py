# main.py - Clasificador

def main():

    print("[Clasificador] Clasificando requerimientos...")
    classifier = DummyClassifier()
    requerimientos = [
        {"id": 1, "texto": "el sistema debe permitir login de usuarios"},
        {"id": 2, "texto": "generar reportes mensuales en pdf"},
    ]
    for req in requerimientos:
        categoria = classifier.clasificar(req["texto"])
        print(f"[Clasificador] Req {req['id']}: {categoria}")

class DummyClassifier:
    def clasificar(self, texto):
        """Clasificador de ejemplo: asigna categoría según palabras clave."""
        if "login" in texto or "usuario" in texto:
            return "Autenticación"
        if "reporte" in texto or "pdf" in texto:
            return "Reportes"
        return "General"
if __name__ == "__main__":
    main()
