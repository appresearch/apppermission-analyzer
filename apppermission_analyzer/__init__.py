"""
AppPermission Analyzer - A comprehensive tool for analyzing application permission requests and patterns.
"""

__version__ = "2.1.0"
__author__ = "Applied Science Research Institute"

from .analyzer import Analyzer
from .models import Permission, AppMetadata, AnalysisResult

__all__ = ["Analyzer", "Permission", "AppMetadata", "AnalysisResult"]


