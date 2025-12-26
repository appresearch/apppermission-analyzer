"""
Data models for permission analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Permission:
    """Represents an application permission."""

    name: str
    category: str = "Other"
    risk_level: str = "low"  # low, medium, high
    description: Optional[str] = None


@dataclass
class AppMetadata:
    """Application metadata."""

    package_name: str
    app_name: str
    version: str
    category: str = "unknown"
    developer: Optional[str] = None
    min_sdk: Optional[str] = None
    target_sdk: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result of permission analysis."""

    app_id: str
    platform: str
    permissions: List[Permission]
    metadata: AppMetadata
    over_permissions: List[str] = field(default_factory=list)
    patterns: Dict[str, any] = field(default_factory=dict)

    def summary(self) -> str:
        """Generate a summary of the analysis."""
        return f"""
Analysis Summary for {self.app_id}
Platform: {self.platform}
Total Permissions: {len(self.permissions)}
High Risk Permissions: {sum(1 for p in self.permissions if p.risk_level == 'high')}
Over-Permissions Detected: {len(self.over_permissions)}
        """.strip()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "app_id": self.app_id,
            "platform": self.platform,
            "permissions": [
                {
                    "name": p.name,
                    "category": p.category,
                    "risk_level": p.risk_level,
                    "description": p.description,
                }
                for p in self.permissions
            ],
            "metadata": {
                "package_name": self.metadata.package_name,
                "app_name": self.metadata.app_name,
                "version": self.metadata.version,
                "category": self.metadata.category,
            },
            "over_permissions": self.over_permissions,
            "patterns": self.patterns,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)


