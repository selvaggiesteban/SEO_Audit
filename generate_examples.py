"""
Generate Example Outputs - Genera ejemplos de auditorías para ambos sitios
==========================================================================
Crea informes de ejemplo para selvaggiesteban.dev y lanuscomputacion.com
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Configurar codificación para Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.audit_engine import AuditEngine, AuditConfig


def generate_selveaggiesteban_audit():
    """Genera auditoría de ejemplo para selvaggiesteban.dev"""
    print("🔍 Generando auditoría para selvaggiesteban.dev...")
    
    config = AuditConfig(
        site_url="https://selvaggiesteban.dev",
        site_name="selvaggiesteban.dev",
        period_days=28,
        output_dir=str(ROOT_DIR / "output" / "selvaggiesteban.dev"),
        weights={
            "posicionamiento": 25,
            "palabras_clave": 20,
            "contenido": 15,
            "seo_tecnico": 15,
            "experiencia_usuario": 10,
            "enlaces": 10,
            "competencia": 5
        }
    )
    
    engine = AuditEngine(config)
    
    # Sobrescribir datos de ejemplo con datos más específicos
    engine.data['gsc'] = {
        'totalClicks': 1250,
        'totalImpressions': 45000,
        'averageCTR': 2.8,
        'averagePosition': 22.5,
        'queries': [
            {'query': 'recuperar página web', 'clicks': 120, 'impressions': 2500, 'ctr': 4.8, 'position': 12},
            {'query': 'restaurar sitio web', 'clicks': 95, 'impressions': 1800, 'ctr': 5.3, 'position': 14},
            {'query': 'cómo recuperar mi página', 'clicks': 85, 'impressions': 1500, 'ctr': 5.7, 'position': 16},
            {'query': 'recuperación de página web', 'clicks': 75, 'impressions': 1200, 'ctr': 6.3, 'position': 18},
            {'query': 'mi página web no carga', 'clicks': 65, 'impressions': 1000, 'ctr': 6.5, 'position': 20},
            {'query': 'problemas con mi sitio web', 'clicks': 55, 'impressions': 900, 'ctr': 6.1, 'position': 22},
            {'query': 'arreglar página web', 'clicks': 45, 'impressions': 800, 'ctr': 5.6, 'position': 24},
            {'query': 'página web caída', 'clicks': 40, 'impressions': 700, 'ctr': 5.7, 'position': 26},
            {'query': 'sitio web no funciona', 'clicks': 35, 'impressions': 600, 'ctr': 5.8, 'position': 28},
            {'query': 'error en mi página', 'clicks': 30, 'impressions': 500, 'ctr': 6.0, 'position': 30},
        ]
    }
    
    engine.data['pagespeed'] = {
        'mobile': {
            'score': 72,
            'lcp': 3.1,
            'fid': 120,
            'cls': 0.08,
            'fcp': 1.9,
            'tti': 3.8,
            'tbt': 280
        },
        'desktop': {
            'score': 88,
            'lcp': 1.6,
            'fid': 45,
            'cls': 0.04,
            'fcp': 1.1,
            'tti': 1.8,
            'tbt': 95
        }
    }
    
    result = engine.run_full_audit()
    return result


def generate_lanus_audit():
    """Genera auditoría de ejemplo para lanuscomputacion.com"""
    print("🔍 Generando auditoría para lanuscomputacion.com...")
    
    config = AuditConfig(
        site_url="sc-domain:lanuscomputacion.com",
        site_name="Lanús Computación",
        period_days=28,
        output_dir=str(ROOT_DIR / "output" / "lanuscomputacion.com"),
        weights={
            "posicionamiento": 25,
            "palabras_clave": 20,
            "contenido": 15,
            "seo_tecnico": 15,
            "experiencia_usuario": 10,
            "enlaces": 10,
            "competencia": 5
        }
    )
    
    engine = AuditEngine(config)
    
    # Sobrescribir datos de ejemplo con datos más específicos
    engine.data['gsc'] = {
        'totalClicks': 890,
        'totalImpressions': 32000,
        'averageCTR': 2.8,
        'averagePosition': 25.3,
        'queries': [
            {'query': 'autocad 2022', 'clicks': 85, 'impressions': 2200, 'ctr': 3.9, 'position': 15},
            {'query': 'computación lanús', 'clicks': 75, 'impressions': 1800, 'ctr': 4.2, 'position': 12},
            {'query': 'reparación pc lanús', 'clicks': 65, 'impressions': 1200, 'ctr': 5.4, 'position': 18},
            {'query': 'venta de computadoras lanús', 'clicks': 55, 'impressions': 900, 'ctr': 6.1, 'position': 20},
            {'query': 'soporte técnico lanús', 'clicks': 45, 'impressions': 750, 'ctr': 6.0, 'position': 22},
            {'query': 'taller de computación lanús', 'clicks': 40, 'impressions': 600, 'ctr': 6.7, 'position': 25},
            {'query': 'service de pc lanús', 'clicks': 35, 'impressions': 500, 'ctr': 7.0, 'position': 28},
            {'query': 'impresoras lanús', 'clicks': 30, 'impressions': 400, 'ctr': 7.5, 'position': 30},
        ]
    }
    
    engine.data['pagespeed'] = {
        'mobile': {
            'score': 58,
            'lcp': 4.2,
            'fid': 180,
            'cls': 0.15,
            'fcp': 2.8,
            'tti': 5.2,
            'tbt': 420
        },
        'desktop': {
            'score': 75,
            'lcp': 2.1,
            'fid': 65,
            'cls': 0.06,
            'fcp': 1.4,
            'tti': 2.5,
            'tbt': 150
        }
    }
    
    result = engine.run_full_audit()
    return result


def main():
    """Genera ambos informes de ejemplo."""
    print("=" * 60)
    print("SEO Audit Tool - Generador de Ejemplos")
    print("=" * 60)
    
    # Crear directorio de salida
    output_dir = ROOT_DIR / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generar auditorías
    try:
        selvaggi_result = generate_selveaggiesteban_audit()
        print(f"✅ selvaggiesteban.dev: Puntuación {selvaggi_result.get('scoring', {}).get('total', 'N/A')}")
    except Exception as e:
        print(f"❌ Error en selvaggiesteban.dev: {e}")
    
    try:
        lanus_result = generate_lanus_audit()
        print(f"✅ lanuscomputacion.com: Puntuación {lanus_result.get('scoring', {}).get('total', 'N/A')}")
    except Exception as e:
        print(f"❌ Error en lanuscomputacion.com: {e}")
    
    print("\n" + "=" * 60)
    print("Archivos generados en: output/")
    print("=" * 60)


if __name__ == '__main__':
    main()
