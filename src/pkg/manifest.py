"""
Package Manifest Parser

Handles parsing and validation of package manifest files (syntari.toml).
"""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Dependency:
    """Represents a package dependency with version constraints"""

    name: str
    version_constraint: str
    source: Optional[str] = None

    def matches_version(self, version: str) -> bool:
        """
        Check if a version satisfies this dependency's constraint.

        Supports:
        - Exact: "1.0.0"
        - Caret: "^1.0.0" (matches 1.x.x but not 2.x.x)
        - Tilde: "~1.2.0" (matches 1.2.x but not 1.3.x)
        - Greater than or equal: ">=1.0.0"
        - Greater than: ">1.0.0"
        - Less than or equal: "<=2.0.0"
        - Less than: "<2.0.0"
        - Wildcard: "*" (matches any version)
        """
        constraint = self.version_constraint.strip()

        # Wildcard matches any version
        if constraint == "*":
            return True

        # Caret constraint: ^1.2.3 allows >=1.2.3 and <2.0.0
        if constraint.startswith("^"):
            min_version = constraint[1:]
            parts = min_version.split(".")

            # Must be >= min_version
            if self._compare_versions(version, min_version) < 0:
                return False

            # Must have same major version
            version_parts = version.split(".")
            if len(parts) > 0 and len(version_parts) > 0:
                return version_parts[0] == parts[0]

            return True

        # Tilde constraint: ~1.2.3 allows >=1.2.3 and <1.3.0
        if constraint.startswith("~"):
            min_version = constraint[1:]
            parts = min_version.split(".")

            # Must be >= min_version
            if self._compare_versions(version, min_version) < 0:
                return False

            # Must have same major.minor if patch specified, otherwise just major
            version_parts = version.split(".")
            if len(parts) >= 2:
                # Has major.minor - match both
                return (
                    len(version_parts) >= 2
                    and version_parts[0] == parts[0]
                    and version_parts[1] == parts[1]
                )
            elif len(parts) == 1:
                # Only major version - match major
                return len(version_parts) >= 1 and version_parts[0] == parts[0]

            return True

        # Greater than or equal: >=1.0.0
        if constraint.startswith(">="):
            min_version = constraint[2:]
            return self._compare_versions(version, min_version) >= 0

        # Greater than: >1.0.0
        if constraint.startswith(">"):
            min_version = constraint[1:]
            return self._compare_versions(version, min_version) > 0

        # Less than or equal: <=2.0.0
        if constraint.startswith("<="):
            max_version = constraint[2:]
            return self._compare_versions(version, max_version) <= 0

        # Less than: <2.0.0
        if constraint.startswith("<"):
            max_version = constraint[1:]
            return self._compare_versions(version, max_version) < 0

        # Exact version match
        return version == constraint

    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        """
        Compare two semantic versions.

        Returns:
        - -1 if v1 < v2
        - 0 if v1 == v2
        - 1 if v1 > v2
        """
        # Remove pre-release and build metadata for comparison
        v1_base = v1.split("-")[0].split("+")[0]
        v2_base = v2.split("-")[0].split("+")[0]

        parts1 = [int(p) for p in v1_base.split(".")]
        parts2 = [int(p) for p in v2_base.split(".")]

        # Pad shorter version with zeros
        max_len = max(len(parts1), len(parts2))
        parts1 += [0] * (max_len - len(parts1))
        parts2 += [0] * (max_len - len(parts2))

        # Compare each part
        for p1, p2 in zip(parts1, parts2):
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1

        return 0


