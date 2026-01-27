"""
Syntari Package Manager

Handles package installation, dependency resolution, and version management.
"""

from .manifest import PackageManifest, Dependency
from .resolver import DependencyResolver, ResolverError
from .cache import PackageCache
from .registry import PackageRegistry

__all__ = [
    "PackageManifest",
    "Dependency",
    "DependencyResolver",
    "ResolverError",
    "PackageCache",
    "PackageRegistry",
]
