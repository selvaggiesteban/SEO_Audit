"""
SEO Audit Engine - Motor principal de auditorías SEO
=====================================================
Genera informes HTML completos a partir de datos de GSC, GA4 y PageSpeed.

Uso:
    python audit_engine.py --site https://example.com --output ./output
    
    # O con configuración personalizada
    python audit_engine.py --site https://example.com --config ./config/custom.yaml
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@dataclass
class AuditConfig:
    """Configuración de la auditoría."""
    site_url: str
    site_name: str = ""
    period_days: int = 28
    output_dir: str = "./output"
    ga4_property_id: Optional[str] = None
    bing_site_url: Optional[str] = None
    pagespeed_api_key: Optional[str] = None
    
    # Pesos para scoring (default)
    weights: Dict[str, float] = field(default_factory=lambda: {
        "posicionamiento": 25,
        "palabras_clave": 20,
        "contenido": 15,
        "seo_tecnico": 15,
        "experiencia_usuario": 10,
        "enlaces": 10,
        "competencia": 5
    })
    
    # Filtros de keywords
    keyword_filters: Dict[str, Any] = field(default_factory=lambda: {
        "min_impressions": 10,
        "max_position": 30,
        "position_ranges": {
            "excellent": {"min": 11, "max": 15},
            "good": {"min": 16, "max": 20},
            "needs_work": {"min": 21, "max": 30}
        }
    })


class AuditEngine:
    """Motor principal de auditorías SEO."""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.data = {}
        self.analysis = {}
        self.scoring = {}
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Ejecuta una auditoría completa."""
        print(f"🔍 Iniciando auditoría para: {self.config.site_url}")
        
        # 1. Recopilar datos
        print("📊 Recopilando datos de GSC...")
        self._collect_gsc_data()
        
        if self.config.ga4_property_id:
            print("📈 Recopilando datos de GA4...")
            self._collect_ga4_data()
        
        if self.config.pagespeed_api_key:
            print("⚡ Analizando PageSpeed...")
            self._collect_pagespeed_data()
        
        # 2. Analizar datos
        print("🧠 Analizando datos...")
        self._analyze_positioning()
        self._analyze_keywords()
        self._analyze_content()
        self._analyze_technical_seo()
        self._analyze_user_experience()
        self._analyze_links()
        self._analyze_competition()
        
        # 3. Calcular puntuación
        print("🎯 Calculando puntuación...")
        self._calculate_scores()
        
        # 4. Generar plan de acción
        print("📋 Generando plan de acción...")
        self._generate_action_plan()
        
        # 5. Generar informe HTML
        print("📄 Generando informe HTML...")
        html_output = self._generate_html_report()
        
        # 6. Guardar archivos
        self._save_output(html_output)
        
        print(f"✅ Auditoría completada: {self.config.output_dir}")
        return self.analysis
    
    def _collect_gsc_data(self):
        """Recopila datos de Google Search Console."""
        # En producción, esto llamaría a la API de GSC
        # Por ahora, cargamos desde archivos JSON si existen
        data_file = Path(self.config.output_dir) / "raw-data.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data['gsc'] = json.load(f)
        else:
            # Datos de ejemplo para testing
            self.data['gsc'] = self._get_sample_gsc_data()
    
    def _collect_ga4_data(self):
        """Recopila datos de Google Analytics 4."""
        # Placeholder para integración con GA4
        self.data['ga4'] = self._get_sample_ga4_data()
    
    def _collect_pagespeed_data(self):
        """Recopila datos de PageSpeed Insights."""
        # Placeholder para integración con PageSpeed API
        self.data['pagespeed'] = self._get_sample_pagespeed_data()
    
    def _analyze_positioning(self):
        """Analiza el posicionamiento general."""
        gsc_data = self.data.get('gsc', {})
        
        total_clicks = gsc_data.get('totalClicks', 0)
        total_impressions = gsc_data.get('totalImpressions', 0)
        avg_ctr = gsc_data.get('averageCTR', 0)
        avg_position = gsc_data.get('averagePosition', 0)
        
        # Distribución de posiciones
        queries = gsc_data.get('queries', [])
        position_dist = {
            'top3': 0,
            'top10': 0,
            'top20': 0,
            'top30': 0,
            'beyond30': 0
        }
        
        for q in queries:
            pos = q.get('position', 0)
            if pos <= 3:
                position_dist['top3'] += 1
            elif pos <= 10:
                position_dist['top10'] += 1
            elif pos <= 20:
                position_dist['top20'] += 1
            elif pos <= 30:
                position_dist['top30'] += 1
            else:
                position_dist['beyond30'] += 1
        
        self.analysis['posicionamiento'] = {
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'avg_ctr': avg_ctr,
            'avg_position': avg_position,
            'position_distribution': position_dist,
            'total_queries': len(queries)
        }
    
    def _analyze_keywords(self):
        """Analiza palabras clave filtradas."""
        gsc_data = self.data.get('gsc', {})
        queries = gsc_data.get('queries', [])
        
        filters = self.config.keyword_filters
        min_imp = filters.get('min_impressions', 10)
        max_pos = filters.get('max_position', 30)
        
        filtered_keywords = []
        
        for q in queries:
            impressions = q.get('impressions', 0)
            position = q.get('position', 0)
            
            if impressions >= min_imp and position <= max_pos:
                # Determinar rango de posición
                pos_ranges = filters.get('position_ranges', {})
                if position <= pos_ranges.get('excellent', {}).get('max', 15):
                    position_class = 'excellent'
                elif position <= pos_ranges.get('good', {}).get('max', 20):
                    position_class = 'good'
                else:
                    position_class = 'needs_work'
                
                filtered_keywords.append({
                    'query': q.get('query', ''),
                    'clicks': q.get('clicks', 0),
                    'impressions': impressions,
                    'ctr': q.get('ctr', 0),
                    'position': position,
                    'position_class': position_class
                })
        
        # Ordenar por impresiones (mayor a menor)
        filtered_keywords.sort(key=lambda x: x['impressions'], reverse=True)
        
        self.analysis['palabras_clave'] = {
            'total_filtered': len(filtered_keywords),
            'keywords': filtered_keywords[:50],  # Top 50
            'summary': {
                'excellent': len([k for k in filtered_keywords if k['position_class'] == 'excellent']),
                'good': len([k for k in filtered_keywords if k['position_class'] == 'good']),
                'needs_work': len([k for k in filtered_keywords if k['position_class'] == 'needs_work'])
            }
        }
    
    def _analyze_content(self):
        """Analiza el contenido del sitio."""
        # Placeholder - en producción analizaría datos de GA4 y GSC
        self.analysis['contenido'] = {
            'total_pages': 0,
            'pages_with_data': 0,
            'avg_engagement_rate': 0,
            'top_pages': []
        }
    
    def _analyze_technical_seo(self):
        """Analiza SEO técnico."""
        pagespeed_data = self.data.get('pagespeed', {})
        
        self.analysis['seo_tecnico'] = {
            'mobile_score': pagespeed_data.get('mobile', {}).get('score', 0),
            'desktop_score': pagespeed_data.get('desktop', {}).get('score', 0),
            'core_web_vitals': {
                'lcp': pagespeed_data.get('mobile', {}).get('lcp', 0),
                'fid': pagespeed_data.get('mobile', {}).get('fid', 0),
                'cls': pagespeed_data.get('mobile', {}).get('cls', 0)
            },
            'issues': []
        }
    
    def _analyze_user_experience(self):
        """Analiza experiencia de usuario."""
        self.analysis['experiencia_usuario'] = {
            'core_web_vitals': {},
            'mobile_friendly': True,
            'https': True,
            'issues': []
        }
    
    def _analyze_links(self):
        """Analiza enlaces internos y externos."""
        self.analysis['enlaces'] = {
            'internal_links': 0,
            'external_links': 0,
            'backlinks': 0,
            'referring_domains': 0
        }
    
    def _analyze_competition(self):
        """Analiza competencia."""
        self.analysis['competencia'] = {
            'competitors': [],
            'market_share': 0
        }
    
    def _calculate_scores(self):
        """Calcula puntuaciones para cada dimensión."""
        weights = self.config.weights
        scores = {}
        
        # Posicionamiento (25%)
        pos_data = self.analysis.get('posicionamiento', {})
        avg_pos = pos_data.get('avg_position', 50)
        if avg_pos <= 10:
            scores['posicionamiento'] = 90
        elif avg_pos <= 20:
            scores['posicionamiento'] = 70
        elif avg_pos <= 30:
            scores['posicionamiento'] = 50
        else:
            scores['posicionamiento'] = 30
        
        # Palabras clave (20%)
        kw_data = self.analysis.get('palabras_clave', {})
        total_kw = kw_data.get('total_filtered', 0)
        excellent_kw = kw_data.get('summary', {}).get('excellent', 0)
        if total_kw > 0:
            kw_score = min(100, (excellent_kw / total_kw) * 100 + 50)
        else:
            kw_score = 0
        scores['palabras_clave'] = int(kw_score)
        
        # Contenido (15%)
        scores['contenido'] = 60  # Placeholder
        
        # SEO técnico (15%)
        tech_data = self.analysis.get('seo_tecnico', {})
        mobile_score = tech_data.get('mobile_score', 0)
        desktop_score = tech_data.get('desktop_score', 0)
        scores['seo_tecnico'] = int((mobile_score + desktop_score) / 2) if (mobile_score + desktop_score) > 0 else 50
        
        # Experiencia de usuario (10%)
        scores['experiencia_usuario'] = 70  # Placeholder
        
        # Enlaces (10%)
        scores['enlaces'] = 50  # Placeholder
        
        # Competencia (5%)
        scores['competencia'] = 50  # Placeholder
        
        # Calcular puntuación total
        total_score = 0
        for dimension, weight in weights.items():
            total_score += scores.get(dimension, 0) * (weight / 100)
        
        self.scoring = {
            'dimensions': scores,
            'total': int(total_score),
            'weights': weights
        }
    
    def _generate_action_plan(self):
        """Genera plan de acción 30/60/90 días."""
        plan = {
            'phase_30': {
                'title': 'Primeros 30 Días',
                'subtitle': 'Acciones inmediatas de alto impacto',
                'tasks': []
            },
            'phase_60': {
                'title': 'Días 31-60',
                'subtitle': 'Optimizaciones técnicas y de contenido',
                'tasks': []
            },
            'phase_90': {
                'title': 'Días 61-90',
                'subtitle': 'Estrategia a largo plazo',
                'tasks': []
            }
        }
        
        # Generar tareas basadas en el análisis
        pos_data = self.analysis.get('posicionamiento', {})
        if pos_data.get('avg_position', 50) > 20:
            plan['phase_30']['tasks'].append({
                'title': 'Optimizar meta descriptions',
                'description': 'Mejorar descripciones para keywords en posición 11-30',
                'priority': 'p0',
                'effort': 'low'
            })
        
        self.analysis['action_plan'] = plan
    
    def _generate_html_report(self) -> str:
        """Genera el informe HTML completo."""
        # Cargar template base
        template_path = ROOT_DIR / "templates" / "base-audit.html"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Reemplazar variables del template
            html = self._render_template(template)
            return html
        else:
            return self._generate_simple_html()
    
    def _render_template(self, template: str) -> str:
        """Renderiza el template con los datos."""
        scoring = self.scoring
        total_score = scoring.get('total', 0)
        
        # Determinar clase de score
        if total_score >= 90:
            score_class = 'excellent'
            score_label = 'Excelente'
        elif total_score >= 70:
            score_class = 'good'
            score_label = 'Bueno'
        elif total_score >= 50:
            score_class = 'needs-work'
            score_label = 'Necesita Mejoras'
        else:
            score_class = 'critical'
            score_label = 'Crítico'
        
        # Calcular dashoffset para gauge (283 = circumference de un semicírculo de radio 45)
        score_dashoffset = 283 - (283 * total_score / 100)
        
        # Preparar datos para template
        now = datetime.now()
        period_start = now - timedelta(days=self.config.period_days)
        
        replacements = {
            '{{ title }}': f'Auditoría SEO - {self.config.site_name or self.config.site_url}',
            '{{ subtitle }}': f'Análisis completo de posicionamiento web',
            '{{ site_url }}': self.config.site_url,
            '{{ date }}': now.strftime('%d/%m/%Y'),
            '{{ period }}': f'{period_start.strftime("%d/%m/%Y")} - {now.strftime("%d/%m/%Y")}',
            '{{ score }}': str(total_score),
            '{{ score_class }}': score_class,
            '{{ score_dashoffset }}': str(score_dashoffset),
            '{{ score_label }}': score_label,
            '{{ score_description }}': f'Puntuación basada en {len(scoring.get("weights", {}))} dimensiones de análisis',
        }
        
        for key, value in replacements.items():
            template = template.replace(key, value)
        
        return template
    
    def _generate_simple_html(self) -> str:
        """Genera HTML simple como fallback."""
        scoring = self.scoring
        total_score = scoring.get('total', 0)
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoría SEO - {self.config.site_url}</title>
</head>
<body>
    <h1>Auditoría SEO</h1>
    <p>Sitio: {self.config.site_url}</p>
    <p>Puntuación: {total_score}/100</p>
    <pre>{json.dumps(self.analysis, indent=2, ensure_ascii=False)}</pre>
