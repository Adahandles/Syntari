"""Tests for dependency resolver"""

import pytest
from src.pkg.manifest import PackageManifest, Dependency
from src.pkg.resolver import DependencyResolver, ResolverError, ResolvedPackage


def test_resolve_no_dependencies():
    """Test resolving a package with no dependencies"""
    manifest = PackageManifest(name="simple-pkg", version="1.0.0", dependencies={})

    resolver = DependencyResolver()
    resolved = resolver.resolve(manifest)

    assert len(resolved) == 0


def test_resolve_simple_dependencies():
    """Test resolving simple dependencies"""
    manifest = PackageManifest(
        name="my-pkg",
        version="1.0.0",
        dependencies={"dep1": Dependency("dep1", "1.0.0"), "dep2": Dependency("dep2", "2.0.0")},
    )

    resolver = DependencyResolver()
    resolved = resolver.resolve(manifest)

    assert len(resolved) == 2
    names = {pkg.name for pkg in resolved}
    assert "dep1" in names
    assert "dep2" in names


def test_topological_sort():
    """Test dependency ordering (dependencies come before dependents)"""
    manifest = PackageManifest(
        name="my-pkg",
        version="1.0.0",
        dependencies={
            "dep1": Dependency("dep1", "1.0.0"),
        },
    )

    resolver = DependencyResolver()
    resolved = resolver.resolve(manifest)

    # dep1 should come before my-pkg in installation order
    assert len(resolved) >= 1
    assert resolved[0].name == "dep1"


def test_dependency_tree():
    """Test building dependency tree"""
    manifest = PackageManifest(
        name="root",
        version="1.0.0",
        dependencies={
            "child1": Dependency("child1", "1.0.0"),
            "child2": Dependency("child2", "1.0.0"),
        },
    )

    resolver = DependencyResolver()
    resolver.resolve(manifest)
    tree = resolver.get_dependency_tree(manifest)

    assert "child1" in tree
    assert "child2" in tree
    assert tree["child1"]["version"] == "1.0.0"


def test_version_constraint_caret():
    """Test caret version constraint resolution"""
    dep = Dependency("test", "^1.2.3")
    resolver = DependencyResolver()

    version = resolver._find_matching_version("test", "^1.2.3")
    assert version == "1.2.3"


def test_version_constraint_wildcard():
    """Test wildcard version constraint"""
    dep = Dependency("test", "*")
    resolver = DependencyResolver()

    version = resolver._find_matching_version("test", "*")
    assert version is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
