"""
Package Registry

Handles communication with package registry for downloading packages.
"""

from typing import Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass


@dataclass
class RegistryPackage:
    """Package information from registry"""

    name: str
    version: str
    description: str
    author: str
    download_url: str
    checksum: str
    dependencies: Dict[str, str]


class PackageRegistry:
    """
    Interface to Syntari package registry.

    For v0.4, this is a stub implementation.
    In production, this would connect to a remote registry server.
    """

    def __init__(self, registry_url: str = "https://registry.syntari.dev"):
        self.registry_url = registry_url
        self.local_index: Dict[str, Dict[str, RegistryPackage]] = {}

    def search(self, query: str) -> List[RegistryPackage]:
        """
        Search for packages in registry.

        Args:
            query: Search query (package name or keyword)

        Returns:
            List of matching packages
        """
        # Stub implementation
        # In production: HTTP request to registry API
        results = []

        for pkg_name, versions in self.local_index.items():
            if query.lower() in pkg_name.lower():
                # Return latest version
                latest = max(versions.keys())
                results.append(versions[latest])

        return results

    def get_package_info(self, name: str, version: str) -> Optional[RegistryPackage]:
        """
        Get package information from registry.

        Args:
            name: Package name
            version: Package version

        Returns:
            Package info or None if not found
        """
        # Stub implementation
        if name in self.local_index:
            return self.local_index[name].get(version)
        return None

    def get_available_versions(self, name: str) -> List[str]:
        """
        Get all available versions of a package.

        Args:
            name: Package name

        Returns:
            List of version strings, sorted newest to oldest
        """
        if name not in self.local_index:
            return []

        versions = list(self.local_index[name].keys())
        # Sort by semantic version (descending)
        versions.sort(key=lambda v: [int(x) for x in v.split(".")], reverse=True)
        return versions

    def download_package(self, name: str, version: str, dest_dir: Path) -> Path:
        """
        Download a package from registry.

        Args:
            name: Package name
            version: Package version
            dest_dir: Destination directory

        Returns:
            Path to downloaded package
        """
        # Stub implementation
        # In production: HTTP download from registry

        pkg_info = self.get_package_info(name, version)
        if not pkg_info:
            raise ValueError(f"Package {name}@{version} not found in registry")

        # For now, just create a placeholder directory
        pkg_dir = dest_dir / f"{name}-{version}"
        pkg_dir.mkdir(parents=True, exist_ok=True)

        # Create a basic syntari.toml
        manifest_path = pkg_dir / "syntari.toml"
        manifest_path.write_text(f"""[package]
name = "{name}"
version = "{version}"
description = "{pkg_info.description}"

[dependencies]
""")

        return pkg_dir

    def publish_package(self, manifest_path: Path, package_dir: Path, api_key: str) -> bool:
        """
        Publish a package to registry.

        Args:
            manifest_path: Path to syntari.toml
            package_dir: Path to package source
            api_key: Registry API key

        Returns:
            True if successful
        """
        # Stub implementation
        # In production: HTTP POST to registry API
        print(f"[Registry] Publishing package from {package_dir}")
        print(f"[Registry] Stub implementation - not actually publishing")
        return True

    def add_local_package(self, package: RegistryPackage):
        """Add a package to local index (for testing)"""
        if package.name not in self.local_index:
            self.local_index[package.name] = {}
        self.local_index[package.name][package.version] = package