</body>
</html>"""
    
    def _save_output(self, html_content: str):
        """Guarda los archivos de salida."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar HTML
        html_file = output_dir / "audit-report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Guardar datos de análisis como JSON
        analysis_file = output_dir / "analysis-data.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        
        # Guardar scoring como JSON
        scoring_file = output_dir / "scoring-data.json"
        with open(scoring_file, 'w', encoding='utf-8') as f:
            json.dump(self.scoring, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Archivos guardados en: {output_dir}")
    
    # ================================================================
    # DATOS DE EJEMPLO (para testing)
    # ================================================================
    
    def _get_sample_gsc_data(self) -> Dict:
        """Retorna datos de ejemplo de GSC."""
        return {
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
                {'query': 'sito web no funciona', 'clicks': 35, 'impressions': 600, 'ctr': 5.8, 'position': 28},
                {'query': 'error en mi página', 'clicks': 30, 'impressions': 500, 'ctr': 6.0, 'position': 30},
            ]
        }
    
    def _get_sample_ga4_data(self) -> Dict:
        """Retorna datos de ejemplo de GA4."""
        return {
            'sessions': 5000,
            'users': 3500,
            'pageviews': 15000,
            'avg_session_duration': 180,
            'bounce_rate': 45,
            'engagement_rate': 55
        }
    
    def _get_sample_pagespeed_data(self) -> Dict:
        """Retorna datos de ejemplo de PageSpeed."""
        return {
            'mobile': {
                'score': 65,
                'lcp': 3.2,
                'fid': 150,
                'cls': 0.12,
                'fcp': 2.1,
                'tti': 4.5,
                'tbt': 350
            },
            'desktop': {
                'score': 82,
                'lcp': 1.8,
                'fid': 50,
                'cls': 0.05,
                'fcp': 1.2,
                'tti': 2.1,
                'tbt': 120
            }
        }