@dataclass
class PackageManifest:
    """Represents a package manifest (syntari.toml)"""

    name: str
    version: str
    description: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    license: Optional[str] = None
    dependencies: Dict[str, Dependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, Dependency] = field(default_factory=dict)
    entry_point: str = "main.syn"
    compile_to_bytecode: bool = True

    def validate(self) -> List[str]:
        """
        Validate the manifest.

        Returns list of error messages (empty if valid).
        """
        errors = []

        # Name is required
        if not self.name or not self.name.strip():
            errors.append("Package name is required")
        elif not self._is_valid_package_name(self.name):
            errors.append(
                f"Invalid package name '{self.name}'. Must be lowercase, alphanumeric, "
                "with dashes or underscores, and cannot start with a number"
            )

        # Version is required
        if not self.version or not self.version.strip():
            errors.append("Package version is required")
        elif not self._is_valid_version(self.version):
            errors.append(f"Invalid version '{self.version}'. Must be valid semantic version")

        # Check for circular dependency (package depending on itself)
        if self.name in self.dependencies:
            errors.append(f"Package '{self.name}' cannot depend on itself")

        if self.name in self.dev_dependencies:
            errors.append(f"Package '{self.name}' cannot depend on itself")

        return errors

    @classmethod
    def from_dict(cls, data: Dict) -> "PackageManifest":
        """
        Parse manifest from dictionary (loaded from TOML).

        Args:
            data: Dictionary representation of manifest

        Returns:
            PackageManifest instance

        Raises:
            ValueError: If manifest is invalid
        """
        if "package" not in data:
            raise ValueError("Missing [package] section in manifest")

        package_data = data["package"]

        # Required fields
        name = package_data.get("name", "").strip()
        version = package_data.get("version", "").strip()

        if not name:
            raise ValueError("Package name is required")
        if not version:
            raise ValueError("Package version is required")

        # Validate name and version
        if not cls._is_valid_package_name(name):
            raise ValueError(
                f"Invalid package name '{name}'. Must be lowercase, alphanumeric, "
                "with dashes or underscores, and cannot start with a number"
            )

        if not cls._is_valid_version(version):
            raise ValueError(f"Invalid version '{version}'. Must be valid semantic version")

        # Optional fields
        description = package_data.get("description")
        authors = package_data.get("authors", [])
        license_val = package_data.get("license")

        # Parse dependencies
        dependencies = {}
        if "dependencies" in data:
            for dep_name, dep_spec in data["dependencies"].items():
                if isinstance(dep_spec, str):
                    # Simple version string
                    dependencies[dep_name] = Dependency(dep_name, dep_spec)
                elif isinstance(dep_spec, dict):
                    # Detailed specification with version and source
                    version_constraint = dep_spec.get("version", "*")
                    source = dep_spec.get("source")
                    dependencies[dep_name] = Dependency(dep_name, version_constraint, source)

        # Parse dev dependencies
        dev_dependencies = {}
        if "dev-dependencies" in data:
            for dep_name, dep_spec in data["dev-dependencies"].items():
                if isinstance(dep_spec, str):
                    # Simple version string
                    dev_dependencies[dep_name] = Dependency(dep_name, dep_spec)
                elif isinstance(dep_spec, dict):
                    # Detailed specification
                    version_constraint = dep_spec.get("version", "*")
                    source = dep_spec.get("source")
                    dev_dependencies[dep_name] = Dependency(dep_name, version_constraint, source)

        # Parse build configuration
        entry_point = "main.syn"
        compile_to_bytecode = True

        if "build" in data:
            build_data = data["build"]
            entry_point = build_data.get("entry_point", "main.syn")
            compile_to_bytecode = build_data.get("compile_to_bytecode", True)

        return cls(
            name=name,
            version=version,
            description=description,
            authors=authors,
            license=license_val,
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            entry_point=entry_point,
            compile_to_bytecode=compile_to_bytecode,
        )

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """
        Load manifest from TOML file.

        Args:
            path: Path to syntari.toml file

        Returns:
            PackageManifest instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If manifest is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Manifest file not found: {path}")

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls.from_dict(data)

    def to_dict(self) -> Dict:
        """
        Convert manifest to dictionary for serialization.

        Returns:
            Dictionary representation suitable for TOML serialization
        """
        result = {
            "package": {
                "name": self.name,
                "version": self.version,
            }
        }

        if self.description:
            result["package"]["description"] = self.description

        if self.authors:
            result["package"]["authors"] = self.authors

        if self.license:
            result["package"]["license"] = self.license

        # Add dependencies
        if self.dependencies:
            result["dependencies"] = {}
            for name, dep in self.dependencies.items():
                if dep.source:
                    result["dependencies"][name] = {
                        "version": dep.version_constraint,
                        "source": dep.source,
                    }
                else:
                    result["dependencies"][name] = dep.version_constraint

        # Add dev dependencies
        if self.dev_dependencies:
            result["dev-dependencies"] = {}
            for name, dep in self.dev_dependencies.items():
                if dep.source:
                    result["dev-dependencies"][name] = {
                        "version": dep.version_constraint,
                        "source": dep.source,
                    }
                else:
                    result["dev-dependencies"][name] = dep.version_constraint

        # Add build config
        result["build"] = {
            "entry_point": self.entry_point,
            "compile_to_bytecode": self.compile_to_bytecode,
        }

        return result

    @staticmethod
    def _is_valid_package_name(name: str) -> bool:
        """
        Validate package name.

        Package names must be lowercase, alphanumeric with dashes or underscores,
        and cannot start with a number.

        Args:
            name: Package name to validate

        Returns:
            True if valid, False otherwise
        """
        if not name:
            return False

        # Must be lowercase alphanumeric with dashes or underscores
        # Cannot start with a number
        pattern = r"^[a-z_][a-z0-9_-]*$"
        return bool(re.match(pattern, name))

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """
        Validate semantic version.

        Valid versions: 1.2.3, 1.2.3-alpha, 1.2.3+build.123, 1.2.3-beta.1+build.456

        Args:
            version: Version string to validate

        Returns:
            True if valid, False otherwise
        """
        if not version:
            return False

        # Semantic versioning pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
        return bool(re.match(pattern, version))


def create_default_manifest(name: str, version: str = "0.1.0") -> str:
    """
    Create a default manifest TOML string.

    Args:
        name: Package name
        version: Package version (default: "0.1.0")

    Returns:
        String containing default TOML manifest
    """
    return f"""[package]
name = "{name}"
version = "{version}"
description = "A Syntari package"
authors = []
license = "MIT"

[dependencies]
# Add your dependencies here
# example = "^1.0.0"

[dev-dependencies]
# Add development dependencies here
# test-framework = "^2.0.0"

[build]
entry_point = "main.syn"
compile_to_bytecode = true
"""
