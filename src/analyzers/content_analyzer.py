"""Content Analyzer Module.

Analyzes content performance and page metrics.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """Result of content analysis."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class ContentAnalyzer:
    """Analyzes content performance and page-level metrics.

    Evaluates page depth, engagement signals, content freshness,
    thin content risk, and overall content quality signals.
    """

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run content analysis and return a scored result.

        Args:
            data: Dictionary containing page data with keys such as
                'pages', 'sessions', 'pageviews', 'bounce_rate',
                'avg_time_on_page', 'word_count', 'last_modified',
                'title_length', 'meta_length', and 'headings'.

        Returns:
            AnalysisResult with score (0-100), findings list, and summary.
        """
        result = AnalysisResult()
        pages = data.get("pages", [])
        sessions = data.get("sessions", [])
        pageviews = data.get("pageviews", [])
        bounce_rate = data.get("bounce_rate", [])
        avg_time = data.get("avg_time_on_page", [])
        word_count = data.get("word_count", [])
        last_modified = data.get("last_modified", [])
        title_length = data.get("title_length", [])
        meta_length = data.get("meta_length", [])
        headings = data.get("headings", [])

        summary = self._build_summary(
            pages, sessions, pageviews, bounce_rate, avg_time,
            word_count, last_modified, title_length, meta_length, headings,
        )
        result.summary = summary

        findings = self._generate_findings(summary, data)
        result.findings = findings

        result.score = self._calculate_score(summary, findings)
        return result

    def _build_summary(
        self,
        pages: list[dict],
        sessions: list[int],
        pageviews: list[int],
        bounce_rate: list[float],
        avg_time: list[float],
        word_count: list[int],
        last_modified: list[str],
        title_length: list[int],
        meta_length: list[int],
        headings: list[dict],
    ) -> dict[str, Any]:
        """Build a summary dict from raw page data."""
        total_pages = len(pages)
        total_sessions = sum(sessions) if sessions else 0
        total_pageviews = sum(pageviews) if pageviews else 0
        avg_bounce = (sum(bounce_rate) / len(bounce_rate)) if bounce_rate else 0.0
        avg_time_on_page = (sum(avg_time) / len(avg_time)) if avg_time else 0.0

        thin_pages = sum(1 for w in word_count if w < 300) if word_count else 0
        adequate_pages = sum(1 for w in word_count if 300 <= w <= 1500) if word_count else 0
        deep_pages = sum(1 for w in word_count if w > 1500) if word_count else 0

        avg_title_len = (sum(title_length) / len(title_length)) if title_length else 0
        short_titles = sum(1 for t in title_length if t < 30) if title_length else 0
        long_titles = sum(1 for t in title_length if t > 60) if title_length else 0

        avg_meta_len = (sum(meta_length) / len(meta_length)) if meta_length else 0
        missing_meta = sum(1 for m in meta_length if m == 0) if meta_length else 0
        short_meta = sum(1 for m in meta_length if 0 < m < 120) if meta_length else 0

        # Bounce rate distribution
        high_bounce = sum(1 for b in bounce_rate if b > 0.7) if bounce_rate else 0
        mid_bounce = sum(1 for b in bounce_rate if 0.4 <= b <= 0.7) if bounce_rate else 0

        # Time on page distribution
        low_engagement = sum(1 for t in avg_time if t < 30) if avg_time else 0

        # Freshness
        stale_pages = sum(1 for d in last_modified if d and d < "2024-01-01") if last_modified else 0

        return {
            "total_pages": total_pages,
            "total_sessions": total_sessions,
            "total_pageviews": total_pageviews,
            "avg_bounce_rate": round(avg_bounce, 4),
            "avg_time_on_page": round(avg_time_on_page, 2),
            "thin_content_pages": thin_pages,
            "adequate_content_pages": adequate_pages,
            "deep_content_pages": deep_pages,
            "avg_title_length": round(avg_title_len, 1),
            "short_titles": short_titles,
            "long_titles": long_titles,
            "avg_meta_length": round(avg_meta_len, 1),
            "missing_meta_descriptions": missing_meta,
            "short_meta_descriptions": short_meta,
            "high_bounce_pages": high_bounce,
            "mid_bounce_pages": mid_bounce,
            "low_engagement_pages": low_engagement,
            "stale_content_pages": stale_pages,
        }

    def _generate_findings(
        self, summary: dict[str, Any], raw: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Generate actionable findings from content summary."""
        findings: list[dict[str, str]] = []
        total = summary.get("total_pages", 0) or 1

        thin_ratio = summary.get("thin_content_pages", 0) / total
        if thin_ratio > 0.3:
            findings.append({
                "severity": "high",
                "title": "Excessive thin content pages",
                "description": (
                    f"{summary.get('thin_content_pages', 0)} pages ({thin_ratio:.0%}) have fewer than 300 words."
                ),
                "recommendation": (
                    "Consolidate or expand thin pages. Consider noindexing low-value thin pages."
                ),
            })

        avg_bounce = summary.get("avg_bounce_rate", 0)
        if avg_bounce > 0.6:
            findings.append({
                "severity": "medium",
                "title": "High average bounce rate",
                "description": f"Average bounce rate is {avg_bounce:.1%}.",
                "recommendation": (
                    "Improve content relevance, add clear CTAs, and enhance internal linking."
                ),
            })

        missing_meta = summary.get("missing_meta_descriptions", 0)
        if missing_meta > 0:
            findings.append({
                "severity": "high",
                "title": "Missing meta descriptions",
                "description": f"{missing_meta} pages have no meta description.",
                "recommendation": (
                    "Write unique meta descriptions for all pages to improve CTR in search results."
                ),
            })

        short_meta = summary.get("short_meta_descriptions", 0)
        if short_meta > total * 0.2:
            findings.append({
                "severity": "medium",
                "title": "Too many short meta descriptions",
                "description": f"{short_meta} pages have meta descriptions under 120 characters.",
                "recommendation": (
                    "Expand meta descriptions to 150-160 characters for better SERP snippets."
                ),
            })

        short_titles = summary.get("short_titles", 0)
        if short_titles > total * 0.2:
            findings.append({
                "severity": "medium",
                "title": "Too many short title tags",
                "description": f"{short_titles} pages have titles under 30 characters.",
                "recommendation": (
                    "Optimize title tags to 50-60 characters with primary keywords."
                ),
            })

        stale = summary.get("stale_content_pages", 0)
        if stale > 0:
            findings.append({
                "severity": "medium",
                "title": "Stale content detected",
                "description": f"{stale} pages have not been updated since before 2024.",
                "recommendation": (
                    "Audit and refresh stale content to maintain rankings and relevance."
                ),
            })

        low_eng = summary.get("low_engagement_pages", 0)
        if low_eng > total * 0.3:
            findings.append({
                "severity": "medium",
                "title": "Low engagement on many pages",
                "description": f"{low_eng} pages average less than 30 seconds on page.",
                "recommendation": (
                    "Improve content quality, readability, and add engaging elements."
                ),
            })

        return findings

    def _calculate_score(
        self, summary: dict[str, Any], findings: list[dict[str, str]]
    ) -> int:
        """Calculate an overall content score from 0 to 100.

        Scoring weights:
            - Content depth (25%)
            - Engagement signals (25%)
            - SEO meta quality (25%)
            - Content freshness (15%)
            - Penalty from findings (10%)
        """
        total = summary.get("total_pages", 0) or 1

        # Content depth (25 points)
        thin_ratio = summary.get("thin_content_pages", 0) / total
        deep_ratio = summary.get("deep_content_pages", 0) / total
        depth_score = max(0, 25 - (thin_ratio * 30) + (deep_ratio * 10))
        depth_score = min(25, depth_score)

        # Engagement (25 points)
        avg_bounce = summary.get("avg_bounce_rate", 0)
        avg_time = summary.get("avg_time_on_page", 0)
        bounce_component = max(0, 12.5 - (avg_bounce * 12.5))
        time_component = min(12.5, (avg_time / 120) * 12.5)
        engagement_score = bounce_component + time_component

        # SEO meta quality (25 points)
        missing_meta = summary.get("missing_meta_descriptions", 0) / total
        missing_title_penalty = summary.get("short_titles", 0) / total
        meta_score = 25 - (missing_meta * 20) - (missing_title_penalty * 5)
        meta_score = max(0, min(25, meta_score))

        # Freshness (15 points)
        stale_ratio = summary.get("stale_content_pages", 0) / total
        freshness_score = max(0, 15 - (stale_ratio * 15))

        # Findings penalty (10 points)
        severity_penalties = {"high": 4, "medium": 2, "low": 0}
        penalty = sum(
            severity_penalties.get(f.get("severity", "low"), 0)
            for f in findings
        )

        raw_score = depth_score + engagement_score + meta_score + freshness_score
        adjusted = max(0, min(100, round(raw_score - penalty)))
        return adjusted
