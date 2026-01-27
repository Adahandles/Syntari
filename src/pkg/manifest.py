"""
Package Manifest Parser

Handles parsing and validation of syntari.toml package manifests.
"""

import tomllib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class Dependency:
    """Represents a package dependency"""

    name: str
    version_constraint: str
    source: str = "registry"  # registry, git, path

    def matches_version(self, version: str) -> bool:
        """Check if a version satisfies this dependency's constraint"""
        # Simple version matching for now
        # Supports: "1.0.0", "^1.0.0", "~1.0.0", ">=1.0.0", "*"

        if self.version_constraint == "*":
            return True

        if self.version_constraint.startswith("^"):
            # Caret: compatible with version (major version must match)
            required = self.version_constraint[1:]
            return version.startswith(required.split(".")[0])

        if self.version_constraint.startswith("~"):
            # Tilde: compatible with minor version
            required = self.version_constraint[1:]
            parts = required.split(".")
            if len(parts) >= 2:
                return version.startswith(f"{parts[0]}.{parts[1]}")
            return version.startswith(parts[0])

        if self.version_constraint.startswith(">="):
            required = self.version_constraint[2:]
            return self._compare_versions(version, required) >= 0

        if self.version_constraint.startswith(">"):
            required = self.version_constraint[1:]
            return self._compare_versions(version, required) > 0

        if self.version_constraint.startswith("<="):
            required = self.version_constraint[2:]
            return self._compare_versions(version, required) <= 0

        if self.version_constraint.startswith("<"):
            required = self.version_constraint[1:]
            return self._compare_versions(version, required) < 0

        # Exact match
        return version == self.version_constraint

    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns -1, 0, or 1"""
        parts1 = [int(x) for x in v1.split(".")]
        parts2 = [int(x) for x in v2.split(".")]

        # Pad to same length
        while len(parts1) < len(parts2):
            parts1.append(0)
        while len(parts2) < len(parts1):
            parts2.append(0)

        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            if p1 > p2:
                return 1
        return 0


@dataclass
class PackageManifest:
    """Represents a syntari.toml package manifest"""

    # [package]
    name: str
    version: str
    description: str = ""
    authors: List[str] = field(default_factory=list)
    license: str = ""
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)

    # [dependencies]
    dependencies: Dict[str, Dependency] = field(default_factory=dict)

    # [dev-dependencies]
    dev_dependencies: Dict[str, Dependency] = field(default_factory=dict)

    # [build]
    entry_point: Optional[str] = None
    compile_to_bytecode: bool = False

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """Load manifest from syntari.toml file"""
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict) -> "PackageManifest":
        """Parse manifest from dictionary"""

        # Validate required fields
        package_data = data.get("package", {})
        if "name" not in package_data:
            raise ValueError("Package name is required")
        if "version" not in package_data:
            raise ValueError("Package version is required")

        # Validate package name
        name = package_data["name"]
        if not cls._is_valid_package_name(name):
            raise ValueError(
                f"Invalid package name '{name}'. "
                "Must contain only lowercase letters, numbers, hyphens, and underscores"
            )

        # Validate version
        version = package_data["version"]
        if not cls._is_valid_version(version):
            raise ValueError(f"Invalid version '{version}'. Must be in semver format (e.g., 1.0.0)")

        # Parse dependencies
        dependencies = {}
        for dep_name, dep_value in data.get("dependencies", {}).items():
            if isinstance(dep_value, str):
                # Simple version string
                dependencies[dep_name] = Dependency(dep_name, dep_value)
            elif isinstance(dep_value, dict):
                # Detailed dependency specification
                dependencies[dep_name] = Dependency(
                    name=dep_name,
                    version_constraint=dep_value.get("version", "*"),
                    source=dep_value.get("source", "registry"),
                )

        # Parse dev dependencies
        dev_dependencies = {}
        for dep_name, dep_value in data.get("dev-dependencies", {}).items():
            if isinstance(dep_value, str):
                dev_dependencies[dep_name] = Dependency(dep_name, dep_value)
            elif isinstance(dep_value, dict):
                dev_dependencies[dep_name] = Dependency(
                    name=dep_name,
                    version_constraint=dep_value.get("version", "*"),
                    source=dep_value.get("source", "registry"),
                )

        # Parse build configuration
        build_data = data.get("build", {})

        return cls(
            name=name,
            version=version,
            description=package_data.get("description", ""),
            authors=package_data.get("authors", []),
            license=package_data.get("license", ""),
            homepage=package_data.get("homepage", ""),
            repository=package_data.get("repository", ""),
            keywords=package_data.get("keywords", []),
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            entry_point=build_data.get("entry_point"),
            compile_to_bytecode=build_data.get("compile_to_bytecode", False),
        )

    @staticmethod
    def _is_valid_package_name(name: str) -> bool:
        """Validate package name format"""
        # Only lowercase letters, numbers, hyphens, underscores
        # Must start with letter
        pattern = r"^[a-z][a-z0-9_-]*$"
        return bool(re.match(pattern, name))

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Validate semantic version format"""
        pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$"
        return bool(re.match(pattern, version))

    def to_dict(self) -> Dict:
        """Convert manifest to dictionary"""
        return {
            "package": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "authors": self.authors,
                "license": self.license,
                "homepage": self.homepage,
                "repository": self.repository,
                "keywords": self.keywords,
            },
            "dependencies": {
                name: dep.version_constraint for name, dep in self.dependencies.items()
            },
            "dev-dependencies": {
                name: dep.version_constraint for name, dep in self.dev_dependencies.items()
            },
            "build": {
                "entry_point": self.entry_point,
                "compile_to_bytecode": self.compile_to_bytecode,
            },
        }

    def validate(self) -> List[str]:
        """Validate manifest and return list of errors"""
        errors = []

        if not self.name:
            errors.append("Package name is required")
        elif not self._is_valid_package_name(self.name):
            errors.append(f"Invalid package name: {self.name}")

        if not self.version:
            errors.append("Package version is required")
        elif not self._is_valid_version(self.version):
            errors.append(f"Invalid version: {self.version}")

        # Check for circular dependencies (self-reference)
        if self.name in self.dependencies:
            errors.append(f"Package cannot depend on itself: {self.name}")

        return errors


def create_default_manifest(name: str, version: str = "0.1.0") -> str:
    """Generate a default syntari.toml manifest"""
    return f"""[package]
name = "{name}"
version = "{version}"
description = "A Syntari package"
authors = []
license = ""

[dependencies]
# Example: core = "^1.0.0"

[dev-dependencies]
# Example: test-framework = "^1.0.0"

[build]
# entry_point = "main.syn"
# compile_to_bytecode = false
"""
