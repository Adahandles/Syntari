"""
Dependency Resolver

Resolves package dependencies and determines installation order.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

from .manifest import PackageManifest, Dependency


class ResolverError(Exception):
    """Raised when dependency resolution fails"""

    pass


@dataclass
class ResolvedPackage:
    """A package with resolved version"""

    name: str
    version: str
    dependencies: Dict[str, Dependency]

    def __hash__(self):
        return hash((self.name, self.version))

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version


class DependencyResolver:
    """Resolves package dependencies and determines installation order"""

    def __init__(self, registry=None):
        self.registry = registry  # Will be implemented in registry.py
        self.resolved: Dict[str, ResolvedPackage] = {}
        self.visited: Set[str] = set()

    def resolve(
        self, manifest: PackageManifest, include_dev: bool = False
    ) -> List[ResolvedPackage]:
        """
        Resolve all dependencies for a package.

        Returns list of packages in installation order (dependencies first).
        """
        self.resolved = {}
        self.visited = set()

        # Collect all dependencies
        dependencies = dict(manifest.dependencies)
        if include_dev:
            dependencies.update(manifest.dev_dependencies)

        # Resolve each dependency recursively
        for dep_name, dep in dependencies.items():
            self._resolve_dependency(dep_name, dep)

        # Build dependency graph and return topologically sorted order
        return self._topological_sort()

    def _resolve_dependency(self, name: str, dep: Dependency):
        """Recursively resolve a single dependency"""

        # Check for circular dependencies
        if name in self.visited:
            if name not in self.resolved:
                raise ResolverError(f"Circular dependency detected: {name}")
            return

        self.visited.add(name)

        # Find a version that satisfies the constraint
        version = self._find_matching_version(name, dep.version_constraint)
        if not version:
            raise ResolverError(
                f"No version of '{name}' satisfies constraint '{dep.version_constraint}'"
            )

        # Check if we already resolved this package
        if name in self.resolved:
            existing = self.resolved[name]
            if existing.version != version:
                # Version conflict
                raise ResolverError(
                    f"Version conflict for '{name}': "
                    f"need {version} but already resolved to {existing.version}"
                )
            return

        # Get package manifest for this version
        package_manifest = self._get_package_manifest(name, version)
        if not package_manifest:
            raise ResolverError(f"Could not find manifest for '{name}@{version}'")

        # Create resolved package
        resolved_pkg = ResolvedPackage(
            name=name, version=version, dependencies=package_manifest.dependencies
        )
        self.resolved[name] = resolved_pkg

        # Recursively resolve this package's dependencies
        for sub_dep_name, sub_dep in package_manifest.dependencies.items():
            self._resolve_dependency(sub_dep_name, sub_dep)

    def _find_matching_version(self, name: str, constraint: str) -> Optional[str]:
        """Find a version that matches the constraint"""
        # For now, return a mock version
        # In full implementation, this would query the registry

        if constraint == "*":
            return "1.0.0"  # Latest version

        if constraint.startswith("^"):
            return constraint[1:]  # Return the minimum version

        if constraint.startswith("~"):
            return constraint[1:]

        if constraint.startswith(">="):
            return constraint[2:]

        if constraint.startswith(">"):
            # Return next patch version
            base = constraint[1:]
            parts = base.split(".")
            if len(parts) == 3:
                parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)

        # Exact version
        return constraint

    def _get_package_manifest(self, name: str, version: str) -> Optional[PackageManifest]:
        """Get package manifest from registry or cache"""
        # For now, return a mock manifest
        # In full implementation, this would fetch from registry/cache

        return PackageManifest(
            name=name, version=version, dependencies={}  # No transitive dependencies for mock
        )

    def _topological_sort(self) -> List[ResolvedPackage]:
        """
        Sort resolved packages in dependency order.

        Packages with no dependencies come first.
        """
        # Build adjacency list (package -> packages that depend on it)
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize in_degree for all packages
        for pkg in self.resolved.values():
            if pkg.name not in in_degree:
                in_degree[pkg.name] = 0

        # Build graph
        for pkg in self.resolved.values():
            for dep_name in pkg.dependencies.keys():
                if dep_name in self.resolved:
                    graph[dep_name].append(pkg.name)
                    in_degree[pkg.name] += 1

        # Kahn's algorithm for topological sort
        queue = deque()
        for pkg_name, degree in in_degree.items():
            if degree == 0:
                queue.append(pkg_name)

        result = []
        while queue:
            pkg_name = queue.popleft()
            result.append(self.resolved[pkg_name])

            for dependent in graph[pkg_name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles (shouldn't happen as we check earlier, but be safe)
        if len(result) != len(self.resolved):
            raise ResolverError("Circular dependency detected during topological sort")

        return result

    def get_dependency_tree(self, manifest: PackageManifest) -> Dict:
        """
        Get a hierarchical representation of the dependency tree.

        Returns a nested dictionary showing the dependency structure.
        """
        tree = {}

        for dep_name, dep in manifest.dependencies.items():
            if dep_name in self.resolved:
                pkg = self.resolved[dep_name]
                tree[dep_name] = {"version": pkg.version, "dependencies": self._build_subtree(pkg)}

        return tree

    def _build_subtree(self, pkg: ResolvedPackage) -> Dict:
        """Recursively build dependency subtree"""
        subtree = {}

        for dep_name in pkg.dependencies.keys():
            if dep_name in self.resolved:
                sub_pkg = self.resolved[dep_name]
                subtree[dep_name] = {
                    "version": sub_pkg.version,
                    "dependencies": self._build_subtree(sub_pkg),
                }

        return subtree


def print_dependency_tree(tree: Dict, indent: int = 0):
    """Pretty-print a dependency tree"""
    for name, info in tree.items():
        print("  " * indent + f"├── {name}@{info['version']}")
        if info["dependencies"]:
            print_dependency_tree(info["dependencies"], indent + 1)
