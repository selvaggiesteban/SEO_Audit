"""Technical Analyzer Module.

Analyzes PageSpeed and Core Web Vitals.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """Result of technical analysis."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class TechnicalAnalyzer:
    """Analyzes PageSpeed and Core Web Vitals performance.

    Evaluates LCP, FID/INP, CLS, FCP, TTFB, render-blocking resources,
    image optimization, script bloat, and overall technical health.
    """

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run technical analysis and return a scored result.

        Args:
            data: Dictionary containing technical data with keys such as
                'pagespeed', 'core_web_vitals', 'mobile_scores',
                'desktop_scores', 'lcp', 'fid', 'inp', 'cls',
                'fcp', 'ttfb', 'blocking_resources', 'image_issues',
                and 'script_stats'.

        Returns:
            AnalysisResult with score (0-100), findings list, and summary.
        """
        result = AnalysisResult()
        pagespeed = data.get("pagespeed", {})
        cwv = data.get("core_web_vitals", {})
        mobile_scores = data.get("mobile_scores", {})
        desktop_scores = data.get("desktop_scores", {})
        lcp = data.get("lcp", [])
        fid = data.get("fid", [])
        inp = data.get("inp", [])
        cls = data.get("cls", [])
        fcp = data.get("fcp", [])
        ttfb = data.get("ttfb", [])
        blocking = data.get("blocking_resources", [])
        image_issues = data.get("image_issues", [])
        script_stats = data.get("script_stats", {})

        summary = self._build_summary(
            pagespeed, cwv, mobile_scores, desktop_scores,
            lcp, fid, inp, cls, fcp, ttfb, blocking, image_issues, script_stats,
        )
        result.summary = summary

        findings = self._generate_findings(summary, data)
        result.findings = findings

        result.score = self._calculate_score(summary, findings)
        return result

    def _build_summary(
        self,
        pagespeed: dict,
        cwv: dict,
        mobile_scores: dict,
        desktop_scores: dict,
        lcp: list[float],
        fid: list[float],
        inp: list[float],
        cls: list[float],
        fcp: list[float],
        ttfb: list[float],
        blocking: list[dict],
        image_issues: list[dict],
        script_stats: dict,
    ) -> dict[str, Any]:
        """Build a summary dict from raw technical data."""
        avg_mobile = mobile_scores.get("performance", 0)
        avg_desktop = desktop_scores.get("performance", 0)

        avg_lcp = (sum(lcp) / len(lcp)) if lcp else 0.0
        avg_fid = (sum(fid) / len(fid)) if fid else 0.0
        avg_inp = (sum(inp) / len(inp)) if inp else 0.0
        avg_cls = (sum(cls) / len(cls)) if cls else 0.0
        avg_fcp = (sum(fcp) / len(fcp)) if fcp else 0.0
        avg_ttfb = (sum(ttfb) / len(ttfb)) if ttfb else 0.0

        poor_lcp = sum(1 for v in lcp if v > 2.5) if lcp else 0
        poor_fid = sum(1 for v in fid if v > 100) if fid else 0
        poor_inp = sum(1 for v in inp if v > 200) if inp else 0
        poor_cls = sum(1 for v in cls if v > 0.1) if cls else 0

        good_lcp = sum(1 for v in lcp if v <= 2.5) if lcp else 0
        good_fid = sum(1 for v in fid if v <= 100) if fid else 0
        good_inp = sum(1 for v in inp if v <= 200) if inp else 0
        good_cls = sum(1 for v in cls if v <= 0.1) if cls else 0

        blocking_count = len(blocking) if blocking else 0
        blocking_total_bytes = sum(
            r.get("size", 0) for r in blocking
        ) if blocking else 0

        image_count = len(image_issues) if image_issues else 0
        unoptimized_images = sum(
            1 for i in image_issues if i.get("unoptimized", False)
        ) if image_issues else 0

        total_scripts = script_stats.get("total_count", 0)
        total_script_size = script_stats.get("total_size_kb", 0)
        render_blocking_scripts = script_stats.get("render_blocking", 0)

        return {
            "avg_mobile_performance": round(avg_mobile, 1),
            "avg_desktop_performance": round(avg_desktop, 1),
            "avg_lcp": round(avg_lcp, 3),
            "avg_fid": round(avg_fid, 1),
            "avg_inp": round(avg_inp, 1),
            "avg_cls": round(avg_cls, 4),
            "avg_fcp": round(avg_fcp, 3),
            "avg_ttfb": round(avg_ttfb, 3),
            "poor_lcp_count": poor_lcp,
            "poor_fid_count": poor_fid,
            "poor_inp_count": poor_inp,
            "poor_cls_count": poor_cls,
            "good_lcp_count": good_lcp,
            "good_fid_count": good_fid,
            "good_inp_count": good_inp,
            "good_cls_count": good_cls,
            "blocking_resources": blocking_count,
            "blocking_total_bytes": blocking_total_bytes,
            "image_issues_total": image_count,
            "unoptimized_images": unoptimized_images,
            "total_scripts": total_scripts,
            "total_script_size_kb": total_script_size,
            "render_blocking_scripts": render_blocking_scripts,
        }

    def _generate_findings(
        self, summary: dict[str, Any], raw: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Generate actionable findings from technical summary."""
        findings: list[dict[str, str]] = []

        avg_mobile = summary.get("avg_mobile_performance", 0)
        if avg_mobile < 50:
            findings.append({
                "severity": "high",
                "title": "Poor mobile performance score",
                "description": f"Average mobile PageSpeed score is {avg_mobile}/100.",
                "recommendation": (
                    "Optimize images, defer non-critical JS, and minimize render-blocking resources."
                ),
            })
        elif avg_mobile < 80:
            findings.append({
                "severity": "medium",
                "title": "Below-average mobile performance",
                "description": f"Average mobile PageSpeed score is {avg_mobile}/100.",
                "recommendation": (
                    "Aim for 90+ by optimizing largest contentful paint and scripts."
                ),
            })

        avg_lcp = summary.get("avg_lcp", 0)
        if avg_lcp > 2.5:
            findings.append({
                "severity": "high",
                "title": "LCP exceeds 2.5s threshold",
                "description": f"Average LCP is {avg_lcp}s. Good LCP is under 2.5s.",
                "recommendation": (
                    "Preload hero images, use CDN, optimize server response time."
                ),
            })

        avg_cls = summary.get("avg_cls", 0)
        if avg_cls > 0.1:
            findings.append({
                "severity": "high",
                "title": "CLS exceeds 0.1 threshold",
                "description": f"Average CLS is {avg_cls}. Good CLS is under 0.1.",
                "recommendation": (
                    "Set explicit dimensions for images/videos, avoid dynamic content injection."
                ),
            })

        avg_fid = summary.get("avg_fid", 0)
        if avg_fid > 100:
            findings.append({
                "severity": "high",
                "title": "FID exceeds 100ms threshold",
                "description": f"Average FID is {avg_fid}ms. Good FID is under 100ms.",
                "recommendation": (
                    "Break up long tasks, use web workers, defer heavy scripts."
                ),
            })

        avg_inp = summary.get("avg_inp", 0)
        if avg_inp > 200:
            findings.append({
                "severity": "high",
                "title": "INP exceeds 200ms threshold",
                "description": f"Average INP is {avg_inp}ms. Good INP is under 200ms.",
                "recommendation": (
                    "Reduce main thread work, optimize event handlers."
                ),
            })

        blocking = summary.get("blocking_resources", 0)
        if blocking > 5:
            findings.append({
                "severity": "medium",
                "title": "Excessive render-blocking resources",
                "description": f"{blocking} render-blocking resources detected.",
                "recommendation": (
                    "Inline critical CSS, defer non-essential scripts, use async loading."
                ),
            })

        unopt_images = summary.get("unoptimized_images", 0)
        if unopt_images > 0:
            findings.append({
                "severity": "medium",
                "title": "Unoptimized images detected",
                "description": f"{unopt_images} images are unoptimized.",
                "recommendation": (
                    "Use modern formats (WebP/AVIF), compress, and lazy-load below-fold images."
                ),
            })

        script_size = summary.get("total_script_size_kb", 0)
        if script_size > 500:
            findings.append({
                "severity": "medium",
                "title": "Large JavaScript payload",
                "description": f"Total script size is {script_size:.0f}KB.",
                "recommendation": (
                    "Tree-shake unused code, code-split, and use dynamic imports."
                ),
            })

        return findings

    def _calculate_score(
        self, summary: dict[str, Any], findings: list[dict[str, str]]
    ) -> int:
        """Calculate an overall technical score from 0 to 100.

        Scoring weights:
            - PageSpeed scores (30%)
            - Core Web Vitals (40%)
            - Resource optimization (15%)
            - Image optimization (15%)
        """
        # PageSpeed scores (30 points)
        mobile = summary.get("avg_mobile_performance", 0)
        desktop = summary.get("avg_desktop_performance", 0)
        pagespeed_score = min(30, (mobile * 0.2) + (desktop * 0.1))

        # Core Web Vitals (40 points)
        total_lcp = summary.get("poor_lcp_count", 0) + summary.get("good_lcp_count", 0) or 1
        total_fid = summary.get("poor_fid_count", 0) + summary.get("good_fid_count", 0) or 1
        total_inp = summary.get("poor_inp_count", 0) + summary.get("good_inp_count", 0) or 1
        total_cls = summary.get("poor_cls_count", 0) + summary.get("good_cls_count", 0) or 1

        lcp_pct = summary.get("good_lcp_count", 0) / total_lcp
        fid_pct = summary.get("good_fid_count", 0) / total_fid
        inp_pct = summary.get("good_inp_count", 0) / total_inp
        cls_pct = summary.get("good_cls_count", 0) / total_cls
        cwv_score = ((lcp_pct + fid_pct + inp_pct + cls_pct) / 4) * 40

        # Resource optimization (15 points)
        blocking = summary.get("blocking_resources", 0)
        resource_score = max(0, 15 - (blocking * 1.5))

        # Image optimization (15 points)
        image_total = summary.get("image_issues_total", 0) or 1
        unopt = summary.get("unoptimized_images", 0)
        image_score = max(0, 15 - (unopt / image_total) * 15)

        # Findings penalty
        severity_penalties = {"high": 5, "medium": 2, "low": 0}
        penalty = sum(
            severity_penalties.get(f.get("severity", "low"), 0)
            for f in findings
        )

        raw_score = pagespeed_score + cwv_score + resource_score + image_score
        adjusted = max(0, min(100, round(raw_score - penalty)))
        return adjusted
