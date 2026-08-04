# SEO Audit Tool

Herramienta profesional de auditoría SEO con 10 dimensiones de análisis, scoring ponderado y plan de acción automático 30/60/90 días.

## Características

- **10 dimensiones de auditoría** con 200+ checks
- **Scoring ponderado** por categoría (0-100 puntos)
- **Plan de acción automático** con prioridades P0-P3
- **Informe HTML premium** con diseño web profesional
- **Integración con Google Search Console** y Google Analytics 4
- **Análisis de Core Web Vitals** via PageSpeed Insights API
- **AI Search Readiness** - Visibilidad en ChatGPT, Perplexity, AI Overviews

## Instalación

```bash
git clone https://github.com/selvaggiesteban/SEO_Audit.git
cd SEO_Audit
pip install -r requirements.txt
```

## Uso Rápido

### Auditoría básica (solo crawl)

```bash
python -m src.audit_engine --url https://example.com --output report.html
```

### Auditoría con Google Search Console

```bash
python -m src.audit_engine --url https://example.com --gsc --output report.html
```

### Auditoría completa (GSC + GA4 + PageSpeed)

```bash
python -m src.audit_engine --url https://example.com --gsc --ga4 --pagespeed --output report.html
```

## Estructura del Informe

| # | Sección | Descripción |
|---|---------|-------------|
| 1 | Resumen Ejecutivo | Score total, top 5 hallazgos, KPIs clave |
| 2 | AI Search Readiness | Visibilidad en IA (ChatGPT, Perplexity, AI Overviews) |
| 3 | Rastreabilidad e Indexación | Robots.txt, sitemap, indexación, crawl budget |
| 4 | On-Page SEO | Titles, metas, H1-H6, canonical, hreflang |
| 5 | Core Web Vitals | LCP, INP, CLS, FCP, TBT |
| 6 | Enlaces Internos | Estructura de enlaces, profundidad, huérfanos |
| 7 | Schema & Datos Estructurados | JSON-LD, Rich Results, validación |
| 8 | Perfil de Backlinks | Dominios referentes, toxicidad, ancla |
| 9 | Calidad de Contenido | Thin content, canibalización, freshness |
| 10 | Plan de Acción 30/60/90 | Priorizado P0-P3 con impacto estimado |

## Sistema de Scoring

| Dimensión | Peso | Checks |
|-----------|------|--------|
| Rastreabilidad | 20% | 42 |
| On-Page SEO | 18% | 38 |
| Core Web Vitals | 15% | 28 |
| Enlaces Internos | 12% | 22 |
| Schema | 10% | 18 |
| Backlinks | 10% | 24 |
| Calidad de Contenido | 8% | 16 |
| AI Readiness | 7% | 14 |

### Categorías de Score

- **90-100**: Excelente (verde)
- **70-89**: Bueno (azul)
- **50-69**: Necesita mejoras (amarillo)
- **0-49**: Crítico (rojo)

## Matrix de Priorización

| Prioridad | Impacto | Esfuerzo | Acción |
|-----------|---------|----------|--------|
| **P0 - Ahora** | Alto | Bajo | Ship this week |
| **P1 - Sprint** | Alto | Medio | Next sprint |
| **P2 - Backlog** | Medio | Medio | This quarter |
| **P3 - Monitorear** | Bajo | Alto | When convenient |

## Uso como Skill de opencode

Agregar a `opencode.jsonc`:

```json
{
  "mcp": {
    "seo-audit": {
      "type": "local",
      "command": ["python", "-m", "src.audit_engine"],
      "enabled": true
    }
  }
}
```

Luego usar:

```
Auditoría SEO completa de https://example.com
```

## Configuración

Los pesos y thresholds se pueden configurar en `config/weights.yaml`:

```yaml
scoring:
  dimensions:
    crawlability: { weight: 0.20, checks: 42 }
    onpage: { weight: 0.18, checks: 38 }
    # ... más dimensiones
```

## Dependencias

- Python 3.9+
- requests
- beautifulsoup4
- lxml
- pyyaml
- jinja2
- google-api-python-client (opcional, para GSC)
- google-auth (opcional, para GSC)

## Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

## Autor

**Esteban Selvaggi** - [selvaggiesteban.dev](https://selvaggiesteban.dev)

Ingeniero en Informática especializado en Ingeniería de Software con más de 10 años de experiencia en desarrollo web, SEO y automatización.
