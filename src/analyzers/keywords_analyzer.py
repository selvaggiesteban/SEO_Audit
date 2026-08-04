"""Keywords Analyzer Module.

Analyzes filtered keywords with opportunity scoring.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """Result of keyword analysis."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class KeywordsAnalyzer:
    """Analyzes filtered keywords with opportunity scoring.

    Evaluates keyword distribution, difficulty spread, search volume tiers,
    SERP feature opportunities, and ranking potential.
    """

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run keyword analysis and return a scored result.

        Args:
            data: Dictionary containing keyword data with keys such as
                'keywords', 'positions', 'impressions', 'clicks', 'ctr',
                'volume', 'difficulty', 'serp_features', and 'trends'.

        Returns:
            AnalysisResult with score (0-100), findings list, and summary.
        """
        result = AnalysisResult()
        keywords = data.get("keywords", [])
        positions = data.get("positions", [])
        impressions = data.get("impressions", [])
        clicks = data.get("clicks", [])
        ctr = data.get("ctr", [])
        volume = data.get("volume", [])
        difficulty = data.get("difficulty", [])
        serp_features = data.get("serp_features", [])
        trends = data.get("trends", [])

        summary = self._build_summary(
            keywords, positions, impressions, clicks, ctr,
            volume, difficulty, serp_features, trends
        )
        result.summary = summary

        findings = self._generate_findings(summary, data)
        result.findings = findings

        result.score = self._calculate_score(summary, findings)
        return result

    def _build_summary(
        self,
        keywords: list[dict],
        positions: list[float],
        impressions: list[int],
        clicks: list[int],
        ctr: list[float],
        volume: list[int],
        difficulty: list[float],
        serp_features: list[dict],
        trends: list[dict],
    ) -> dict[str, Any]:
        """Build a summary dict from raw keyword data."""
        total_keywords = len(keywords)
        total_impressions = sum(impressions) if impressions else 0
        total_clicks = sum(clicks) if clicks else 0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
        avg_position = (sum(positions) / len(positions)) if positions else 0.0

        top_3 = sum(1 for p in positions if 1 <= p <= 3) if positions else 0
        top_10 = sum(1 for p in positions if 1 <= p <= 10) if positions else 0
        page_2 = sum(1 for p in positions if 11 <= p <= 20) if positions else 0
        beyond_page_1 = sum(1 for p in positions if p > 10) if positions else 0

        low_volume = sum(1 for v in volume if v < 100) if volume else 0
        mid_volume = sum(1 for v in volume if 100 <= v <= 1000) if volume else 0
        high_volume = sum(1 for v in volume if v > 1000) if volume else 0

        low_diff = sum(1 for d in difficulty if d < 30) if difficulty else 0
        mid_diff = sum(1 for d in difficulty if 30 <= d <= 60) if difficulty else 0
        high_diff = sum(1 for d in difficulty if d > 60) if difficulty else 0

        feature_count = len(serp_features) if serp_features else 0
        rising_count = sum(1 for t in trends if t.get("direction") == "up") if trends else 0
        declining_count = sum(1 for t in trends if t.get("direction") == "down") if trends else 0

        return {
            "total_keywords": total_keywords,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "avg_ctr": round(avg_ctr, 2),
            "avg_position": round(avg_position, 2),
            "top_3_count": top_3,
            "top_10_count": top_10,
            "page_2_count": page_2,
            "beyond_page_1_count": beyond_page_1,
            "low_volume": low_volume,
            "mid_volume": mid_volume,
            "high_volume": high_volume,
            "low_difficulty": low_diff,
            "mid_difficulty": mid_diff,
            "high_difficulty": high_diff,
            "serp_feature_count": feature_count,
            "rising_trends": rising_count,
            "declining_trends": declining_count,
        }

    def _generate_findings(
        self, summary: dict[str, Any], raw: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Generate actionable findings from keyword summary."""
        findings: list[dict[str, str]] = []
        total = summary.get("total_keywords", 0) or 1

        top_3_ratio = summary.get("top_3_count", 0) / total
        if top_3_ratio < 0.1:
            findings.append({
                "severity": "high",
                "title": "Low top-3 keyword count",
                "description": (
                    f"Only {summary.get('top_3_count', 0)} keywords rank in the top 3 "
                    f"({top_3_ratio:.0%} of total)."
                ),
                "recommendation": (
                    "Focus on high-intent, low-difficulty keywords to improve top-3 coverage."
                ),
            })

        beyond_page_1_ratio = summary.get("beyond_page_1_count", 0) / total
        if beyond_page_1_ratio > 0.5:
            findings.append({
                "severity": "high",
                "title": "Majority of keywords rank beyond page 1",
                "description": (
                    f"{summary.get('beyond_page_1_count', 0)} keywords ({beyond_page_1_ratio:.0%}) "
                    f"rank beyond position 10."
                ),
                "recommendation": (
                    "Prioritize on-page optimization and internal linking for page 2 keywords."
                ),
            })

        avg_ctr = summary.get("avg_ctr", 0)
        if avg_ctr < 2.0:
            findings.append({
                "severity": "medium",
                "title": "Low average click-through rate",
                "description": f"Average CTR is {avg_ctr:.2f}%, below the 2% benchmark.",
                "recommendation": (
                    "Improve title tags and meta descriptions for higher impression keywords."
                ),
            })

        avg_pos = summary.get("avg_position", 0)
        if avg_pos > 20:
            findings.append({
                "severity": "medium",
                "title": "Poor average ranking position",
                "description": f"Average position is {avg_pos:.1f}.",
                "recommendation": (
                    "Target long-tail keywords with lower competition to improve positions."
                ),
            })

        high_diff_ratio = summary.get("high_difficulty", 0) / total
        if high_diff_ratio > 0.5:
            findings.append({
                "severity": "medium",
                "title": "High keyword difficulty distribution",
                "description": (
                    f"{summary.get('high_difficulty', 0)} keywords ({high_diff_ratio:.0%}) have difficulty > 60."
                ),
                "recommendation": (
                    "Balance portfolio with lower-difficulty keywords for faster wins."
                ),
            })

        rising = summary.get("rising_trends", 0)
        if rising > 0:
            findings.append({
                "severity": "low",
                "title": "Rising keyword trends detected",
                "description": f"{rising} keywords show upward trend.",
                "recommendation": "Create or update content to capture emerging search demand.",
            })

        declining = summary.get("declining_trends", 0)
        if declining > 0:
            findings.append({
                "severity": "medium",
                "title": "Declining keyword trends",
                "description": f"{declining} keywords show downward trend.",
                "recommendation": "Review content freshness and update outdated information.",
            })

        if summary.get("serp_feature_count", 0) == 0:
            findings.append({
                "severity": "medium",
                "title": "No SERP feature opportunities identified",
                "description": "No keywords trigger rich snippets or featured snippets.",
                "recommendation": "Implement structured data and optimize for featured snippets.",
            })

        return findings

    def _calculate_score(
        self, summary: dict[str, Any], findings: list[dict[str, str]]
    ) -> int:
        """Calculate an overall keyword score from 0 to 100.

        Scoring weights:
            - Ranking distribution (35%)
            - CTR performance (20%)
            - Volume opportunity (15%)
            - Difficulty balance (15%)
            - SERP features & trends (15%)
        """
        total = summary.get("total_keywords", 0) or 1

        # Ranking distribution component (35 points)
        top_3_pct = summary.get("top_3_count", 0) / total
        top_10_pct = summary.get("top_10_count", 0) / total
        ranking_score = min(35, (top_3_pct * 25) + (top_10_pct * 10))

        # CTR component (20 points)
        avg_ctr = summary.get("avg_ctr", 0)
        ctr_score = min(20, avg_ctr * 4)

        # Volume component (15 points)
        high_vol = summary.get("high_volume", 0)
        mid_vol = summary.get("mid_volume", 0)
        vol_score = min(15, (high_vol * 3) + (mid_vol * 1))

        # Difficulty balance component (15 points)
        low_diff = summary.get("low_difficulty", 0)
        diff_score = min(15, (low_diff / total) * 15)

        # SERP features & trends component (15 points)
        features = summary.get("serp_feature_count", 0)
        rising = summary.get("rising_trends", 0)
        feature_score = min(15, features * 3 + rising * 2)

        raw_score = ranking_score + ctr_score + vol_score + diff_score + feature_score

        # Severity penalty
        severity_penalties = {"high": 5, "medium": 2, "low": 0}
        penalty = sum(
            severity_penalties.get(f.get("severity", "low"), 0)
            for f in findings
        )
        adjusted = max(0, min(100, round(raw_score - penalty)))
        return adjusted
