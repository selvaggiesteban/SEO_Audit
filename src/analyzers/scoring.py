"""Scoring Module.

Calculates weighted scores across all dimensions (0-100).
"""

from dataclasses import dataclass, field
from typing import Any

from .keywords_analyzer import KeywordsAnalyzer, AnalysisResult as KeywordsResult
from .content_analyzer import ContentAnalyzer, AnalysisResult as ContentResult
from .technical_analyzer import TechnicalAnalyzer, AnalysisResult as TechnicalResult
from .ux_analyzer import UXAnalyzer, AnalysisResult as UXResult
from .links_analyzer import LinksAnalyzer, AnalysisResult as LinksResult


@dataclass
class WeightedScores:
    """Breakdown of individual dimension scores."""

    keywords: int = 0
    content: int = 0
    technical: int = 0
    ux: int = 0
    links: int = 0


@dataclass
class AnalysisResult:
    """Final aggregated analysis result."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    weighted_scores: WeightedScores = field(default_factory=WeightedScores)


# Default dimension weights (must sum to 1.0)
DEFAULT_WEIGHTS: dict[str, float] = {
    "keywords": 0.25,
    "content": 0.20,
    "technical": 0.25,
    "ux": 0.15,
    "links": 0.15,
}


class ScoringEngine:
    """Calculates weighted scores across all SEO dimensions.

    Orchestrates all analyzer modules, aggregates their results,
    and computes a final 0-100 score with severity-ranked findings.
    """

    def __init__(self, weights: dict[str, float] | None = None):
        """Initialize the scoring engine with optional custom weights.

        Args:
            weights: Optional dict mapping dimension names to weights.
                Weights are normalized to sum to 1.0. If None, defaults
                are used.
        """
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self._normalize_weights()

        self.keywords_analyzer = KeywordsAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ux_analyzer = UXAnalyzer()
        self.links_analyzer = LinksAnalyzer()

    def _normalize_weights(self) -> None:
        """Normalize weights so they sum to 1.0."""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run all analyzers and calculate the final weighted score.

        Args:
            data: Dictionary containing keys for each dimension:
                'keywords', 'content', 'technical', 'ux', 'links'.
                Each key maps to the data dict expected by that analyzer.

        Returns:
            AnalysisResult with final weighted score (0-100),
            aggregated findings, per-dimension breakdown, and summary.
        """
        results: dict[str, Any] = {}

        if "keywords" in data:
            results["keywords"] = self.keywords_analyzer.analyze(data["keywords"])
        if "content" in data:
            results["content"] = self.content_analyzer.analyze(data["content"])
        if "technical" in data:
            results["technical"] = self.technical_analyzer.analyze(data["technical"])
        if "ux" in data:
            results["ux"] = self.ux_analyzer.analyze(data["ux"])
        if "links" in data:
            results["links"] = self.links_analyzer.analyze(data["links"])

        weighted_scores = self._compute_weighted_scores(results)
        all_findings = self._aggregate_findings(results)
        all_findings = self._rank_findings(all_findings)

        summary = self._build_summary(results, weighted_scores)
        final_score = self._compute_final_score(weighted_scores)

        return AnalysisResult(
            score=final_score,
            findings=all_findings,
            summary=summary,
            weighted_scores=weighted_scores,
        )

    def _compute_weighted_scores(
        self, results: dict[str, Any]
    ) -> WeightedScores:
        """Extract raw scores from each analyzer result."""
        return WeightedScores(
            keywords=results.get("keywords", KeywordsResult()).score,
            content=results.get("content", ContentResult()).score,
            technical=results.get("technical", TechnicalResult()).score,
            ux=results.get("ux", UXResult()).score,
            links=results.get("links", LinksResult()).score,
        )

    def _compute_final_score(self, weighted: WeightedScores) -> int:
        """Compute the final weighted score."""
        raw = (
            weighted.keywords * self.weights.get("keywords", 0)
            + weighted.content * self.weights.get("content", 0)
            + weighted.technical * self.weights.get("technical", 0)
            + weighted.ux * self.weights.get("ux", 0)
            + weighted.links * self.weights.get("links", 0)
        )
        return max(0, min(100, round(raw)))

    def _aggregate_findings(
        self, results: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Collect and tag all findings with their source dimension."""
        aggregated: list[dict[str, str]] = []
        for dimension, result in results.items():
            for finding in result.findings:
                tagged = dict(finding)
                tagged["dimension"] = dimension
                aggregated.append(tagged)
        return aggregated

    def _rank_findings(
        self, findings: list[dict[str, str]]
    ) -> list[dict[str, str]]:
        """Sort findings by severity (high first) then by dimension priority."""
        severity_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            findings,
            key=lambda f: (
                severity_order.get(f.get("severity", "low"), 3),
                f.get("dimension", "zzz"),
            ),
        )

    def _build_summary(
        self, results: dict[str, Any], weighted: WeightedScores
    ) -> dict[str, Any]:
        """Build a consolidated summary from all dimensions."""
        summary: dict[str, Any] = {
            "dimension_scores": {
                "keywords": weighted.keywords,
                "content": weighted.content,
                "technical": weighted.technical,
                "ux": weighted.ux,
                "links": weighted.links,
            },
            "weights": self.weights,
            "dimension_summaries": {},
        }

        for dimension, result in results.items():
            summary["dimension_summaries"][dimension] = result.summary

        return summary

    def get_score_label(self, score: int) -> str:
        """Return a human-readable label for a score.

        Args:
            score: Score from 0 to 100.

        Returns:
            Label string: 'Critical', 'Poor', 'Needs Work',
            'Good', or 'Excellent'.
        """
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Work"
        elif score >= 30:
            return "Poor"
        else:
            return "Critical"

    def get_critical_findings(
        self, findings: list[dict[str, str]], limit: int = 5
    ) -> list[dict[str, str]]:
        """Return top critical findings limited to N results.

        Args:
            findings: List of findings dicts.
            limit: Maximum number of findings to return.

        Returns:
            List of high-severity findings.
        """
        return [f for f in findings if f.get("severity") == "high"][:limit]
