#!/usr/bin/env python
"""
Script de demostración: Carga datos sintéticos y los clasifica.

Uso:
    python scripts/demo.py --count 100  # Carga 100 tickets

Este script transforma Skema de "arquitectura" a "producto funcional demostrable".
"""

import argparse
import sys
from sqlalchemy.orm import Session

# Imports
from skema.infrastructure.database import SessionLocal, init_db, engine, Base
from skema.infrastructure.models import RequirementModel, ClassificationModel
from skema.datasets import generate_synthetic_tickets
from skema.bootstrap import bootstrap
from skema.core.models import Requirement

def setup_database():
    """Inicializa la base de datos"""
    print("📦 Inicializando base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos lista\n")

def load_synthetic_data(count: int):
    """Carga tickets sintéticos en la BD"""
    print(f"📥 Generando {count} tickets sintéticos...")
    tickets = generate_synthetic_tickets(count)
    
    session = SessionLocal()
    try:
        print(f"💾 Guardando en BD...")
        for ticket in tickets:
            model = RequirementModel(
                id=ticket.id,
                text=ticket.text,
                metadata_json=ticket.metadata,
            )
            session.add(model)
        
        session.commit()
        print(f"✅ {count} tickets cargados\n")
    finally:
        session.close()

def classify_all():
    """Clasifica todos los tickets cargados"""
    session = SessionLocal()
    
    try:
        container = bootstrap(session)
        
        # Obtén todos los tickets sin clasificar
        requirements = session.query(RequirementModel).filter(
            ~RequirementModel.classifications.any()
        ).all()
        
        print(f"🤖 Clasificando {len(requirements)} tickets...")
        
        for i, req_model in enumerate(requirements, 1):
            # Convierte a domain model
            domain_req = req_model.to_domain()
            
            # Clasifica
            result = container.classify_requirement.execute(domain_req)
            
            # Muestra progreso
            if i % 50 == 0 or i == len(requirements):
                print(f"   [{i}/{len(requirements)}] ✓ {result.category} (conf: {result.confidence.value:.2f})")
        
        print(f"✅ Clasificación completada\n")
        
    finally:
        session.close()

def show_stats():
    """Muestra estadísticas del sistema"""
    session = SessionLocal()
    
    try:
        total_reqs = session.query(RequirementModel).count()
        total_classifications = session.query(ClassificationModel).count()
        
        if total_classifications > 0:
            from sqlalchemy import func
            
            # Categorías
            categories = session.query(
                ClassificationModel.category,
                func.count(ClassificationModel.id)
            ).group_by(ClassificationModel.category).all()
            
            # Confianza promedio
            avg_conf = session.query(func.avg(ClassificationModel.confidence)).scalar() or 0
            
            # Baja confianza
            low_conf = session.query(ClassificationModel).filter(
                ClassificationModel.confidence < 0.6
            ).count()
            
            print("📊 ESTADÍSTICAS DEL SISTEMA")
            print("=" * 50)
            print(f"Tickets cargados:      {total_reqs}")
            print(f"Clasificaciones:       {total_classifications}")
            print(f"Confianza promedio:    {avg_conf:.2f}")
            print(f"Baja confianza (<60%): {low_conf}\n")
            
            print("Distribución por categoría:")
            for category, count in categories:
                pct = (count / total_classifications) * 100
                print(f"  {category:20} {count:5} ({pct:5.1f}%)")
    
    finally:
        session.close()

def show_sample_classifications():
    """Muestra ejemplos de clasificaciones"""
    session = SessionLocal()
    
    try:
        print("\n📝 EJEMPLOS DE CLASIFICACIONES")
        print("=" * 80)
        
        samples = session.query(ClassificationModel).order_by(
            ClassificationModel.created_at.desc()
        ).limit(5).all()
        
        for sample in samples:
            text = sample.requirement.text[:60]
            conf_bar = "█" * int(sample.confidence * 20) + "░" * (20 - int(sample.confidence * 20))
            
            print(f"\n✓ {text}...")
            print(f"  Categoría: {sample.category}")
            print(f"  Confianza: [{conf_bar}] {sample.confidence:.0%}")
            print(f"  Modelo:    {sample.model_version}")
    
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(
        description="Demostración de Skema - Pipeline de clasificación inteligente"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=200,
        help="Cantidad de tickets sintéticos a cargar (default: 200)"
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="No carga datos (solo clasifica lo existente)"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║          🔷 SKEMA - DEMO END-TO-END                             ║
    ║     Clasificación Inteligente de Requerimientos                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 1. Setup
        setup_database()
        
        # 2. Load data (si no se especifica --skip-load)
        if not args.skip_load:
            load_synthetic_data(args.count)
        
        # 3. Classify
        classify_all()
        
        # 4. Show results
        show_stats()
        show_sample_classifications()
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETADA")
        print("\nPróximos pasos:")
        print("  1. Levanta el dashboard:  python -m skema.api.main")
        print("  2. Abre en el navegador:  http://localhost:8000")
        print("  3. Revisa y proporciona feedback humano")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
