"""
Positioning Analyzer - Analizador de posicionamiento SEO
=========================================================
Analiza el posicionamiento general y distribución de rankings.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class PositioningAnalysis:
    """Resultado del análisis de posicionamiento."""
    total_clicks: int
    total_impressions: int
    avg_ctr: float
    avg_position: float
    total_queries: int
    position_distribution: Dict[str, int]
    top_keywords: List[Dict[str, Any]]
    score: int
    findings: List[Dict[str, Any]]


class PositioningAnalyzer:
    """Analizador de posicionamiento SEO."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el analizador.
        
        Args:
            config: Configuración del análisis
        """
        self.config = config or {}
        self.position_ranges = self.config.get('position_ranges', {
            'top3': {'min': 1, 'max': 3},
            'top10': {'min': 4, 'max': 10},
            'top20': {'min': 11, 'max': 20},
            'top30': {'min': 21, 'max': 30},
            'beyond30': {'min': 31, 'max': 100}
        })
    
    def analyze(self, gsc_data: Dict[str, Any]) -> PositioningAnalysis:
        """
        Analiza el posicionamiento general.
        
        Args:
            gsc_data: Datos de Google Search Console
            
        Returns:
            PositioningAnalysis con los resultados
        """
        total_clicks = gsc_data.get('totalClicks', 0)
        total_impressions = gsc_data.get('totalImpressions', 0)
        avg_ctr = gsc_data.get('averageCTR', 0)
        avg_position = gsc_data.get('averagePosition', 0)
        
        queries = gsc_data.get('queries', [])
        
        # Calcular distribución de posiciones
        position_dist = self._calculate_position_distribution(queries)
        
        # Obtener top keywords
        top_keywords = self._get_top_keywords(queries, limit=20)
        
        # Calcular puntuación
        score = self._calculate_score(
            avg_position=avg_position,
            avg_ctr=avg_ctr,
            position_dist=position_dist
        )
        
        # Generar hallazgos
        findings = self._generate_findings(
            avg_position=avg_position,
            avg_ctr=avg_ctr,
            position_dist=position_dist,
            total_queries=len(queries)
        )
        
        return PositioningAnalysis(
            total_clicks=total_clicks,
            total_impressions=total_impressions,
            avg_ctr=avg_ctr,
            avg_position=avg_position,
            total_queries=len(queries),
            position_distribution=position_dist,
            top_keywords=top_keywords,
            score=score,
            findings=findings
        )
    
    def _calculate_position_distribution(self, queries: List[Dict]) -> Dict[str, int]:
        """Calcula la distribución de posiciones."""
        dist = {
            'top3': 0,
            'top10': 0,
            'top20': 0,
            'top30': 0,
            'beyond30': 0
        }
        
        for q in queries:
            pos = q.get('position', 0)
            
            if pos <= self.position_ranges['top3']['max']:
                dist['top3'] += 1
            elif pos <= self.position_ranges['top10']['max']:
                dist['top10'] += 1
            elif pos <= self.position_ranges['top20']['max']:
                dist['top20'] += 1
            elif pos <= self.position_ranges['top30']['max']:
                dist['top30'] += 1
            else:
                dist['beyond30'] += 1
        
        return dist
    
    def _get_top_keywords(
        self,
        queries: List[Dict],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Obtiene las keywords principales por impresiones."""
        sorted_queries = sorted(
            queries,
            key=lambda x: x.get('impressions', 0),
            reverse=True
        )[:limit]
        
        return [
            {
                'query': q.get('query', ''),
                'clicks': q.get('clicks', 0),
                'impressions': q.get('impressions', 0),
                'ctr': q.get('ctr', 0),
                'position': q.get('position', 0)
            }
            for q in sorted_queries
        ]
    
    def _calculate_score(
        self,
        avg_position: float,
        avg_ctr: float,
        position_dist: Dict[str, int]
    ) -> int:
        """
        Calcula la puntuación de posicionamiento (0-100).
        
        Factores:
        - Posición promedio (40%)
        - Distribución de posiciones (30%)
        - CTR promedio (30%)
        """
        # Puntuación por posición promedio (40%)
        if avg_position <= 5:
            pos_score = 100
        elif avg_position <= 10:
            pos_score = 85
        elif avg_position <= 15:
            pos_score = 70
        elif avg_position <= 20:
            pos_score = 55
        elif avg_position <= 30:
            pos_score = 40
        else:
            pos_score = 20
        
        # Puntuación por distribución (30%)
        total = sum(position_dist.values())
        if total > 0:
            top10_pct = (position_dist.get('top3', 0) + position_dist.get('top10', 0)) / total
            top20_pct = (position_dist.get('top20', 0)) / total
            
            dist_score = (top10_pct * 60) + (top20_pct * 40)
            dist_score = min(100, dist_score * 100)
        else:
            dist_score = 0
        
        # Puntuación por CTR (30%)
        if avg_ctr >= 5:
            ctr_score = 100
        elif avg_ctr >= 3:
            ctr_score = 75
        elif avg_ctr >= 2:
            ctr_score = 50
        elif avg_ctr >= 1:
            ctr_score = 30
        else:
            ctr_score = 10
        
        # Puntuación total ponderada
        total_score = (pos_score * 0.4) + (dist_score * 0.3) + (ctr_score * 0.3)
        
        return int(min(100, max(0, total_score)))
    
    def _generate_findings(
        self,
        avg_position: float,
        avg_ctr: float,
        position_dist: Dict[str, int],
        total_queries: int
    ) -> List[Dict[str, Any]]:
        """Genera hallazgos basados en el análisis."""
        findings = []
        
        # Hallazgo: Posición promedio
        if avg_position > 20:
            findings.append({
                'severity': 'critical',
                'title': 'Posición promedio baja',
                'description': f'La posición promedio es {avg_position:.1f}, lo que indica que las páginas aparecen en la segunda página de resultados.',
                'recommendation': 'Enfócate en optimizar keywords con posiciones 11-30 para llevarlas a la primera página.'
            })
        elif avg_position > 15:
            findings.append({
                'severity': 'high',
                'title': 'Posición promedio mejorable',
                'description': f'La posición promedio es {avg_position:.1f}. Hay espacio para mejorar hacia la primera página.',
                'recommendation': 'Optimiza el contenido y enlaces internos para keywords cercanas a la primera página.'
            })
        
        # Hallazgo: CTR bajo
        if avg_ctr < 2:
            findings.append({
                'severity': 'high',
                'title': 'CTR promedio bajo',
                'description': f'El CTR promedio es {avg_ctr:.1f}%, lo que indica que los títulos y descripciones no son atractivos.',
                'recommendation': 'Mejora los meta títulos y descripciones para hacerlos más clickeables.'
            })
        
        # Hallazgo: Distribución
        total = sum(position_dist.values())
        if total > 0:
            top3_pct = position_dist.get('top3', 0) / total * 100
            if top3_pct < 5:
                findings.append({
                    'severity': 'medium',
                    'title': 'Pocas keywords en Top 3',
                    'description': f'Solo el {top3_pct:.1f}% de las keywords están en las primeras 3 posiciones.',
                    'recommendation': 'Identifica las keywords con mayor potencial y optimízalas para alcanzar el Top 3.'
                })
        
        return findings
