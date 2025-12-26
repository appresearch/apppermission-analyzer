"""
Main analyzer class for processing application permissions.
"""

import os
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from .models import Permission, AppMetadata, AnalysisResult


class Analyzer:
    """Main analyzer class for application permission analysis."""

    def __init__(self):
        """Initialize the analyzer."""
        self.android_permissions = self._load_android_permissions()
        self.ios_permissions = self._load_ios_permissions()

    def analyze(self, app_path: str) -> AnalysisResult:
        """
        Analyze an application file and extract permission information.

        Args:
            app_path: Path to the application file (.apk, .ipa, or directory)

        Returns:
            AnalysisResult object containing analysis results
        """
        app_path = Path(app_path)

        if not app_path.exists():
            raise FileNotFoundError(f"Application file not found: {app_path}")

        # Detect platform
        if app_path.suffix == ".apk" or (app_path.is_dir() and "AndroidManifest.xml" in str(app_path)):
            return self._analyze_android(app_path)
        elif app_path.suffix == ".ipa" or (app_path.is_dir() and "Info.plist" in str(app_path)):
            return self._analyze_ios(app_path)
        else:
            raise ValueError(f"Unsupported application format: {app_path.suffix}")

    def _analyze_android(self, app_path: Path) -> AnalysisResult:
        """Analyze Android application."""
        metadata = self._extract_android_metadata(app_path)
        permissions = self._extract_android_permissions(app_path)

        # Analyze patterns
        over_permissions = self._detect_over_permissioning(permissions, metadata)
        patterns = self._identify_patterns(permissions)

        return AnalysisResult(
            app_id=metadata.package_name,
            platform="Android",
            permissions=permissions,
            metadata=metadata,
            over_permissions=over_permissions,
            patterns=patterns,
        )

    def _analyze_ios(self, app_path: Path) -> AnalysisResult:
        """Analyze iOS application."""
        metadata = self._extract_ios_metadata(app_path)
        permissions = self._extract_ios_permissions(app_path)

        # Analyze patterns
        over_permissions = self._detect_over_permissioning(permissions, metadata)
        patterns = self._identify_patterns(permissions)

        return AnalysisResult(
            app_id=metadata.package_name,
            platform="iOS",
            permissions=permissions,
            metadata=metadata,
            over_permissions=over_permissions,
            patterns=patterns,
        )

    def _extract_android_metadata(self, app_path: Path) -> AppMetadata:
        """Extract metadata from Android application."""
        # Try to use aapt if available
        try:
            result = subprocess.run(
                ["aapt", "dump", "badging", str(app_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return self._parse_aapt_output(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: try to extract from AndroidManifest.xml if app is unzipped
        manifest_path = app_path / "AndroidManifest.xml"
        if manifest_path.exists():
            return self._parse_manifest(manifest_path)

        # Default metadata
        return AppMetadata(
            package_name=app_path.stem,
            app_name=app_path.stem,
            version="unknown",
            category="unknown",
        )

    def _extract_android_permissions(self, app_path: Path) -> List[Permission]:
        """Extract permissions from Android application."""
        permissions = []

        # Try aapt first
        try:
            result = subprocess.run(
                ["aapt", "dump", "permissions", str(app_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("permission:"):
                        perm_name = line.split(":")[1].strip()
                        permissions.append(
                            Permission(
                                name=perm_name,
                                category=self._categorize_permission(perm_name),
                                risk_level=self._assess_risk(perm_name),
                            )
                        )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: parse AndroidManifest.xml
        manifest_path = app_path / "AndroidManifest.xml"
        if manifest_path.exists():
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            for perm in root.findall(".//uses-permission"):
                perm_name = perm.get("{http://schemas.android.com/apk/res/android}name", "")
                if perm_name:
                    permissions.append(
                        Permission(
                            name=perm_name,
                            category=self._categorize_permission(perm_name),
                            risk_level=self._assess_risk(perm_name),
                        )
                    )

        return permissions

    def _extract_ios_metadata(self, app_path: Path) -> AppMetadata:
        """Extract metadata from iOS application."""
        # Look for Info.plist
        info_plist_path = None
        if app_path.is_dir():
            info_plist_path = app_path / "Info.plist"
        else:
            # Try to unzip and find Info.plist
            pass

        if info_plist_path and info_plist_path.exists():
            return self._parse_info_plist(info_plist_path)

        return AppMetadata(
            package_name=app_path.stem,
            app_name=app_path.stem,
            version="unknown",
            category="unknown",
        )

    def _extract_ios_permissions(self, app_path: Path) -> List[Permission]:
        """Extract permissions from iOS application."""
        permissions = []
        # iOS permissions are typically in Info.plist under usage descriptions
        info_plist_path = app_path / "Info.plist"
        if info_plist_path.exists():
            # Parse Info.plist for usage descriptions
            pass
        return permissions

    def _detect_over_permissioning(
        self, permissions: List[Permission], metadata: AppMetadata
    ) -> List[str]:
        """Detect potentially unnecessary permissions."""
        over_permissions = []
        # Simple heuristic: check for permissions that don't match common app categories
        # This is a simplified version - real implementation would be more sophisticated
        return over_permissions

    def _identify_patterns(self, permissions: List[Permission]) -> Dict[str, any]:
        """Identify patterns in permission usage."""
        patterns = {
            "total_count": len(permissions),
            "categories": {},
            "high_risk_count": sum(1 for p in permissions if p.risk_level == "high"),
        }
        for perm in permissions:
            cat = perm.category
            patterns["categories"][cat] = patterns["categories"].get(cat, 0) + 1
        return patterns

    def _categorize_permission(self, perm_name: str) -> str:
        """Categorize a permission by name."""
        perm_lower = perm_name.lower()
        if "location" in perm_lower or "gps" in perm_lower:
            return "Location"
        elif "camera" in perm_lower:
            return "Camera"
        elif "contact" in perm_lower or "phone" in perm_lower:
            return "Contacts"
        elif "storage" in perm_lower or "read_external" in perm_lower or "write_external" in perm_lower:
            return "Storage"
        elif "internet" in perm_lower or "network" in perm_lower:
            return "Network"
        elif "sms" in perm_lower or "call" in perm_lower:
            return "Communication"
        else:
            return "Other"

    def _assess_risk(self, perm_name: str) -> str:
        """Assess risk level of a permission."""
        high_risk_perms = [
            "location",
            "camera",
            "microphone",
            "contacts",
            "sms",
            "phone",
            "call",
        ]
        perm_lower = perm_name.lower()
        if any(risk in perm_lower for risk in high_risk_perms):
            return "high"
        elif "storage" in perm_lower or "internet" in perm_lower:
            return "medium"
        else:
            return "low"

    def _load_android_permissions(self) -> Set[str]:
        """Load known Android permissions."""
        # This would typically load from a comprehensive list
        return set()

    def _load_ios_permissions(self) -> Set[str]:
        """Load known iOS permissions."""
        return set()

    def _parse_aapt_output(self, output: str) -> AppMetadata:
        """Parse aapt output to extract metadata."""
        metadata = {"package_name": "unknown", "app_name": "unknown", "version": "unknown", "category": "unknown"}
        for line in output.split("\n"):
            if line.startswith("package: name="):
                metadata["package_name"] = line.split("'")[1]
            elif line.startswith("application-label:"):
                metadata["app_name"] = line.split(":")[1].strip()
            elif line.startswith("versionCode="):
                metadata["version"] = line.split("=")[1].split()[0]
        return AppMetadata(**metadata)

    def _parse_manifest(self, manifest_path: Path) -> AppMetadata:
        """Parse AndroidManifest.xml."""
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            package_name = root.get("package", "unknown")
            return AppMetadata(
                package_name=package_name,
                app_name=package_name,
                version="unknown",
                category="unknown",
            )
        except Exception:
            return AppMetadata(
                package_name="unknown",
                app_name="unknown",
                version="unknown",
                category="unknown",
            )

    def _parse_info_plist(self, plist_path: Path) -> AppMetadata:
        """Parse iOS Info.plist."""
        # Simplified - would use proper plist parser in production
        return AppMetadata(
            package_name=plist_path.parent.name,
            app_name=plist_path.parent.name,
            version="unknown",
            category="unknown",
        )



