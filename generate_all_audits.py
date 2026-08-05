"""
Generate All Audits - Genera auditorías SEO completas para 7 sitios
====================================================================
Usa datos REALES recopilados de Google Search Console (período de 28 días:
2026-07-07 a 2026-08-04) y estimaciones de PageSpeed Insights.

Genera informes HTML completos para cada sitio en output/<site_name>/.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Fix codificación para Windows (utf-8 en stdout)
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Agregar directorio raíz del SEO_Audit al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from src.audit_engine import AuditEngine, AuditConfig


# ================================================================
# PESOS DE SCORING (mismos para todos los sitios)
# ================================================================
WEIGHTS = {
    "posicionamiento": 25,
    "palabras_clave": 20,
    "contenido": 15,
    "seo_tecnico": 15,
    "experiencia_usuario": 10,
    "enlaces": 10,
    "competencia": 5
}


# ================================================================
# DATOS REALES DE GSC PARA LOS 7 SITIOS
# Período: 2026-07-07 a 2026-08-04 (28 días)
# ================================================================

SITES = [
    # --------------------------------------------------------------
    # SITE 1: mottobasic.com
    # --------------------------------------------------------------
    {
        "site_url": "sc-domain:mottobasic.com",
        "site_name": "mottobasic.com",
        "output_dir": "mottobasic.com",
        "gsc": {
            "totalClicks": 324,
            "totalImpressions": 3299,
            "averageCTR": 9.82,
            "averagePosition": 8.59,
            "queries": [
                {"query": "motto basic", "clicks": 126, "impressions": 206, "ctr": 61.17, "position": 1.57},
                {"query": "motto concordia", "clicks": 28, "impressions": 39, "ctr": 71.79, "position": 1.03},
                {"query": "mottobasic", "clicks": 26, "impressions": 48, "ctr": 54.17, "position": 1.0},
                {"query": "moto basic", "clicks": 6, "impressions": 85, "ctr": 7.06, "position": 5.27},
                {"query": "motobasic", "clicks": 5, "impressions": 32, "ctr": 15.63, "position": 5.97},
                {"query": "motto", "clicks": 3, "impressions": 437, "ctr": 0.69, "position": 7.32}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 65, "lcp": 3.0, "fid": 120, "cls": 0.10, "fcp": 2.0, "tti": 4.0, "tbt": 300},
            "desktop": {"score": 80, "lcp": 1.8, "fid": 50, "cls": 0.05, "fcp": 1.2, "tti": 2.2, "tbt": 120}
        }
    },
    # --------------------------------------------------------------
    # SITE 2: decotay.com.ar
    # --------------------------------------------------------------
    {
        "site_url": "https://decotay.com.ar/",
        "site_name": "decotay.com.ar",
        "output_dir": "decotay.com.ar",
        "gsc": {
            "totalClicks": 7,
            "totalImpressions": 39,
            "averageCTR": 17.95,
            "averagePosition": 7.85,
            "queries": [
                {"query": "taytay", "clicks": 0, "impressions": 1, "ctr": 0.0, "position": 43.0}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 55, "lcp": 4.0, "fid": 180, "cls": 0.15, "fcp": 2.8, "tti": 5.0, "tbt": 420},
            "desktop": {"score": 72, "lcp": 2.2, "fid": 70, "cls": 0.06, "fcp": 1.5, "tti": 2.6, "tbt": 170}
        }
    },
    # --------------------------------------------------------------
    # SITE 3: selvaggiesteban.dev
    # --------------------------------------------------------------
    {
        "site_url": "https://selvaggiesteban.dev/",
        "site_name": "selvaggiesteban.dev",
        "output_dir": "selvaggiesteban.dev",
        "gsc": {
            "totalClicks": 12,
            "totalImpressions": 1677,
            "averageCTR": 0.72,
            "averagePosition": 26.22,
            "queries": [
                {"query": "como recuperar mi sitio web", "clicks": 0, "impressions": 23, "ctr": 0.0, "position": 20.83},
                {"query": "recuperacion de paginas web", "clicks": 0, "impressions": 23, "ctr": 0.0, "position": 38.83},
                {"query": "como puedo recuperar mi pagina web", "clicks": 0, "impressions": 27, "ctr": 0.0, "position": 31.04},
                {"query": "recuperar una pagina web", "clicks": 0, "impressions": 21, "ctr": 0.0, "position": 44.33},
                {"query": "sistemas multi-agente", "clicks": 0, "impressions": 52, "ctr": 0.0, "position": 60.31},
                {"query": "consultoría seo", "clicks": 0, "impressions": 34, "ctr": 0.0, "position": 28.94},
                {"query": "best online marketing resources 2024", "clicks": 0, "impressions": 16, "ctr": 0.0, "position": 8.19}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 72, "lcp": 3.1, "fid": 120, "cls": 0.08, "fcp": 1.9, "tti": 3.8, "tbt": 280},
            "desktop": {"score": 88, "lcp": 1.6, "fid": 45, "cls": 0.04, "fcp": 1.1, "tti": 1.8, "tbt": 95}
        }
    },
    # --------------------------------------------------------------
    # SITE 4: lanuscomputacion.com
    # --------------------------------------------------------------
    {
        "site_url": "sc-domain:lanuscomputacion.com",
        "site_name": "lanuscomputacion.com",
        "output_dir": "lanuscomputacion.com",
        "gsc": {
            "totalClicks": 30,
            "totalImpressions": 937,
            "averageCTR": 3.20,
            "averagePosition": 14.18,
            "queries": [
                {"query": "computacion lanus", "clicks": 2, "impressions": 46, "ctr": 4.35, "position": 15.35},
                {"query": "estabilizador 2200va", "clicks": 1, "impressions": 1, "ctr": 100.0, "position": 74.0},
                {"query": "joystick inalambrico redragon darkflame g820", "clicks": 1, "impressions": 2, "ctr": 50.0, "position": 36.5},
                {"query": "casa de computacion cerca de mi", "clicks": 0, "impressions": 8, "ctr": 0.0, "position": 5.25},
                {"query": "casa de computacion lanus", "clicks": 0, "impressions": 13, "ctr": 0.0, "position": 8.54},
                {"query": "pc lanus", "clicks": 0, "impressions": 16, "ctr": 0.0, "position": 6.25},
                {"query": "hp deskjet 2540 cartuchos", "clicks": 0, "impressions": 4, "ctr": 0.0, "position": 10.5},
                {"query": "hp 2540 cartuchos", "clicks": 0, "impressions": 1, "ctr": 0.0, "position": 22.0}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 48, "lcp": 4.5, "fid": 200, "cls": 0.18, "fcp": 3.0, "tti": 5.5, "tbt": 480},
            "desktop": {"score": 68, "lcp": 2.3, "fid": 75, "cls": 0.07, "fcp": 1.6, "tti": 2.7, "tbt": 180}
        }
    },
    # --------------------------------------------------------------
    # SITE 5: oteguiobras.com
    # --------------------------------------------------------------
    {
        "site_url": "sc-domain:oteguiobras.com",
        "site_name": "oteguiobras.com",
        "output_dir": "oteguiobras.com",
        "gsc": {
            "totalClicks": 47,
            "totalImpressions": 339,
            "averageCTR": 13.86,
            "averagePosition": 5.37,
            "queries": [
                {"query": "otegui obras", "clicks": 21, "impressions": 45, "ctr": 46.67, "position": 1.07},
                {"query": "grupo otegui", "clicks": 2, "impressions": 19, "ctr": 10.53, "position": 3.37},
                {"query": "otegui", "clicks": 1, "impressions": 27, "ctr": 3.70, "position": 6.78},
                {"query": "samsung plaza oeste", "clicks": 0, "impressions": 4, "ctr": 0.0, "position": 9.75},
                {"query": "ferri real estate", "clicks": 0, "impressions": 3, "ctr": 0.0, "position": 9.0},
                {"query": "vcelina", "clicks": 0, "impressions": 6, "ctr": 0.0, "position": 3.67}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 70, "lcp": 2.9, "fid": 110, "cls": 0.09, "fcp": 1.8, "tti": 3.6, "tbt": 260},
            "desktop": {"score": 85, "lcp": 1.7, "fid": 48, "cls": 0.04, "fcp": 1.1, "tti": 2.0, "tbt": 100}
        }
    },
    # --------------------------------------------------------------
    # SITE 6: matiasgarcetesuarez.com.ar
    # --------------------------------------------------------------
    {
        "site_url": "https://matiasgarcetesuarez.com.ar/",
        "site_name": "matiasgarcetesuarez.com.ar",
        "output_dir": "matiasgarcetesuarez.com.ar",
        "gsc": {
            "totalClicks": 0,
            "totalImpressions": 68,
            "averageCTR": 0.0,
            "averagePosition": 5.21,
            "queries": [
                {"query": "garcete", "clicks": 0, "impressions": 10, "ctr": 0.0, "position": 5.7},
                {"query": "matias garcete", "clicks": 0, "impressions": 2, "ctr": 0.0, "position": 10.0}
            ]
        },
        "pagespeed": {
            "mobile": {"score": 45, "lcp": 5.0, "fid": 220, "cls": 0.20, "fcp": 3.2, "tti": 6.0, "tbt": 520},
            "desktop": {"score": 65, "lcp": 2.5, "fid": 80, "cls": 0.08, "fcp": 1.7, "tti": 2.9, "tbt": 200}
        }
    },
    # --------------------------------------------------------------
    # SITE 7: selvaggiconsultores.com
    # --------------------------------------------------------------
    {
        "site_url": "sc-domain:selvaggiconsultores.com",
        "site_name": "selvaggiconsultores.com",
        "output_dir": "selvaggiconsultores.com",
        "gsc": {
            "totalClicks": 0,
            "totalImpressions": 1,
            "averageCTR": 0.0,
            "averagePosition": 1.0,
            "queries": []
        },
        "pagespeed": {
            "mobile": {"score": 50, "lcp": 4.2, "fid": 190, "cls": 0.16, "fcp": 2.9, "tti": 5.2, "tbt": 440},
            "desktop": {"score": 70, "lcp": 2.4, "fid": 72, "cls": 0.07, "fcp": 1.6, "tti": 2.7, "tbt": 175}
        }
    }
]


def generate_audit(site_data: dict) -> dict:
    """Genera una auditoría para un sitio con los datos proporcionados."""
    site_url = site_data["site_url"]
    site_name = site_data["site_name"]
    output_dir = ROOT_DIR / "output" / site_data["output_dir"]

    print(f"\n{'=' * 60}")
    print(f"🔍 Generando auditoría para: {site_name}")
    print(f"   URL: {site_url}")
    print(f"   Output: {output_dir}")
    print(f"{'=' * 60}")

    # 1. Crear AuditConfig
    config = AuditConfig(
        site_url=site_url,
        site_name=site_name,
        period_days=28,
        output_dir=str(output_dir),
        weights=WEIGHTS
    )

    # 2. Crear el motor
    engine = AuditEngine(config)

    # 3. Sobrescribir datos de GSC con datos REALES
    engine.data['gsc'] = site_data["gsc"]

    # 4. Sobrescribir datos de PageSpeed con estimaciones
    engine.data['pagespeed'] = site_data["pagespeed"]

    # 5. Ejecutar auditoría completa
    result = engine.run_full_audit()

    # 6. Recuperar la puntuación desde engine.scoring
    score = engine.scoring.get('total', 'N/A')

    return {
        "site_name": site_name,
        "output_dir": str(output_dir),
        "score": score,
        "result": result
    }


def main():
    """Genera auditorías para los 7 sitios."""
    print("=" * 60)
    print("SEO Audit Tool - Generador de Auditorías para 7 Sitios")
    print("Período: 2026-07-07 a 2026-08-04 (28 días)")
    print("Datos: REALES de Google Search Console")
    print("=" * 60)

    # Crear directorio de salida principal
    output_base = ROOT_DIR / "output"
    output_base.mkdir(exist_ok=True)

    results = []

    # Generar auditoría para cada sitio
    for i, site_data in enumerate(SITES, 1):
        print(f"\n[Sitio {i}/7]")
        try:
            res = generate_audit(site_data)
            results.append(res)
            print(f"✅ {res['site_name']}: Puntuación {res['score']}/100")
            print(f"   📁 Informe: {res['output_dir']}/audit-report.html")
        except Exception as e:
            print(f"❌ Error en {site_data['site_name']}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "site_name": site_data["site_name"],
                "output_dir": str(ROOT_DIR / "output" / site_data["output_dir"]),
                "score": "ERROR",
                "result": None
            })

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL - 7 Auditorías SEO")
    print("=" * 60)
    print(f"{'Sitio':<35} {'Score':<8} {'Output'}")
    print("-" * 80)
    for res in results:
        score_str = f"{res['score']}/100" if res['score'] != "ERROR" else "ERROR"
        print(f"{res['site_name']:<35} {score_str:<8} {res['output_dir']}")
    print("=" * 60)
    print(f"✅ Total de auditorías generadas: {len(results)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
