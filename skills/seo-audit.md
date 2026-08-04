# SEO Audit Skill

## Overview
This skill guides an AI agent through performing a complete SEO audit using the SEO Audit Tool project. It connects to Google Search Console MCP, analyzes site data, and generates an HTML report.

## Prerequisites
- Google Search Console MCP configured in `opencode.jsonc`
- Authenticated Google account with access to the target site
- Python 3.8+ installed

## Workflow

### Step 1: Site Configuration
```bash
# Get site URL from user
# Determine GSC URL format:
#   - Regular site: https://example.com
#   - Subdomain: sc-domain:example.com
```

### Step 2: Data Collection
Use the Search Console MCP tools to collect data:
- `search-console_analytics_query` - Get keyword data with dimensions ['query']
- `search-console_analytics_top_pages` - Get top performing pages
- `search-console_analytics_performance_summary` - Get aggregate metrics

### Step 3: Run Analysis
```bash
cd <SEO_Audit_root>
python src/audit_engine.py --site <site_url> --output ./output/<site_name>
```

### Step 4: Review & Deliver
- Review generated `audit-report.html`
- Check scoring breakdown
- Verify action plan tasks

## Output Structure
```
output/
├── audit-report.html      # Main HTML report
├── analysis-data.json     # Raw analysis data
├── scoring-data.json      # Scoring breakdown
└── raw-data.json          # Raw GSC data
```

## Scoring Dimensions (100% total)
| Dimension | Weight | Source |
|-----------|--------|--------|
| Posicionamiento | 25% | GSC queries |
| Palabras Clave | 20% | GSC filtered keywords |
| Contenido | 15% | GA4 + GSC pages |
| SEO Técnico | 15% | PageSpeed API |
| Experiencia Usuario | 10% | Core Web Vitals |
| Enlaces | 10% | GSC + external |
| Competencia | 5% | Market analysis |

## Score Categories
- **90-100**: Excelente (green)
- **70-89**: Bueno (blue)
- **50-69**: Necesita Mejoras (yellow)
- **0-49**: Crítico (red)
