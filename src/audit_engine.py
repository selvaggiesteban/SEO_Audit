"""
SEO Audit Engine - Motor principal de auditorias SEO
=====================================================
Genera informes HTML completos a partir de datos de GSC, GA4 y PageSpeed.

Uso:
    python audit_engine.py --site https://example.com --output ./output
    
    # O con configuracion personalizada
    python audit_engine.py --site https://example.com --config ./config/custom.yaml
"""

import os
import sys
import json
import yaml
import argparse
import html as html_lib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    _HAS_JINJA = True
except ImportError:
    _HAS_JINJA = False

# Agregar directorio raiz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@dataclass
class AuditConfig:
    """Configuracion de la auditoria."""
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
    """Motor principal de auditorias SEO."""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.data = {}
        self.analysis = {}
        self.scoring = {}
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Ejecuta una auditoria completa."""
        print(f"[SEARCH] Iniciando auditoria para: {self.config.site_url}")
        
        # 1. Recopilar datos
        print("[DATA] Recopilando datos de GSC...")
        self._collect_gsc_data()
        
        if self.config.ga4_property_id:
            print("[GA4] Recopilando datos de GA4...")
            self._collect_ga4_data()
        
        if self.config.pagespeed_api_key:
            print("[SPEED] Analizando PageSpeed...")
            self._collect_pagespeed_data()
        
        # 2. Analizar datos
        print("[ANALYZE] Analizando datos...")
        self._analyze_positioning()
        self._analyze_keywords()
        self._analyze_content()
        self._analyze_technical_seo()
        self._analyze_user_experience()
        self._analyze_links()
        self._analyze_competition()
        
        # 3. Calcular puntuacion
        print("[SCORE] Calculando puntuacion...")
        self._calculate_scores()
        
        # 4. Generar plan de accion
        print("[PLAN] Generando plan de accion...")
        self._generate_action_plan()
        
        # 5. Generar informe HTML
        print("[HTML] Generando informe HTML...")
        html_output = self._generate_html_report()
        
        # 6. Guardar archivos
        self._save_output(html_output)
        
        print(f"[OK] Auditoria completada: {self.config.output_dir}")
        return self.analysis
    
    def _collect_gsc_data(self):
        """Recopila datos de Google Search Console."""
        # Si los datos ya fueron inyectados (ej. desde un script externo),
        # respetarlos y no sobrescribirlos.
        if 'gsc' in self.data and self.data['gsc']:
            return

        # En produccion, esto llamaria a la API de GSC
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
        # Placeholder para integracion con GA4
        self.data['ga4'] = self._get_sample_ga4_data()
    
    def _collect_pagespeed_data(self):
        """Recopila datos de PageSpeed Insights."""
        # Si los datos ya fueron inyectados, respetarlos.
        if 'pagespeed' in self.data and self.data['pagespeed']:
            return
        # Placeholder para integracion con PageSpeed API
        self.data['pagespeed'] = self._get_sample_pagespeed_data()
    
    def _analyze_positioning(self):
        """Analiza el posicionamiento general."""
        gsc_data = self.data.get('gsc', {})
        
        total_clicks = gsc_data.get('totalClicks', 0)
        total_impressions = gsc_data.get('totalImpressions', 0)
        avg_ctr = gsc_data.get('averageCTR', 0)
        avg_position = gsc_data.get('averagePosition', 0)
        
        # Distribucion de posiciones
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
                # Determinar rango de posicion
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
        # Placeholder - en produccion analizaria datos de GA4 y GSC
        self.analysis['contenido'] = {
            'total_pages': 0,
            'pages_with_data': 0,
            'avg_engagement_rate': 0,
            'top_pages': []
        }
    
    def _analyze_technical_seo(self):
        """Analiza SEO tecnico."""
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
        """Calcula puntuaciones para cada dimension."""
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
        
        # SEO tecnico (15%)
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
        
        # Calcular puntuacion total
        total_score = 0
        for dimension, weight in weights.items():
            total_score += scores.get(dimension, 0) * (weight / 100)
        
        self.scoring = {
            'dimensions': scores,
            'total': int(total_score),
            'weights': weights
        }
    
    def _generate_action_plan(self):
        """Genera plan de accion 30/60/90 dias basado en todos los analisis."""
        plan = {
            'phase_30': {
                'title': 'Primeros 30 Dias',
                'subtitle': 'Acciones inmediatas de alto impacto',
                'tasks': []
            },
            'phase_60': {
                'title': 'Dias 31-60',
                'subtitle': 'Optimizaciones tecnicas y de contenido',
                'tasks': []
            },
            'phase_90': {
                'title': 'Dias 61-90',
                'subtitle': 'Estrategia a largo plazo',
                'tasks': []
            }
        }

        scores = self.scoring.get('dimensions', {})
        pos_data = self.analysis.get('posicionamiento', {})
        kw_data = self.analysis.get('palabras_clave', {})
        tech_data = self.analysis.get('seo_tecnico', {})

        # === PHASE 30: Acciones inmediatas (P0-P1) ===

        # P0: Posicion promedio baja -> Optimizar meta tags
        if scores.get('posicionamiento', 0) < 70:
            plan['phase_30']['tasks'].append({
                'title': 'Optimizar meta titles y descriptions',
                'description': 'Mejorar titulos y descripciones para keywords en posiciones 11-30. Foco en incrementar CTR en resultados de busqueda.',
                'priority': 'p0',
                'effort': 'low'
            })

        # P0: Keywords en posicion 21-30 -> Quick wins
        needs_work_kws = kw_data.get('summary', {}).get('needs_work', 0)
        if needs_work_kws > 0:
            plan['phase_30']['tasks'].append({
                'title': f'Optimizar {needs_work_kws} keywords en posicion 21-30',
                'description': 'Estas keywords estan a punto de alcanzar la primera pagina. Actualiza el contenido existente para mejorar su relevancia.',
                'priority': 'p0',
                'effort': 'low'
            })

        # P1: CTR bajo -> Mejorar snippets
        avg_ctr = pos_data.get('avg_ctr', 0)
        if avg_ctr < 3:
            plan['phase_30']['tasks'].append({
                'title': 'Mejorar CTR con rich snippets',
                'description': f'El CTR promedio es {avg_ctr:.1f}%. Implementar structured data (Schema.org) para destacar en los resultados de busqueda.',
                'priority': 'p1',
                'effort': 'medium'
            })

        # P1: PageSpeed mobile bajo
        mobile_score = tech_data.get('mobile_score', 0)
        if mobile_score < 60:
            plan['phase_30']['tasks'].append({
                'title': 'Optimizar velocidad mobile (urgente)',
                'description': f'El score movil es {mobile_score}/100. Comprimir imagenes, minificar CSS/JS, y usar lazy loading.',
                'priority': 'p1',
                'effort': 'medium'
            })

        # === PHASE 60: Optimizaciones tecnicas y contenido (P1-P2) ===

        # P1: Keywords en posicion 16-20 -> Push to page 1
        good_kws = kw_data.get('summary', {}).get('good', 0)
        if good_kws > 0:
            plan['phase_60']['tasks'].append({
                'title': f'Empujar {good_kws} keywords de posicion 16-20 a Top 10',
                'description': 'Mejorar la profundidad del contenido y anadir enlaces internos para estas keywords cercanas a la primera pagina.',
                'priority': 'p1',
                'effort': 'medium'
            })

        # P2: PageSpeed desktop
        desktop_score = tech_data.get('desktop_score', 0)
        if desktop_score < 80:
            plan['phase_60']['tasks'].append({
                'title': 'Mejorar PageSpeed desktop',
                'description': f'El score desktop es {desktop_score}/100. Optimizar render-blocking resources y caching.',
                'priority': 'p2',
                'effort': 'medium'
            })

        # P2: Core Web Vitals
        cwv = tech_data.get('core_web_vitals', {})
        lcp = cwv.get('lcp', 0)
        if lcp > 2.5:
            plan['phase_60']['tasks'].append({
                'title': 'Optimizar LCP (Largest Contentful Paint)',
                'description': f'LCP actual: {lcp}s (objetivo: <2.5s). Optimizar imagenes hero, preconnect a dominios externos, y mejorar server response time.',
                'priority': 'p2',
                'effort': 'medium'
            })

        cls = cwv.get('cls', 0)
        if cls > 0.1:
            plan['phase_60']['tasks'].append({
                'title': 'Reducir CLS (Cumulative Layout Shift)',
                'description': f'CLS actual: {cls} (objetivo: <0.1). Asignar dimensiones a imagenes/videos y evitar contenido dinamico above-the-fold.',
                'priority': 'p2',
                'effort': 'low'
            })

        # P2: Pocas keywords en Top 3
        pos_dist = pos_data.get('position_distribution', {})
        top3_count = pos_dist.get('top3', 0)
        total_queries = pos_data.get('total_queries', 0)
        if total_queries > 0 and top3_count < total_queries * 0.2:
            plan['phase_60']['tasks'].append({
                'title': 'Incrementar presencia en Top 3',
                'description': f'Solo {top3_count} de {total_queries} keywords estan en Top 3. Crear contenido de mayor calidad y conseguir backlinks para escalar posiciones.',
                'priority': 'p2',
                'effort': 'medium'
            })

        # === PHASE 90: Estrategia a largo plazo (P2-P3) ===

        # P2: Contenido nuevo para keyword gaps
        if kw_data.get('total_filtered', 0) > 0:
            plan['phase_90']['tasks'].append({
                'title': 'Crear contenido para keyword gaps',
                'description': 'Identificar keywords relevantes sin cobertura y crear articulos/paginas optimizados para capturar trafico nuevo.',
                'priority': 'p2',
                'effort': 'medium'
            })

        # P3: Estrategia de link building
        if scores.get('enlaces', 0) < 70:
            plan['phase_90']['tasks'].append({
                'title': 'Implementar estrategia de link building',
                'description': 'Conseguir backlinks de calidad mediante guest posting, partnerships, y creacion de contenido linkable (guias, infografias, estudios).',
                'priority': 'p3',
                'effort': 'high'
            })

        # P3: Schema markup
        plan['phase_90']['tasks'].append({
            'title': 'Implementar Schema.org completo',
            'description': 'Anadir structured data para Organization, BreadcrumbList, Article/Product, y FAQ segun corresponda al tipo de sitio.',
            'priority': 'p3',
            'effort': 'medium'
        })

        # P3: Arquitectura de informacion
        if total_queries > 10:
            plan['phase_90']['tasks'].append({
                'title': 'Mejorar arquitectura de informacion',
                'description': 'Revisar la estructura del sitio, crear clusters tematicos (pillar pages + supporting content) y optimizar la navegacion interna.',
                'priority': 'p3',
                'effort': 'high'
            })

        self.analysis['action_plan'] = plan
    
    # Mapeo de claves de dimensiones a nombres legibles en espanol
    DIMENSION_NAMES = {
        'posicionamiento': 'Posicionamiento',
        'palabras_clave': 'Palabras Clave',
        'contenido': 'Contenido',
        'seo_tecnico': 'SEO Tecnico',
        'experiencia_usuario': 'Experiencia Usuario',
        'enlaces': 'Enlaces',
        'competencia': 'Competencia',
    }

    def _generate_html_report(self) -> str:
        """Genera el informe HTML completo usando Jinja2 con CSS inlined."""
        templates_dir = ROOT_DIR / "templates"
        template_path = templates_dir / "base-audit.html"

        if not template_path.exists():
            return self._generate_simple_html()

        # Preparar el contexto completo
        context = self._build_template_context()
        css_text = self._read_inlined_css()

        if _HAS_JINJA:
            # Usar Jinja2 para renderizar el template
            env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                keep_trailing_newline=True,
            )
            # Marcar el CSS inlined como seguro (no queremos escaparlo).
            # En Jinja2 3.1+ Markup se mueve a markupsafe; usamos.Markup con fallback.
            try:
                from markupsafe import Markup
            except ImportError:
                from jinja2 import Markup  # type: ignore
            context['inlined_css'] = Markup(f"<style>\n{css_text}\n</style>")

            template = env.get_template("base-audit.html")
            return template.render(**context)
        else:
            # Fallback: leer el template como texto y hacer reemplazos simples
            # sustituyendo los bloques <link rel="stylesheet"> por <style>
            with open(template_path, 'r', encoding='utf-8') as f:
                template_str = f.read()
            # Sustituir los link tags por un unico style inlined
            import re as _re
            template_str = _re.sub(
                r'<link\s+rel="stylesheet"[^>]*>\s*',
                f'<style>\n{css_text}\n</style>\n',
                template_str,
                count=1,
            )
            template_str = _re.sub(r'<link\s+rel="stylesheet"[^>]*>\s*', '', template_str)
            # Reemplazos simples
            for key, value in context.items():
                if key == 'inlined_css':
                    continue
                template_str = template_str.replace('{{ ' + key + ' }}', str(value))
            return template_str

    def _read_inlined_css(self) -> str:
        """Lee y concatena todos los archivos CSS para inlining."""
        css_files = [
            "css/tokens.css",
            "css/base.css",
            "css/components/card.css",
            "css/components/stat-box.css",
            "css/components/badges.css",
            "css/components/table.css",
            "css/components/cta.css",
            "css/components/findings.css",
            "css/components/score-gauge.css",
            "css/components/plan-timeline.css",
        ]
        chunks = []
        css_root = ROOT_DIR
        for rel in css_files:
            path = css_root / rel
            if path.exists():
                try:
                    chunks.append(f"/* ===== {rel} ===== */")
                    chunks.append(path.read_text(encoding='utf-8'))
                    chunks.append("")
                except Exception:
                    pass
        return "\n".join(chunks)

    def _build_template_context(self) -> Dict[str, Any]:
        """Construye el contexto completo para el template Jinja2."""
        scoring = self.scoring
        total_score = scoring.get('total', 0)

        # Clase de score global
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
            score_label = 'Critico'

        # dashoffset para gauge (283 = circunferencia de un semicirculo de radio 45)
        score_dashoffset = int(283 - (283 * total_score / 100))

        now = datetime.now()
        period_start = now - timedelta(days=self.config.period_days)

        context = {
            'title': f"Auditoria SEO - {self.config.site_name or self.config.site_url}",
            'subtitle': 'Analisis completo de posicionamiento web',
            'site_url': self.config.site_url,
            'date': now.strftime('%d/%m/%Y'),
            'period': f'{period_start.strftime("%d/%m/%Y")} - {now.strftime("%d/%m/%Y")}',
            'score': str(total_score),
            'score_class': score_class,
            'score_dashoffset': str(score_dashoffset),
            'score_label': score_label,
            'score_description': f'Puntuacion basada en {len(scoring.get("weights", {}))} dimensiones de analisis',
            'dimensions': self._build_dimensions_data(),
            'stats': self._build_stats_data(),
            'sections': self._build_sections_data(),
            'action_plan': self._build_action_plan_data(),
        }
        return context

    @staticmethod
    def _score_to_class(score) -> str:
        """Convierte un valor numerico de score en una clase CSS."""
        try:
            s = int(score)
        except (TypeError, ValueError):
            s = 0
        if s >= 90:
            return 'excellent'
        elif s >= 70:
            return 'good'
        elif s >= 50:
            return 'needs-work'
        else:
            return 'critical'

    def _build_dimensions_data(self) -> List[Dict[str, Any]]:
        """Construye la lista de dimensiones para el score breakdown."""
        scoring = self.scoring
        weights = scoring.get('weights', {})
        dim_scores = scoring.get('dimensions', {})
        dimensions = []
        # Mantener el orden canonico de las dimensiones
        order = [
            'posicionamiento', 'palabras_clave', 'contenido', 'seo_tecnico',
            'experiencia_usuario', 'enlaces', 'competencia',
        ]
        for key in order:
            if key not in weights and key not in dim_scores:
                continue
            dimensions.append({
                'name': self.DIMENSION_NAMES.get(key, key),
                'weight': int(weights.get(key, 0)),
                'score': int(dim_scores.get(key, 0)),
                'score_class': self._score_to_class(dim_scores.get(key, 0)),
            })
        return dimensions

    def _build_stats_data(self) -> List[Dict[str, Any]]:
        """Construye las cajas de KPI (stats) desde el analisis de posicionamiento."""
        pos = self.analysis.get('posicionamiento', {})
        kw = self.analysis.get('palabras_clave', {})

        total_clicks = pos.get('total_clicks', 0)
        total_impressions = pos.get('total_impressions', 0)
        avg_ctr = pos.get('avg_ctr', 0)
        avg_position = pos.get('avg_position', 0)
        total_queries = pos.get('total_queries', 0)
        total_filtered = kw.get('total_filtered', 0)

        def cls_for_position(p):
            try:
                pv = float(p)
            except (TypeError, ValueError):
                return 'stat-warning'
            return 'stat-success' if pv <= 15 else ('stat-warning' if pv <= 30 else 'stat-danger')

        def cls_for_ctr(c):
            try:
                cv = float(c)
            except (TypeError, ValueError):
                return 'stat-warning'
            return 'stat-success' if cv >= 3.0 else ('stat-warning' if cv >= 1.0 else 'stat-danger')

        stats = [
            {
                'value': f'{int(total_clicks):,}',
                'label': 'Clicks Totales',
                'class': 'stat-success' if total_clicks > 0 else 'stat-danger',
            },
            {
                'value': f'{int(total_impressions):,}',
                'label': 'Impresiones Totales',
                'class': 'stat-success' if total_impressions > 0 else 'stat-danger',
            },
            {
                'value': f'{avg_ctr:.2f}%',
                'label': 'CTR Promedio',
                'class': cls_for_ctr(avg_ctr),
            },
            {
                'value': f'{avg_position:.1f}',
                'label': 'Posicion Promedio',
                'class': cls_for_position(avg_position),
            },
            {
                'value': f'{int(total_queries):,}',
                'label': 'Queries Totales',
                'class': 'stat-info' if total_queries > 0 else 'stat-danger',
            },
            {
                'value': f'{int(total_filtered):,}',
                'label': 'Keywords Filtradas',
                'class': 'stat-success' if total_filtered > 0 else 'stat-warning',
            },
        ]
        return stats

    @staticmethod
    def _esc(text) -> str:
        """Escapa texto para HTML."""
        return html_lib.escape(str(text), quote=True)

    def _build_sections_data(self) -> List[Dict[str, str]]:
        """Construye las 10 secciones de contenido del informe."""
        sections = []

        # 1. Resumen Ejecutivo
        sections.append({
            'icon': '[PLAN]',
            'title': 'Resumen Ejecutivo',
            'content': self._section_executive_summary(),
        })
        # 2. Posicionamiento General
        sections.append({
            'icon': '[DATA]',
            'title': 'Posicionamiento General',
            'content': self._section_positioning(),
        })
        # 3. Analisis de Palabras Clave
        sections.append({
            'icon': '[SEARCH]',
            'title': 'Analisis de Palabras Clave',
            'content': self._section_keywords(),
        })
        # 4. Analisis de Contenido
        sections.append({
            'icon': '[HTML]',
            'title': 'Analisis de Contenido',
            'content': self._section_content(),
        })
        # 5. SEO Tecnico
        sections.append({
            'icon': '[GEAR]',
            'title': 'SEO Tecnico',
            'content': self._section_technical(),
        })
        # 6. Experiencia de Usuario
        sections.append({
            'icon': '[USERS]',
            'title': 'Experiencia de Usuario',
            'content': self._section_ux(),
        })
        # 7. Enlaces y Autoridad
        sections.append({
            'icon': '[LINK]',
            'title': 'Enlaces y Autoridad',
            'content': self._section_links(),
        })
        # 8. Analisis de Competencia
        sections.append({
            'icon': '[SCORE]',
            'title': 'Analisis de Competencia',
            'content': self._section_competition(),
        })
        # 9. Oportunidades
        sections.append({
            'icon': '[IDEA]',
            'title': 'Oportunidades',
            'content': self._section_opportunities(),
        })
        # 10. Hallazgos
        sections.append({
            'icon': '[WARN]',
            'title': 'Hallazgos',
            'content': self._section_findings(),
        })
        return sections

    @staticmethod
    def _empty_section() -> str:
        return '<p class="text-muted">No hay datos disponibles para esta seccion.</p>'

    def _section_executive_summary(self) -> str:
        scoring = self.scoring
        dims = scoring.get('dimensions', {})
        if not dims:
            return self._empty_section()
        # Mejor y peor dimension
        items = [(k, v) for k, v in dims.items()]
        items.sort(key=lambda x: x[1], reverse=True)
        best_key, best_score = items[0]
        worst_key, worst_score = items[-1]
        best_name = self.DIMENSION_NAMES.get(best_key, best_key)
        worst_name = self.DIMENSION_NAMES.get(worst_key, worst_key)
        pos = self.analysis.get('posicionamiento', {})
        total_clicks = pos.get('total_clicks', 0)
        total_impressions = pos.get('total_impressions', 0)
        html = []
        html.append('<div class="table-container"><table class="data-table">')
        html.append('<thead><tr><th>Metrica</th><th>Valor</th></tr></thead>')
        html.append('<tbody>')
        html.append(f'<tr><td class="query-text">Puntuacion Total</td><td><span class="score-badge {self._score_to_class(scoring.get("total", 0))}">{scoring.get("total", 0)}</span></td></tr>')
        html.append(f'<tr><td class="query-text">Clicks Totales</td><td class="impressions">{int(total_clicks):,}</td></tr>')
        html.append(f'<tr><td class="query-text">Impresiones Totales</td><td class="impressions">{int(total_impressions):,}</td></tr>')
        html.append(f'<tr><td class="query-text">Mejor Dimension</td><td>{self._esc(best_name)} ({best_score}/100)</td></tr>')
        html.append(f'<tr><td class="query-text">Dimension a Mejorar</td><td>{self._esc(worst_name)} ({worst_score}/100)</td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_positioning(self) -> str:
        pos = self.analysis.get('posicionamiento', {})
        dist = pos.get('position_distribution', {})
        if not dist:
            return self._empty_section()
        rows = [
            ('Top 3', dist.get('top3', 0)),
            ('Top 4-10', dist.get('top10', 0)),
            ('Top 11-20', dist.get('top20', 0)),
            ('Top 21-30', dist.get('top30', 0)),
            ('Mas alla de 30', dist.get('beyond30', 0)),
        ]
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Rango de Posicion</th><th>Queries</th></tr></thead>')
        html.append('<tbody>')
        for label, count in rows:
            badge_cls = self._score_to_class(100 if label == 'Top 3' else (85 if 'Top 4-10' in label else (60 if '11-20' in label else (30 if '21-30' in label else 10))))
            html.append(f'<tr><td class="query-text">{self._esc(label)}</td><td><span class="position-badge {badge_cls}">{int(count)}</span></td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_keywords(self) -> str:
        kw = self.analysis.get('palabras_clave', {})
        keywords = kw.get('keywords', [])
        if not keywords:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Keyword</th><th>Clicks</th><th>Impresiones</th><th>CTR</th><th>Posicion</th></tr></thead>')
        html.append('<tbody>')
        for k in keywords:
            pos_cls = k.get('position_class', 'needs-work')
            html.append(
                f'<tr><td class="query-text">{self._esc(k.get("query", ""))}</td>'
                f'<td>{int(k.get("clicks", 0))}</td>'
                f'<td class="impressions">{int(k.get("impressions", 0)):,}</td>'
                f'<td>{k.get("ctr", 0):.2f}%</td>'
                f'<td><span class="position-badge {pos_cls}">{k.get("position", 0):.1f}</span></td></tr>'
            )
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_content(self) -> str:
        content = self.analysis.get('contenido', {})
        pages = content.get('top_pages', [])
        if not pages:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Pagina</th><th>Clicks</th><th>Impresiones</th><th>CTR</th><th>Posicion</th></tr></thead>')
        html.append('<tbody>')
        for p in pages:
            html.append(
                f'<tr><td class="query-text">{self._esc(p.get("page", ""))}</td>'
                f'<td>{int(p.get("clicks", 0))}</td>'
                f'<td class="impressions">{int(p.get("impressions", 0)):,}</td>'
                f'<td>{p.get("ctr", 0):.2f}%</td>'
                f'<td>{p.get("position", 0):.1f}</td></tr>'
            )
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_technical(self) -> str:
        tech = self.analysis.get('seo_tecnico', {})
        mobile = tech.get('mobile_score', 0)
        desktop = tech.get('desktop_score', 0)
        cwv = tech.get('core_web_vitals', {})
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Metrica</th><th>Valor</th></tr></thead>')
        html.append('<tbody>')
        html.append(f'<tr><td class="query-text">Mobile Score</td><td><span class="score-badge {self._score_to_class(mobile)}">{int(mobile)}</span></td></tr>')
        html.append(f'<tr><td class="query-text">Desktop Score</td><td><span class="score-badge {self._score_to_class(desktop)}">{int(desktop)}</span></td></tr>')
        lcp = cwv.get('lcp', 0)
        cls = cwv.get('cls', 0)
        fid = cwv.get('fid', 0)
        html.append(f'<tr><td class="query-text">LCP (Largest Contentful Paint)</td><td>{lcp}s</td></tr>')
        html.append(f'<tr><td class="query-text">CLS (Cumulative Layout Shift)</td><td>{cls}</td></tr>')
        html.append(f'<tr><td class="query-text">FID (First Input Delay)</td><td>{int(fid)}ms</td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_ux(self) -> str:
        ux = self.analysis.get('experiencia_usuario', {})
        if not ux:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Metrica</th><th>Valor</th></tr></thead>')
        html.append('<tbody>')
        html.append(f'<tr><td class="query-text">HTTPS Habilitado</td><td>{"Si" if ux.get("https") else "No"}</td></tr>')
        html.append(f'<tr><td class="query-text">Mobile Friendly</td><td>{"Si" if ux.get("mobile_friendly") else "No"}</td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_links(self) -> str:
        links = self.analysis.get('enlaces', {})
        if not links:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Metrica</th><th>Valor</th></tr></thead>')
        html.append('<tbody>')
        html.append(f'<tr><td class="query-text">Enlaces Internos</td><td>{int(links.get("internal_links", 0))}</td></tr>')
        html.append(f'<tr><td class="query-text">Enlaces Externos</td><td>{int(links.get("external_links", 0))}</td></tr>')
        html.append(f'<tr><td class="query-text">Backlinks</td><td>{int(links.get("backlinks", 0))}</td></tr>')
        html.append(f'<tr><td class="query-text">Dominios Referentes</td><td>{int(links.get("referring_domains", 0))}</td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_competition(self) -> str:
        comp = self.analysis.get('competencia', {})
        competitors = comp.get('competitors', [])
        if not competitors:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Competidor</th><th>Market Share</th></tr></thead>')
        html.append('<tbody>')
        for c in competitors:
            name = c.get('name', c.get('competitor', 'N/A')) if isinstance(c, dict) else str(c)
            share = c.get('market_share', 0) if isinstance(c, dict) else 0
            html.append(f'<tr><td class="query-text">{self._esc(str(name))}</td><td>{share}%</td></tr>')
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_opportunities(self) -> str:
        kw = self.analysis.get('palabras_clave', {})
        keywords = kw.get('keywords', [])
        # Oportunidades: keywords con impresiones altas pero posicion > 10
        opps = [k for k in keywords if k.get('impressions', 0) >= 50 and k.get('position', 0) > 10]
        if not opps:
            return self._empty_section()
        html = ['<div class="table-container"><table class="data-table">']
        html.append('<thead><tr><th>Keyword</th><th>Impresiones</th><th>Posicion Actual</th><th>Oportunidad</th></tr></thead>')
        html.append('<tbody>')
        for k in opps[:15]:
            pos = k.get('position', 0)
            opp = 'Mejorar a Top 10' if pos <= 20 else 'Mejorar a Top 20'
            pos_cls = k.get('position_class', 'needs-work')
            html.append(
                f'<tr><td class="query-text">{self._esc(k.get("query", ""))}</td>'
                f'<td class="impressions">{int(k.get("impressions", 0)):,}</td>'
                f'<td><span class="position-badge {pos_cls}">{pos:.1f}</span></td>'
                f'<td><span class="relevance-tag high">{opp}</span></td></tr>'
            )
        html.append('</tbody></table></div>')
        return ''.join(html)

    def _section_findings(self) -> str:
        findings = []
        pos = self.analysis.get('posicionamiento', {})
        avg_pos = pos.get('avg_position', 0)
        avg_ctr = pos.get('avg_ctr', 0)
        kw = self.analysis.get('palabras_clave', {})
        total_filtered = kw.get('total_filtered', 0)
        tech = self.analysis.get('seo_tecnico', {})
        mobile_score = tech.get('mobile_score', 0)

        if avg_pos > 20:
            findings.append(('critical', 'Posicion promedio baja',
                             f'La posicion promedio es {avg_pos:.1f}, por encima del Top 20.'))
        elif avg_pos > 10:
            findings.append(('high', 'Posicion promedio a mejorar',
                             f'La posicion promedio es {avg_pos:.1f}.'))
        else:
            findings.append(('pass', 'Posicion promedio saludable',
                             f'La posicion promedio es {avg_pos:.1f}, dentro del Top 10.'))

        if avg_ctr < 1.0:
            findings.append(('critical', 'CTR muy bajo',
                             f'El CTR promedio es {avg_ctr:.2f}%.'))
        elif avg_ctr < 3.0:
            findings.append(('high', 'CTR por debajo del optimo',
                             f'El CTR promedio es {avg_ctr:.2f}%.'))
        else:
            findings.append(('pass', 'CTR saludable',
                             f'El CTR promedio es {avg_ctr:.2f}%.'))

        if total_filtered == 0:
            findings.append(('high', 'Sin keywords filtradas',
                             'No hay keywords que cumplan los filtros de impresiones/posicion.'))
        else:
            findings.append(('pass', 'Keywords relevantes detectadas',
                             f'{total_filtered} keywords cumplen los criterios de analisis.'))

        if mobile_score < 50:
            findings.append(('critical', 'Mobile Score critico',
                             f'PageSpeed mobile score: {mobile_score}/100.'))
        elif mobile_score < 70:
            findings.append(('high', 'Mobile Score a mejorar',
                             f'PageSpeed mobile score: {mobile_score}/100.'))
        else:
            findings.append(('pass', 'Mobile Score aceptable',
                             f'PageSpeed mobile score: {mobile_score}/100.'))

        if not findings:
            return self._empty_section()

        html = ['<div class="findings-grid">']
        for sev, title, desc in findings:
            html.append(
                f'<div class="finding-card {sev}">'
                f'<div class="severity"><span class="severity-badge {sev}">{sev.upper()}</span></div>'
                f'<h4>{self._esc(title)}</h4>'
                f'<p>{self._esc(desc)}</p>'
                f'</div>'
            )
        html.append('</div>')
        return ''.join(html)

    def _build_action_plan_data(self) -> List[Dict[str, Any]]:
        """Construye el plan de accion 30/60/90 para el template."""
        plan = self.analysis.get('action_plan', {})
        if not plan:
            return []

        # Mapeo de prioridad a etiqueta legible
        priority_labels = {
            'p0': 'P0 - Critico',
            'p1': 'P1 - Alto',
            'p2': 'P2 - Medio',
            'p3': 'P3 - Bajo',
        }
        effort_labels = {
            'low': 'Bajo esfuerzo',
            'medium': 'Esfuerzo medio',
            'high': 'Alto esfuerzo',
        }

        phases_keys = ['phase_30', 'phase_60', 'phase_90']
        badges = ['30 DIAS', '60 DIAS', '90 DIAS']
        result = []
        for idx, key in enumerate(phases_keys):
            phase = plan.get(key)
            if not phase:
                continue
            tasks_out = []
            for t in phase.get('tasks', []):
                priority = t.get('priority', 'p2')
                effort = t.get('effort', 'medium')
                tasks_out.append({
                    'title': t.get('title', ''),
                    'description': t.get('description', ''),
                    'priority': priority,
                    'priority_label': priority_labels.get(priority, priority.upper()),
                    'effort': effort,
                    'effort_label': effort_labels.get(effort, effort),
                })
            result.append({
                'class': 'active' if idx == 0 else '',
                'badge': badges[idx],
                'title': phase.get('title', ''),
                'subtitle': phase.get('subtitle', ''),
                'tasks': tasks_out,
            })
        return result
    
    def _generate_simple_html(self) -> str:
        """Genera HTML simple como fallback."""
        scoring = self.scoring
        total_score = scoring.get('total', 0)
        
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria SEO - {self.config.site_url}</title>
</head>
<body>
    <h1>Auditoria SEO</h1>
    <p>Sitio: {self.config.site_url}</p>
    <p>Puntuacion: {total_score}/100</p>
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
        
        # Guardar datos de analisis como JSON
        analysis_file = output_dir / "analysis-data.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis, f, indent=2, ensure_ascii=False)
        
        # Guardar scoring como JSON
        scoring_file = output_dir / "scoring-data.json"
        with open(scoring_file, 'w', encoding='utf-8') as f:
            json.dump(self.scoring, f, indent=2, ensure_ascii=False)
        
        print(f"[FOLDER] Archivos guardados en: {output_dir}")
    
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
                {'query': 'recuperar pagina web', 'clicks': 120, 'impressions': 2500, 'ctr': 4.8, 'position': 12},
                {'query': 'restaurar sitio web', 'clicks': 95, 'impressions': 1800, 'ctr': 5.3, 'position': 14},
                {'query': 'como recuperar mi pagina', 'clicks': 85, 'impressions': 1500, 'ctr': 5.7, 'position': 16},
                {'query': 'recuperacion de pagina web', 'clicks': 75, 'impressions': 1200, 'ctr': 6.3, 'position': 18},
                {'query': 'mi pagina web no carga', 'clicks': 65, 'impressions': 1000, 'ctr': 6.5, 'position': 20},
                {'query': 'problemas con mi sitio web', 'clicks': 55, 'impressions': 900, 'ctr': 6.1, 'position': 22},
                {'query': 'arreglar pagina web', 'clicks': 45, 'impressions': 800, 'ctr': 5.6, 'position': 24},
                {'query': 'pagina web caida', 'clicks': 40, 'impressions': 700, 'ctr': 5.7, 'position': 26},
                {'query': 'sito web no funciona', 'clicks': 35, 'impressions': 600, 'ctr': 5.8, 'position': 28},
                {'query': 'error en mi pagina', 'clicks': 30, 'impressions': 500, 'ctr': 6.0, 'position': 30},
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
    """Carga configuracion desde archivo YAML o crea una por defecto."""
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
    parser.add_argument('--config', help='Archivo de configuracion YAML')
    parser.add_argument('--period', type=int, default=28, help='Periodo en dias')
    parser.add_argument('--ga4', help='Property ID de GA4')
    parser.add_argument('--pagespeed-key', help='API key de PageSpeed')
    
    args = parser.parse_args()
    
    # Cargar configuracion
    config = load_config(args.config)
    config.site_url = args.site
    config.site_name = args.name or args.site
    config.output_dir = args.output
    config.period_days = args.period
    
    if args.ga4:
        config.ga4_property_id = args.ga4
    if args.pagespeed_key:
        config.pagespeed_api_key = args.pagespeed_key
    
    # Ejecutar auditoria
    engine = AuditEngine(config)
    result = engine.run_full_audit()
    
    print("\n[DATA] Resumen de la auditoria:")
    print(f"   Puntuacion total: {result.get('scoring', {}).get('total', 'N/A')}")
    print(f"   Palabras clave analizadas: {result.get('palabras_clave', {}).get('total_filtered', 0)}")
    print(f"   Informe generado: {config.output_dir}/audit-report.html")


if __name__ == '__main__':
    main()