def load_config(config_path: Optional[str] = None) -> AuditConfig:
    """Carga configuración desde archivo YAML o crea una por defecto."""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return AuditConfig(**config_data)
    return AuditConfig(site_url="https://example.com")


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='SEO Audit Engine')
    parser.add_argument('--site', required=True, help='URL del sitio a auditar')
    parser.add_argument('--name', help='Nombre del sitio')
    parser.add_argument('--output', default='./output', help='Directorio de salida')
    parser.add_argument('--config', help='Archivo de configuración YAML')
    parser.add_argument('--period', type=int, default=28, help='Período en días')
    parser.add_argument('--ga4', help='Property ID de GA4')
    parser.add_argument('--pagespeed-key', help='API key de PageSpeed')
    
    args = parser.parse_args()
    
    # Cargar configuración
    config = load_config(args.config)
    config.site_url = args.site
    config.site_name = args.name or args.site
    config.output_dir = args.output
    config.period_days = args.period
    
    if args.ga4:
        config.ga4_property_id = args.ga4
    if args.pagespeed_key:
        config.pagespeed_api_key = args.pagespeed_key
    
    # Ejecutar auditoría
    engine = AuditEngine(config)
    result = engine.run_full_audit()
    
    print("\n📊 Resumen de la auditoría:")
    print(f"   Puntuación total: {result.get('scoring', {}).get('total', 'N/A')}")
    print(f"   Palabras clave analizadas: {result.get('palabras_clave', {}).get('total_filtered', 0)}")
    print(f"   Informe generado: {config.output_dir}/audit-report.html")


if __name__ == '__main__':
    main()
