## 🚀 QUICK START - MVP Demostrable en 5 Minutos

### Opción A: Docker (Recomendado, sin dependencias locales)

```bash
# 1. Levanta PostgreSQL + API
docker-compose up --build

# 2. En otra terminal: Carga 200 tickets y clasifícalos
docker exec -it skema_api python scripts/demo.py

# 3. Abre http://localhost:8000
```

### Opción B: Local (requiere Python 3.9+ y PostgreSQL)

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Configura BD (crea una BD llamada skema_db)
export DATABASE_URL="postgresql://skema:skema@localhost:5432/skema_db"

# 3. Ejecuta demostración
python scripts/demo.py --count 200

# 4. Levanta API
python -m skema.api.main

# 5. Abre http://localhost:8000
```

---

## 🎯 QUÉ VAS A VER

```
✅ 200 tickets clasificados automáticamente
✅ Dashboard con últimas clasificaciones  
✅ Botones para proporcionar feedback humano
✅ Métricas: confianza promedio, distribución, precisión
✅ Tickets de baja confianza listados para revisión
```

**Endpoints disponibles:**
- `http://localhost:8000/` - Dashboard principal
- `http://localhost:8000/review` - Revisión (baja confianza)
- `http://localhost:8000/metrics` - Métricas
- `http://localhost:8000/health` - Health check
- `POST http://localhost:8000/classify` - API de clasificación

---

## 💡 DEMOSTRACIÓN INTERACTIVA

1. Ve a http://localhost:8000
2. Verás los últimas 20 clasificaciones
3. Haz click en "Feedback" en cualquier ticket
4. Proporciona feedback humano
5. Verifica que se guardó en `/metrics`

---

## 📊 QUÉ CAMBIÓ

| | Antes | Ahora |
|---|---|---|
| **Persistencia** | In-Memory ❌ | PostgreSQL ✅ |
| **UI** | No había ❌ | 3 dashboards ✅ |
| **Feedback** | No había ❌ | Loop completo ✅ |
| **Clasificador** | Dummy rules | Híbrido (reglas + embeddings) |
| **Demostrable** | Teoría | Producto funcional |

---

## 🛠️ TROUBLESHOOTING

**"Port 8000 already in use"**
```bash
# Usa otro puerto
python -m skema.api.main --port 8001
```

**"PostgreSQL connection error"**
```bash
# Verifica conexión
psql postgresql://skema:skema@localhost:5432/skema_db

# O usa Docker que lo maneja automáticamente
docker-compose up
```

**"Embeddings not available"**
```bash
# Normal - Sistema sigue funcionando solo con reglas
# Primer uso: descargar embeddings (~23MB)
pip install sentence-transformers
```

---

Ver `CHANGELOG_MVP.md` para detalles técnicos completos.
