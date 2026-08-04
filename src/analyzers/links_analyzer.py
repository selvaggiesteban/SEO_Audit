"""Links Analyzer Module.

Analyzes internal and external link profiles.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisResult:
    """Result of link analysis."""

    score: int = 0
    findings: list[dict[str, str]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class LinksAnalyzer:
    """Analyzes internal and external link profiles.

    Evaluates internal linking depth, broken links, external link quality,
    anchor text distribution, link equity flow, and orphans.
    """

    def analyze(self, data: dict[str, Any]) -> AnalysisResult:
        """Run link analysis and return a scored result.

        Args:
            data: Dictionary containing link data with keys such as
                'internal_links', 'external_links', 'backlinks',
                'broken_links', 'orphan_pages', 'anchor_text',
                'link_depth', 'referring_domains', and 'outbound_links'.

        Returns:
            AnalysisResult with score (0-100), findings list, and summary.
        """
        result = AnalysisResult()
        internal_links = data.get("internal_links", [])
        external_links = data.get("external_links", [])
        backlinks = data.get("backlinks", [])
        broken_links = data.get("broken_links", [])
        orphan_pages = data.get("orphan_pages", [])
        anchor_text = data.get("anchor_text", [])
        link_depth = data.get("link_depth", [])
        referring_domains = data.get("referring_domains", [])
        outbound_links = data.get("outbound_links", [])

        summary = self._build_summary(
            internal_links, external_links, backlinks, broken_links,
            orphan_pages, anchor_text, link_depth, referring_domains,
            outbound_links,
        )
        result.summary = summary

        findings = self._generate_findings(summary, data)
        result.findings = findings

        result.score = self._calculate_score(summary, findings)
        return result

    def _build_summary(
        self,
        internal_links: list[dict],
        external_links: list[dict],
        backlinks: list[dict],
        broken_links: list[dict],
        orphan_pages: list[str],
        anchor_text: list[str],
        link_depth: list[int],
        referring_domains: list[str],
        outbound_links: list[dict],
    ) -> dict[str, Any]:
        """Build a summary dict from raw link data."""
        total_internal = len(internal_links) if internal_links else 0
        total_external = len(external_links) if external_links else 0
        total_backlinks = len(backlinks) if backlinks else 0
        total_broken = len(broken_links) if broken_links else 0
        total_orphans = len(orphan_pages) if orphan_pages else 0
        total_anchor = len(anchor_text) if anchor_text else 0
        total_ref_domains = len(referring_domains) if referring_domains else 0

        avg_depth = (sum(link_depth) / len(link_depth)) if link_depth else 0
        deep_pages = sum(1 for d in link_depth if d > 4) if link_depth else 0
        shallow_pages = sum(1 for d in link_depth if d <= 2) if link_depth else 0

        # Anchor text analysis
        exact_match = sum(
            1 for a in anchor_text if a and a.lower() == a.lower()
        ) if anchor_text else 0
        generic_anchors = sum(
            1 for a in anchor_text
            if a.lower() in ("click here", "read more", "here", "more", "link")
        ) if anchor_text else 0

        # Broken link categories
        broken_404 = sum(1 for b in broken_links if b.get("status") == 404) if broken_links else 0
        broken_500 = sum(1 for b in broken_links if b.get("status") == 500) if broken_links else 0
        broken_other = total_broken - broken_404 - broken_500

        # External link quality
        dofollow = sum(1 for e in external_links if e.get("follow") == "dofollow") if external_links else 0
        nofollow = sum(1 for e in external_links if e.get("follow") == "nofollow") if external_links else 0

        return {
            "total_internal_links": total_internal,
            "total_external_links": total_external,
            "total_backlinks": total_backlinks,
            "total_broken_links": total_broken,
            "total_orphan_pages": total_orphans,
            "total_anchor_text_entries": total_anchor,
            "total_referring_domains": total_ref_domains,
            "avg_link_depth": round(avg_depth, 2),
            "deep_pages_count": deep_pages,
            "shallow_pages_count": shallow_pages,
            "generic_anchor_count": generic_anchors,
            "broken_404_count": broken_404,
            "broken_500_count": broken_500,
            "broken_other_count": broken_other,
            "dofollow_external": dofollow,
            "nofollow_external": nofollow,
        }

    def _generate_findings(
        self, summary: dict[str, Any], raw: dict[str, str]
    ) -> list[dict[str, str]]:
        """Generate actionable findings from link summary."""
        findings: list[dict[str, str]] = []

        total_broken = summary.get("total_broken_links", 0)
        if total_broken > 0:
            findings.append({
                "severity": "high",
                "title": "Broken links detected",
                "description": (
                    f"{total_broken} broken links found "
                    f"({summary.get('broken_404_count', 0)} are 404s)."
                ),
                "recommendation": (
                    "Fix or remove broken links, set up redirects for changed URLs."
                ),
            })

        total_orphans = summary.get("total_orphan_pages", 0)
        if total_orphans > 0:
            findings.append({
                "severity": "medium",
                "title": "Orphan pages detected",
                "description": (
                    f"{total_orphans} pages have no internal links pointing to them."
                ),
                "recommendation": (
                    "Add internal links to orphan pages from relevant content pages."
                ),
            })

        avg_depth = summary.get("avg_link_depth", 0)
        if avg_depth > 4:
            findings.append({
                "severity": "medium",
                "title": "Excessive average link depth",
                "description": f"Average link depth is {avg_depth:.1f} clicks from homepage.",
                "recommendation": (
                    "Flatten site architecture so important pages are within 3 clicks."
                ),
            })

        deep_pages = summary.get("deep_pages_count", 0)
        total_internal = summary.get("total_internal_links", 0) or 1
        if deep_pages > total_internal * 0.3:
            findings.append({
                "severity": "medium",
                "title": "Many deeply buried pages",
                "description": f"{deep_pages} pages are more than 4 clicks deep.",
                "recommendation": (
                    "Create hub pages and improve breadcrumb navigation."
                ),
            })

        generic = summary.get("generic_anchor_count", 0)
        if generic > 0:
            findings.append({
                "severity": "low",
                "title": "Generic anchor text used",
                "description": f"{generic} links use generic anchor text (e.g. 'click here').",
                "recommendation": (
                    "Replace generic anchors with descriptive, keyword-relevant text."
                ),
            })

        total_internal = summary.get("total_internal_links", 0)
        total_external = summary.get("total_external_links", 0)
        if total_internal > 0 and total_external / total_internal > 2:
            findings.append({
                "severity": "low",
                "title": "High external-to-internal link ratio",
                "description": (
                    f"Ratio is {total_external / total_internal:.1f}x "
                    f"({total_external} external vs {total_internal} internal)."
                ),
                "recommendation": (
                    "Increase internal linking to distribute equity within the site."
                ),
            })

        ref_domains = summary.get("total_referring_domains", 0)
        backlinks = summary.get("total_backlinks", 0)
        if backlinks > 0 and ref_domains > 0:
            ratio = backlinks / ref_domains
            if ratio > 20:
                findings.append({
                    "severity": "low",
                    "title": "High backlink concentration",
                    "description": (
                        f"Average {ratio:.0f} backlinks per referring domain. "
                        "May indicate link spam."
                    ),
                    "recommendation": (
                        "Diversify backlink profile by earning links from more unique domains."
                    ),
                })

        return findings

    def _calculate_score(
        self, summary: dict[str, Any], findings: list[dict[str, str]]
    ) -> int:
        """Calculate an overall link score from 0 to 100.

        Scoring weights:
            - Internal linking (30%)
            - External quality (20%)
            - Broken link health (25%)
            - Link depth & orphans (15%)
            - Anchor text quality (10%)
        """
        # Internal linking (30 points)
        total_internal = summary.get("total_internal_links", 0)
        shallow = summary.get("shallow_pages_count", 0)
        internal_score = min(30, (total_internal / 50) * 10 + (shallow * 2))

        # External quality (20 points)
        ref_domains = summary.get("total_referring_domains", 0)
        dofollow = summary.get("dofollow_external", 0)
        external_score = min(20, (ref_domains / 10) * 5 + (dofollow / 20) * 5)

        # Broken link health (25 points)
        broken_404 = summary.get("broken_404_count", 0)
        broken_500 = summary.get("broken_500_count", 0)
        broken_score = 25 - (broken_404 * 3) - (broken_500 * 5)
        broken_score = max(0, min(25, broken_score))

        # Link depth & orphans (15 points)
        avg_depth = summary.get("avg_link_depth", 0)
        orphans = summary.get("total_orphan_pages", 0)
        depth_score = 15 - (max(0, avg_depth - 3) * 2) - (orphans * 1)
        depth_score = max(0, min(15, depth_score))

        # Anchor text quality (10 points)
        generic = summary.get("generic_anchor_count", 0)
        total_anchor = summary.get("total_anchor_text_entries", 0) or 1
        anchor_score = 10 - (generic / total_anchor * 10)
        anchor_score = max(0, min(10, anchor_score))

        # Findings penalty
        severity_penalties = {"high": 5, "medium": 2, "low": 0}
        penalty = sum(
            severity_penalties.get(f.get("severity", "low"), 0)
            for f in findings
        )

        raw_score = internal_score + external_score + broken_score + depth_score + anchor_score
        adjusted = max(0, min(100, round(raw_score - penalty)))
        return adjusted
