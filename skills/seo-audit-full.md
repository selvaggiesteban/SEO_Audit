# SEO Audit Full Skill

## Complete Workflow for AI-Assisted SEO Audits

This skill provides a comprehensive step-by-step guide for performing SEO audits using the SEO Audit Tool project with OpenCode and Google Search Console MCP.

---

## Phase 1: Setup & Authentication

### 1.1 Verify MCP Connection
```bash
# Check that search-console MCP is configured
# Run a simple query to verify authentication
```

Use `search-console_sites_list` to verify connected accounts and sites.

### 1.2 Identify Target Site
- Ask user for the site URL
- Determine GSC URL format:
  - Standard: `https://example.com`
  - Subdomain: `sc-domain:example.com` (for permission issues)
  - Subfolder: `https://example.com/blog/`

### 1.3 Configure Audit Parameters
```yaml
# config/default.yaml
site_url: "https://example.com"
site_name: "Example Site"
period_days: 28
output_dir: "./output/example.com"
```

---

## Phase 2: Data Collection

### 2.1 Google Search Console Data

**Performance Summary:**
```
search-console_analytics_performance_summary
  - siteUrl: <site_url>
  - days: 28
```

**Keyword Data:**
```
search-console_analytics_query
  - siteUrl: <site_url>
  - startDate: <YYYY-MM-DD>
  - endDate: <YYYY-MM-DD>
  - dimensions: ["query"]
  - limit: 1000
```

**Top Pages:**
```
search-console_analytics_top_pages
  - siteUrl: <site_url>
  - days: 28
  - limit: 50
```

**Device Breakdown:**
```
search-console_analytics_query
  - dimensions: ["device"]
```

**Country Data:**
```
search-console_analytics_by_country
  - siteUrl: <site_url>
  - days: 28
```

### 2.2 PageSpeed Insights
```
search-console_pagespeed_core_web_vitals
  - url: <site_url>
```

### 2.3 Save Raw Data
Save all collected data to `output/<site>/raw-data.json` for processing.

---

## Phase 3: Analysis

### 3.1 Run Python Engine
```bash
python src/audit_engine.py \
  --site <site_url> \
  --name "<site_name>" \
  --output ./output/<site_name> \
  --period 28
```

### 3.2 Manual Analysis Checks
If Python engine is not available, perform manual analysis:

**Positioning Analysis:**
- Calculate average position
- Count keywords in Top 3, Top 10, Top 20, Top 30
- Identify trending queries

**Keyword Filtering:**
- Filter by min impressions (default: 10)
- Filter by max position (default: 30)
- Categorize by position range:
  - Excellent: 11-15
  - Good: 16-20
  - Needs Work: 21-30

**Technical SEO:**
- Check mobile vs desktop scores
- Review Core Web Vitals (LCP, FID, CLS)
- Identify render-blocking resources

---

## Phase 4: Scoring

### 4.1 Dimension Scores (0-100)

**Posicionamiento (25%):**
- Avg position ≤10: 90 points
- Avg position ≤20: 70 points
- Avg position ≤30: 50 points
- Avg position >30: 30 points

**Palabras Clave (20%):**
- Score = (excellent_kw / total_kw) * 100 + 50

**Contenido (15%):**
- Based on engagement rate and page performance

**SEO Técnico (15%):**
- Average of mobile and desktop PageSpeed scores

**Experiencia Usuario (10%):**
- Core Web Vitals pass rate

**Enlaces (10%):**
- Internal link structure quality

**Competencia (5%):**
- Market position assessment

### 4.2 Final Score
```
total_score = Σ (dimension_score × weight)
```

### 4.3 Score Labels
| Score | Label | Color |
|-------|-------|-------|
| 90-100 | Excelente | Green |
| 70-89 | Bueno | Blue |
| 50-69 | Necesita Mejoras | Yellow |
| 0-49 | Crítico | Red |

---

## Phase 5: Action Plan

### 5.1 Priority Matrix
| Priority | Impact | Effort | Timeline |
|----------|--------|--------|----------|
| P0 | High | Low | 30 days |
| P1 | High | Medium | 30-60 days |
| P2 | Medium | Medium | 60-90 days |
| P3 | Low | High | 90+ days |

### 5.2 Generate Tasks
For each finding, generate:
- Title (action-oriented)
- Description (specific steps)
- Priority (P0-P3)
- Effort (low/medium/high)
- Timeline (30/60/90 days)

### 5.3 Common Actions

**30 Days (P0-P1):**
- Optimize meta titles and descriptions
- Fix broken links
- Improve page speed for top pages
- Add missing alt text to images

**60 Days (P1-P2):**
- Create content for keyword gaps
- Improve internal linking structure
- Optimize images and media
- Fix mobile usability issues

**90 Days (P2-P3):**
- Build backlink strategy
- Create content cluster strategy
- Implement schema markup
- Improve site architecture

---

## Phase 6: Report Generation

### 6.1 HTML Report
The tool generates a single-page HTML report with:
- Executive summary with score gauge
- 10 analysis sections
- Interactive data tables
- Action plan timeline
- PDF export capability

### 6.2 Report Sections
1. Resumen Ejecutivo
2. Posicionamiento General
3. Análisis de Palabras Clave
4. Análisis de Contenido
5. SEO Técnico
6. Experiencia de Usuario
7. Enlaces y Autoridad
8. Análisis de Competencia
9. Oportunidades
10. Hallazgos y Plan de Acción

### 6.3 Delivery
- HTML file: `audit-report.html`
- JSON data: `analysis-data.json`
- Scoring: `scoring-data.json`

---

## Troubleshooting

### Common Issues

**Permission Error on GSC:**
- Use `sc-domain:example.com` format
- Verify Google account has access

**No Data Returned:**
- Check date range (may need 28+ days)
- Verify site is verified in GSC

**Low Scores:**
- Check PageSpeed API key
- Verify GA4 property ID

### Debug Mode
```bash
python src/audit_engine.py --site <url> --debug
```
