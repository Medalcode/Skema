[![Demo](https://img.shields.io/badge/Demo-Vercel-000000?style=flat-square&logo=vercel)](https://skema-api.vercel.app)

# Skema

**Middleware Inteligente para Clasificación y Routing de Requerimientos Operacionales**

> Skema automatiza el triaje, categorización y enrutamiento de requerimientos de software a escala, transformando entradas de texto no estructurado en datos operativos accionables con inteligencia híbrida y feedback humano.

---

## 🎯 El Problema

En equipos de producto y operaciones de ingeniería de alto volumen, la entrada de requerimientos (tickets, feedback de usuarios, historias de usuario) es caótica y ruidosa.

- **Cuello de botella manual:** Product Managers y Tech Leads pierden horas semanales clasificando y asignando tickets.
- **Inconsistencia:** La clasificación manual varía según quién la haga y cuándo.
- **Datos muertos:** El feedback valioso se pierde en el ruido por falta de etiquetado inmediato.
- **Costo operacional:** Clasificación deficiente genera routing incorrecto y retrasos en resolución.

## 💡 La Solución

Skema es un **sistema operativo de intake inteligente** diseñado para operar como middleware entre las fuentes de entrada (GitHub, Jira, Slack, Email) y los sistemas de gestión.

### Principios Clave

1. **Modularidad Aislada:** La lógica de ingesta, limpieza, inferencia y persistencia están completamente desacopladas. Cambiar el motor de clasificación no afecta la API.
2. **Product-Ready:** Construido con observabilidad, contratos de datos estrictos, persistencia real y operación continua en mente.
3. **Agnóstico al Modelo:** Arquitectura hexagonal que permite intercambiar motores de clasificación (Reglas → Embeddings → LLMs → Ensembles) sin reescribir el sistema.
4. **Feedback Loop:** Incorpora correcciones humanas para mejora continua del sistema.

---

## ✨ Características Actuales (FASE 4: Producción)

### 🧠 Clasificador Híbrido Inteligente
- **Reglas Keyword-Based:** Detecta patrones determinísticos rápidamente
- **Embeddings Semánticos:** Búsqueda semántica cuando las reglas son insuficientes
- **Confidence Scoring Real:** Score 0.0-1.0 que refleja certeza verdadera
- **Fallback Elegante:** Sistema sigue funcionando incluso si embeddings no están disponibles

### 💾 Persistencia y Observabilidad
- **PostgreSQL ORM:** Persistencia real con SQLAlchemy
- **4 Modelos de Datos:** Requirements, Classifications, Feedback, Metrics
- **Feedback Loop Completo:** Captura correcciones humanas para mejora continua

### 🎨 Dashboard Operacional
- **Home:** Últimas clasificaciones + estadísticas en tiempo real
- **Revisión:** Tickets de baja confianza listos para corrección humana
- **Métricas:** Distribución de categorías, histogramas de confianza, precisión

### 🚀 API REST Completa
- `POST /classify` - Clasificar nuevo requerimiento
- `POST /api/feedback` - Registrar feedback humano
- `GET /` - Dashboard principal
- `GET /review` - Panel de revisión
- `GET /metrics` - Métricas del sistema
- `GET /health` - Health check

### 🔒 Seguridad y Control
- **API Key Auth** (opt-in via `API_KEY` env var)
- **Rate Limiting** (configurable: `RATE_LIMIT_PER_MINUTE`)
- **CORS configurable** (`CORS_ORIGINS`)
- **Request ID tracking** en headers de respuesta

### 📦 Categorías Soportadas
- **Bug:** Defectos, errores, crashes
- **Feature:** Nuevas funcionalidades, mejoras
- **Documentation:** Docs, wikis, guías
- **Infrastructure:** DevOps, deployment, CI/CD
- **Performance:** Optimización, escalabilidad
- **Security:** Vulnerabilidades, seguridad
- **General:** Otros

---

## 🏗 Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Entrada Externa                          │
│              (GitHub, Jira, Email, API)                     │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   FastAPI REST Endpoint    │
                    │   /classify                │
                    └─────────────┬──────────────┘
                                  │
        ┌─────────────────────────▼──────────────────────────┐
        │      Use Case: ClassifyRequirement                  │
        └─────────────────────────┬──────────────────────────┘
                                  │
        ┌─────────────────────────▼──────────────────────────┐
        │      HybridClassifier Adapter                       │
        │  ┌──────────────┐  ┌──────────────┐                │
        │  │ Keyword Rules│  │  Embeddings  │                │
        │  └──────────────┘  └──────────────┘                │
        │         │                  │                        │
        │         └──────┬───────────┘                        │
        │                ▼                                    │
        │          Confidence Score                          │
        │          (0.0 - 1.0)                               │
        └─────────────────────────┬──────────────────────────┘
                                  │
        ┌─────────────────────────▼──────────────────────────┐
        │      PostgreSQL Repository                          │
        │  ┌──────────────┐  ┌──────────────┐                │
        │  │ Requirements │  │Classifications│                │
        │  └──────────────┘  └──────────────┘                │
        │  ┌──────────────┐  ┌──────────────┐                │
        │  │  Feedback    │  │   Metrics    │                │
        │  └──────────────┘  └──────────────┘                │
        └─────────────────────────┬──────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │  Dashboard + Observabilidad│
                    │ (Métricas, Precisión, UI) │
                    └────────────────────────────┘
```

---

## 🚀 Inicio Rápido

### Opción A: Docker (Recomendado - 5 minutos)

```bash
# 1. Construye y levanta servicios
docker-compose up --build

# 2. En otra terminal: carga demo con 200 tickets
docker exec -it skema_api python scripts/demo.py

# 3. Abre dashboard
open http://localhost:8000
```

### Opción B: Local (requiere PostgreSQL)

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Configura variable de entorno
export DATABASE_URL="postgresql://skema:skema@localhost:5432/skema_db"

# 3. Ejecuta demostración
python scripts/demo.py --count 200

# 4. Levanta API
python -m skema.api.main

# 5. Abre http://localhost:8000
```

### Resultado Esperado
```
✅ 200 tickets clasificados automáticamente
✅ Dashboard visible con últimas clasificaciones
✅ Puedes proporcionar feedback humano
✅ Métricas en tiempo real

Estadísticas:
- Total procesado: 200
- Confianza promedio: 0.82
- Baja confianza (<60%): ~15 tickets
- Distribución: 30% Bugs, 25% Features, 15% Infrastructure, etc.
```

---

## 📊 Demostración Interactiva

1. Abre http://localhost:8000 (Dashboard Home)
2. Verás últimas 20 clasificaciones automáticas
3. Haz click en botón **"Feedback"** en cualquier ticket
4. Proporciona feedback:
   - "✓ Correcta" → marca como acertado
   - "✎ Corregir" → proporciona categoría correcta
5. En `/metrics` verás actualizada la precisión

---

## 🏗 Estructura del Proyecto

```
skema/
├── core/                  # Dominio (limpio, sin dependencias)
│   ├── interfaces.py      # Puertos hexagonales
│   ├── models.py          # Entidades y Value Objects
│   └── use_cases.py       # Casos de uso
├── adapters/              # Implementaciones concretas
│   ├── classifiers.py     # Dummy + Hybrid (Reglas + Embeddings)
│   └── storage.py         # Repositorios en memoria
├── infrastructure/        # Capas técnicas
│   ├── database.py        # SQLAlchemy async setup
│   ├── models.py          # ORM Models
│   └── repositories.py    # PostgreSQL implementations
├── api/                   # API REST + Dashboard
│   ├── main.py            # FastAPI server
│   └── middleware.py      # Auth, rate limit, error handlers, request ID
├── dashboard/             # UI (Jinja2 templates)
│   └── templates/         # HTML pages (index, review, metrics)
├── datasets/              # Synthetic data generator
├── bootstrap.py           # Composición de dependencias
├── alembic/               # Migraciones de base de datos
│   ├── env.py
│   └── versions/          # Migration scripts
└── tests/                 # Suite de tests (20 tests)
```

---

## 🗺 Roadmap

### ✅ Fase 1: MVP Demostrable (COMPLETADA)
- [x] Clasificador híbrido (Reglas + Embeddings)
- [x] Persistencia PostgreSQL
- [x] Dashboard operacional (3 páginas)
- [x] Feedback loop humano
- [x] Dataset sintético realista
- [x] Docker + docker-compose

### ✅ Fase 2: Observabilidad, Tests y Rendimiento (COMPLETADA)
- [x] Logging estructurado y profesional integrado
- [x] Refactorización completa a asíncrono (FastAPI + Asyncpg)
- [x] Configuración centralizada (Pydantic Settings)
- [x] Optimización de IA (Carga Singleton del modelo)
- [x] Unit + Integration + Contract tests (20 tests)
- [x] Error handling mejorado con handlers globales

### ✅ Fase 3: Calidad y Seguridad (COMPLETADA)
- [x] Middleware de autenticación (API Key)
- [x] Rate limiting configurable
- [x] Request ID tracking
- [x] CORS configurable
- [x] Tests de infraestructura (repositorios PostgreSQL via SQLite)
- [x] Tests de contratos para todos los repositorios
- [x] Validación estricta de configuración (extra="forbid")
- [x] Modelos con CHECK constraints y timezone-aware

### ✅ Fase 4: Producción (COMPLETADA)
- [x] Migraciones Alembic para esquema de base de datos
- [x] Pool de conexiones configurable (pool_size=5)
- [x] Inicialización graceful (sin bloqueo si DB no disponible)
- [x] Arquitectura hexagonal estricta (0 imports de frameworks en core/)

### 🔌 Fase 5: Conectores Reales
- [ ] GitHub Issues adapter
- [ ] Jira API adapter
- [ ] Webhook listeners
- [ ] Batch processing

### 🧠 Fase 6: Inteligencia Avanzada
- [ ] Reentrenamiento incremental
- [ ] Multi-model ensemble
- [ ] Detección de drift
- [ ] Recomendaciones automáticas

---

## 📖 Documentación

- [QUICKSTART.md](QUICKSTART.md) - Instrucciones rápidas (5 minutos)
- [CHANGELOG_MVP.md](CHANGELOG_MVP.md) - Cambios técnicos detallados
- [ARQUITECTURA.md](ARQUITECTURA.md) - Visión de alto nivel
- [docs/agents.md](docs/agents.md) - Documento de agentes
- [docs/skills.md](docs/skills.md) - Documento de skills

---

## 🔧 Configuración

Copia `.env.example` a `.env` y ajusta según necesites:

```bash
# Database
DATABASE_URL=postgresql://skema:skema@localhost:5432/skema_db

# API
API_PORT=8000
CORS_ORIGINS=["*"]

# Security (opt-in; leave empty to disable)
API_KEY=
RATE_LIMIT_PER_MINUTE=60

# Classifier
CLASSIFIER_MODEL=hybrid       # hybrid | dummy
CONFIDENCE_THRESHOLD=0.60

# Embeddings
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
```

---

## 📈 Casos de Uso Reales

- **Backlog Grooming Automático:** Etiquetar tickets como Bug/Feature/Tech Debt antes de que un humano los vea
- **Routing de Soporte N1:** Detectar keywords críticas para escalar incidentes de seguridad inmediatamente
- **Análisis de Tendencias:** Identificar patrones en miles de comentarios de usuarios
- **Matriz de Impacto:** Priorizar features basado en volumen de feedback
- **Auditoría:** Revisar decisiones automáticas con feedback humano

---

## 🤝 Contribuir

Por favor consulta [BITACORA.md](BITACORA.md) para detalles de desarrollo.

---

## 📄 Licencia

MIT

---

**Estado Actual:** FASE 4 - Producción ✅
Última actualización: 21 de junio de 2026

Para más detalles técnicos, ver [CHANGELOG_MVP.md](CHANGELOG_MVP.md)
