"""UX Analyzer Module.

Analyzes user experience metrics.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """Result of UX analysis."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class UXAnalyzer:
    """Analyzes user experience metrics.

    Evaluates session quality, navigation patterns, mobile experience,
    accessibility signals, engagement depth, and conversion funnel health.
    """

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run UX analysis and return a scored result.

        Args:
            data: Dictionary containing UX data with keys such as
                'sessions', 'bounce_rate', 'pages_per_session',
                'avg_session_duration', 'exit_rate', 'device_mix',
                'navigation_flow', 'mobile_usage', 'desktop_usage',
                'conversion_rate', 'form_abandonment', 'scroll_depth',
                'accessibility_issues', and 'error_rates'.

        Returns:
            AnalysisResult with score (0-100), findings list, and summary.
        """
        result = AnalysisResult()
        sessions = data.get("sessions", [])
        bounce_rate = data.get("bounce_rate", 0)
        pages_per_session = data.get("pages_per_session", 0)
        avg_session_duration = data.get("avg_session_duration", 0)
        exit_rate = data.get("exit_rate", 0)
        device_mix = data.get("device_mix", {})
        navigation_flow = data.get("navigation_flow", {})
        mobile_usage = data.get("mobile_usage", {})
        desktop_usage = data.get("desktop_usage", {})
        conversion_rate = data.get("conversion_rate", 0)
        form_abandonment = data.get("form_abandonment", 0)
        scroll_depth = data.get("scroll_depth", [])
        accessibility_issues = data.get("accessibility_issues", [])
        error_rates = data.get("error_rates", {})

        summary = self._build_summary(
            sessions, bounce_rate, pages_per_session, avg_session_duration,
            exit_rate, device_mix, navigation_flow, mobile_usage, desktop_usage,
            conversion_rate, form_abandonment, scroll_depth,
            accessibility_issues, error_rates,
        )
        result.summary = summary

        findings = self._generate_findings(summary, data)
        result.findings = findings

        result.score = self._calculate_score(summary, findings)
        return result

    def _build_summary(
        self,
        sessions: list,
        bounce_rate: float,
        pages_per_session: float,
        avg_session_duration: float,
        exit_rate: float,
        device_mix: dict,
        navigation_flow: dict,
        mobile_usage: dict,
        desktop_usage: dict,
        conversion_rate: float,
        form_abandonment: float,
        scroll_depth: list[float],
        accessibility_issues: list[dict],
        error_rates: dict,
    ) -> dict[str, Any]:
        """Build a summary dict from raw UX data."""
        total_sessions = sum(sessions) if sessions else 0
        avg_scroll = (sum(scroll_depth) / len(scroll_depth)) if scroll_depth else 0
        low_scroll = sum(1 for s in scroll_depth if s < 50) if scroll_depth else 0

        mobile_bounce = mobile_usage.get("bounce_rate", 0)
        mobile_pages = mobile_usage.get("pages_per_session", 0)
        mobile_duration = mobile_usage.get("avg_session_duration", 0)

        desktop_bounce = desktop_usage.get("bounce_rate", 0)
        desktop_pages = desktop_usage.get("pages_per_session", 0)
        desktop_duration = desktop_usage.get("avg_session_duration", 0)

        mobile_pct = device_mix.get("mobile", 0)
        desktop_pct = device_mix.get("desktop", 0)

        dead_end_pages = navigation_flow.get("dead_ends", [])
        dead_end_count = len(dead_end_pages) if dead_end_pages else 0

        a11y_critical = sum(
            1 for i in accessibility_issues if i.get("severity") == "critical"
        ) if accessibility_issues else 0
        a11y_major = sum(
            1 for i in accessibility_issues if i.get("severity") == "major"
        ) if accessibility_issues else 0
        a11y_minor = sum(
            1 for i in accessibility_issues if i.get("severity") == "minor"
        ) if accessibility_issues else 0

        error_404 = error_rates.get("404", 0)
        error_500 = error_rates.get("500", 0)

        return {
            "total_sessions": total_sessions,
            "bounce_rate": round(bounce_rate, 4),
            "pages_per_session": round(pages_per_session, 2),
            "avg_session_duration": round(avg_session_duration, 2),
            "exit_rate": round(exit_rate, 4),
            "mobile_bounce_rate": round(mobile_bounce, 4),
            "mobile_pages_per_session": round(mobile_pages, 2),
            "mobile_avg_duration": round(mobile_duration, 2),
            "desktop_bounce_rate": round(desktop_bounce, 4),
            "desktop_pages_per_session": round(desktop_pages, 2),
            "desktop_avg_duration": round(desktop_duration, 2),
            "mobile_traffic_pct": round(mobile_pct, 4),
            "desktop_traffic_pct": round(desktop_pct, 4),
            "dead_end_pages": dead_end_count,
            "avg_scroll_depth": round(avg_scroll, 1),
            "low_scroll_pages": low_scroll,
            "conversion_rate": round(conversion_rate, 4),
            "form_abandonment_rate": round(form_abandonment, 4),
            "accessibility_critical": a11y_critical,
            "accessibility_major": a11y_major,
            "accessibility_minor": a11y_minor,
            "error_404_rate": round(error_404, 4),
            "error_500_rate": round(error_500, 4),
        }

    def _generate_findings(
        self, summary: dict[str, Any], raw: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Generate actionable findings from UX summary."""
        findings: list[dict[str, str]] = []

        bounce_rate = summary.get("bounce_rate", 0)
        if bounce_rate > 0.6:
            findings.append({
                "severity": "high",
                "title": "High overall bounce rate",
                "description": f"Bounce rate is {bounce_rate:.1%}.",
                "recommendation": (
                    "Improve landing page relevance, load speed, and clear navigation paths."
                ),
            })

        pages_per = summary.get("pages_per_session", 0)
        if pages_per < 2:
            findings.append({
                "severity": "medium",
                "title": "Low pages per session",
                "description": f"Users view only {pages_per:.1f} pages per session on average.",
                "recommendation": (
                    "Add related content modules and improve internal linking."
                ),
            })

        session_duration = summary.get("avg_session_duration", 0)
        if session_duration < 60:
            findings.append({
                "severity": "medium",
                "title": "Very short session duration",
                "description": f"Average session duration is {session_duration:.0f} seconds.",
                "recommendation": (
                    "Enhance content engagement with videos, interactive elements, and better layout."
                ),
            })

        mobile_bounce = summary.get("mobile_bounce_rate", 0)
        if mobile_bounce > 0.7:
            findings.append({
                "severity": "high",
                "title": "High mobile bounce rate",
                "description": f"Mobile bounce rate is {mobile_bounce:.1%}.",
                "recommendation": (
                    "Improve mobile responsiveness, touch targets, and mobile page speed."
                ),
            })

        dead_ends = summary.get("dead_end_pages", 0)
        if dead_ends > 5:
            findings.append({
                "severity": "medium",
                "title": "Many dead-end pages detected",
                "description": f"{dead_ends} pages have no outbound navigation links.",
                "recommendation": (
                    "Add CTAs, related content, or navigation elements to dead-end pages."
                ),
            })

        a11y_critical = summary.get("accessibility_critical", 0)
        if a11y_critical > 0:
            findings.append({
                "severity": "high",
                "title": "Critical accessibility issues",
                "description": f"{a11y_critical} critical accessibility issues found.",
                "recommendation": (
                    "Fix critical issues: missing alt text, form labels, keyboard navigation."
                ),
            })

        a11y_major = summary.get("accessibility_major", 0)
        if a11y_major > 0:
            findings.append({
                "severity": "medium",
                "title": "Major accessibility issues",
                "description": f"{a11y_major} major accessibility issues found.",
                "recommendation": (
                    "Address color contrast, ARIA roles, and focus management."
                ),
            })

        conversion = summary.get("conversion_rate", 0)
        if 0 < conversion < 0.02:
            findings.append({
                "severity": "medium",
                "title": "Low conversion rate",
                "description": f"Conversion rate is {conversion:.2%}.",
                "recommendation": (
                    "Run A/B tests on CTAs, simplify forms, and improve value proposition."
                ),
            })

        form_abandon = summary.get("form_abandonment_rate", 0)
        if form_abandon > 0.5:
            findings.append({
                "severity": "medium",
                "title": "High form abandonment rate",
                "description": f"Form abandonment rate is {form_abandon:.1%}.",
                "recommendation": (
                    "Reduce form fields, add progress indicators, and simplify validation."
                ),
            })

        error_404 = summary.get("error_404_rate", 0)
        if error_404 > 0.02:
            findings.append({
                "severity": "medium",
                "title": "High 404 error rate",
                "description": f"404 error rate is {error_404:.2%}.",
                "recommendation": (
                    "Audit broken links, set up proper redirects, and create a custom 404 page."
                ),
            })

        error_500 = summary.get("error_500_rate", 0)
        if error_500 > 0:
            findings.append({
                "severity": "high",
                "title": "Server errors detected",
                "description": f"500 error rate is {error_500:.2%}.",
                "recommendation": (
                    "Investigate server logs, fix application errors, and monitor uptime."
                ),
            })

        return findings

    def _calculate_score(
        self, summary: dict[str, Any], findings: list[dict[str, str]]
    ) -> int:
        """Calculate an overall UX score from 0 to 100.

        Scoring weights:
            - Engagement depth (30%)
            - Mobile experience (25%)
            - Navigation quality (20%)
            - Accessibility (15%)
            - Error health (10%)
        """
        # Engagement depth (30 points)
        bounce_rate = summary.get("bounce_rate", 1)
        pages_per = summary.get("pages_per_session", 0)
        duration = summary.get("avg_session_duration", 0)
        bounce_component = max(0, 15 - (bounce_rate * 15))
        pages_component = min(10, pages_per * 3)
        duration_component = min(5, (duration / 300) * 5)
        engagement_score = bounce_component + pages_component + duration_component

        # Mobile experience (25 points)
        mobile_bounce = summary.get("mobile_bounce_rate", 1)
        mobile_pages = summary.get("mobile_pages_per_session", 0)
        mobile_score = max(0, 25 - (mobile_bounce * 15)) + min(10, mobile_pages * 3)
        mobile_score = min(25, mobile_score)

        # Navigation quality (20 points)
        dead_ends = summary.get("dead_end_pages", 0)
        nav_score = max(0, 20 - (dead_ends * 2))

        # Accessibility (15 points)
        critical = summary.get("accessibility_critical", 0)
        major = summary.get("accessibility_major", 0)
        minor = summary.get("accessibility_minor", 0)
        a11y_score = 15 - (critical * 5) - (major * 2) - (minor * 0.5)
        a11y_score = max(0, min(15, a11y_score))

        # Error health (10 points)
        err_404 = summary.get("error_404_rate", 0)
        err_500 = summary.get("error_500_rate", 0)
        error_score = 10 - (err_404 * 50) - (err_500 * 100)
        error_score = max(0, min(10, error_score))

        # Findings penalty
        severity_penalties = {"high": 5, "medium": 2, "low": 0}
        penalty = sum(
            severity_penalties.get(f.get("severity", "low"), 0)
            for f in findings
        )

        raw_score = engagement_score + mobile_score + nav_score + a11y_score + error_score
        adjusted = max(0, min(100, round(raw_score - penalty)))
        return adjusted
