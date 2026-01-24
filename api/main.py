# main.py - API

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Requerimiento(BaseModel):
    texto: str

class DummyClassifier:
    def clasificar(self, texto):
        if "login" in texto or "usuario" in texto:
            return "Autenticación"
        if "reporte" in texto or "pdf" in texto:
            return "Reportes"
        return "General"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/clasificar")
def clasificar(req: Requerimiento):
    classifier = DummyClassifier()
    categoria = classifier.clasificar(req.texto.lower())
    return {"categoria": categoria}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
