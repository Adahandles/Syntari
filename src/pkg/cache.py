"""
Package Cache

Manages local cache of downloaded packages.
"""

import shutil
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class PackageCache:
    """Manages local package cache"""

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            # Default to ~/.syntari/cache
            cache_dir = Path.home() / ".syntari" / "cache"

        self.cache_dir = Path(cache_dir)
        self.packages_dir = self.cache_dir / "packages"
        self.metadata_dir = self.cache_dir / "metadata"

        # Create directories
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def get_package_path(self, name: str, version: str) -> Path:
        """Get path to cached package directory"""
        return self.packages_dir / f"{name}-{version}"

    def is_cached(self, name: str, version: str) -> bool:
        """Check if package is in cache"""
        pkg_path = self.get_package_path(name, version)
        return pkg_path.exists() and pkg_path.is_dir()

    def add_package(
        self, name: str, version: str, source_path: Path, checksum: Optional[str] = None
    ) -> Path:
        """
        Add a package to the cache.

        Args:
            name: Package name
            version: Package version
            source_path: Path to package source directory
            checksum: Optional SHA256 checksum for verification

        Returns:
            Path to cached package
        """
        pkg_path = self.get_package_path(name, version)

        # Remove if already exists
        if pkg_path.exists():
            shutil.rmtree(pkg_path)

        # Copy package to cache
        shutil.copytree(source_path, pkg_path)

        # Verify checksum if provided
        if checksum:
            actual_checksum = self._compute_checksum(pkg_path)
            if actual_checksum != checksum:
                shutil.rmtree(pkg_path)
                raise ValueError(
                    f"Checksum mismatch for {name}@{version}: "
                    f"expected {checksum}, got {actual_checksum}"
                )

        # Store metadata
        metadata = {
            "name": name,
            "version": version,
            "cached_at": datetime.now().isoformat(),
            "checksum": checksum or self._compute_checksum(pkg_path),
            "size_bytes": self._get_directory_size(pkg_path),
        }
        self._save_metadata(name, version, metadata)

        return pkg_path

    def get_metadata(self, name: str, version: str) -> Optional[Dict]:
        """Get package metadata from cache"""
        metadata_file = self.metadata_dir / f"{name}-{version}.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, "r") as f:
            return json.load(f)

    def _save_metadata(self, name: str, version: str, metadata: Dict):
        """Save package metadata"""
        metadata_file = self.metadata_dir / f"{name}-{version}.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def remove_package(self, name: str, version: str) -> bool:
        """
        Remove a package from cache.

        Returns True if package was removed, False if not found.
        """
        pkg_path = self.get_package_path(name, version)
        metadata_file = self.metadata_dir / f"{name}-{version}.json"

        removed = False

        if pkg_path.exists():
            shutil.rmtree(pkg_path)
            removed = True

        if metadata_file.exists():
            metadata_file.unlink()
            removed = True

        return removed

    def list_cached_packages(self) -> List[Dict]:
        """List all cached packages with metadata"""
        packages = []

        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                packages.append(metadata)

        return sorted(packages, key=lambda p: p["name"])

    def clear_cache(self) -> int:
        """
        Clear all cached packages.

        Returns number of packages removed.
        """
        count = 0

        for pkg_dir in self.packages_dir.iterdir():
            if pkg_dir.is_dir():
                shutil.rmtree(pkg_dir)
                count += 1

        for metadata_file in self.metadata_dir.glob("*.json"):
            metadata_file.unlink()

        return count

    def get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        return self._get_directory_size(self.packages_dir)

    def _compute_checksum(self, path: Path) -> str:
        """Compute SHA256 checksum of directory contents"""
        hasher = hashlib.sha256()

        # Sort files for consistent ordering
        files = sorted(path.rglob("*"))

        for file_path in files:
            if file_path.is_file():
                # Include relative path in hash
                rel_path = file_path.relative_to(path)
                hasher.update(str(rel_path).encode())

                # Include file contents
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)

        return hasher.hexdigest()

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0

        for file_path in path.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size

        return total

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format byte size as human-readable string"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
