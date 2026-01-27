from typing import Dict, Any, List
from datetime import datetime
import uuid
from core.research_state import ResearchState

class ResearchDashboard:
    """Monitor and visualize research progress"""

    def __init__(self):
        self.metrics_history = []

    def track_metrics(self, state: ResearchState):
        """Track research metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "phase": state.get("research_phase", "unknown"),
            "sources_count": len(state.get("sources", [])),
            "findings_count": len(state.get("findings", [])),
            "citations_count": len(state.get("citations", [])),
            "validation_passed": not state.get("validation_errors", []),
            "confidence": state.get("analysis", {}).get("confidence_score", 0.0)
        }
        self.metrics_history.append(metrics)
        return metrics

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard report"""
        if not self.metrics_history:
            return {"error": "No metrics collected"}

        latest = self.metrics_history[-1]

        return {
            "summary": {
                "total_research_time": self._calculate_total_time(),
                "final_phase": latest["phase"],
                "total_sources": latest["sources_count"],
                "total_findings": latest["findings_count"],
                "overall_confidence": latest["confidence"]
            },
            "timeline": self.metrics_history,
            "performance": self._calculate_performance(),
            "recommendations": self._generate_dashboard_recommendations()
        }

    def _calculate_total_time(self) -> str:
        """Calculate total research time"""
        if len(self.metrics_history) < 2:
            return "Unknown"

        start = datetime.fromisoformat(self.metrics_history[0]["timestamp"])
        end = datetime.fromisoformat(self.metrics_history[-1]["timestamp"])
        duration = end - start
        return str(duration)

    def _calculate_performance(self) -> Dict[str, float]:
        """Calculate research performance metrics"""
        if len(self.metrics_history) < 2:
            return {}

        # Calculate rate metrics
        time_per_source = len(self.metrics_history) / max(self.metrics_history[-1]["sources_count"], 1)
        findings_per_hour = self.metrics_history[-1]["findings_count"] / (len(self.metrics_history) / 60)

        return {
            "time_per_source_minutes": time_per_source * 60,
            "findings_per_hour": findings_per_hour,
            "efficiency_score": min(1.0, findings_per_hour / 10),  # Normalize
            "consistency_score": self._calculate_consistency()
        }

    def _calculate_consistency(self) -> float:
        """Calculate consistency of progress"""
        if len(self.metrics_history) < 3:
            return 0.5

        # Check for steady progress in findings
        finding_counts = [m["findings_count"] for m in self.metrics_history]
        diffs = [finding_counts[i+1] - finding_counts[i] for i in range(len(finding_counts)-1)]

        # Calculate coefficient of variation (lower is more consistent)
        if len(diffs) > 1 and sum(diffs) > 0:
            mean = sum(diffs) / len(diffs)
            variance = sum((x - mean) ** 2 for x in diffs) / len(diffs)
            std = variance ** 0.5
            cv = std / mean if mean != 0 else 0
            return 1.0 / (1.0 + cv)  # Convert to 0-1 scale (1 = perfectly consistent)

        return 0.5

    def _generate_dashboard_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        latest = self.metrics_history[-1] if self.metrics_history else {}

        if latest.get("sources_count", 0) < 5:
            recommendations.append("Increase source diversity for more comprehensive analysis")

        if latest.get("confidence", 0) < 0.6:
            recommendations.append("Consider additional validation or expert review")

        if latest.get("findings_count", 0) < 3:
            recommendations.append("Expand analysis to generate more actionable findings")

        return recommendations if recommendations else ["Research proceeding optimally"]