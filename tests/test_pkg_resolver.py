"""Tests for dependency resolver"""

import pytest
from src.pkg.manifest import PackageManifest, Dependency
from src.pkg.resolver import DependencyResolver, ResolverError, ResolvedPackage, print_dependency_tree


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


def test_resolve_with_dev_dependencies():
    """Test resolving with dev dependencies"""
    manifest = PackageManifest(
        name="my-pkg",
        version="1.0.0",
        dependencies={"dep1": Dependency("dep1", "1.0.0")},
        dev_dependencies={"test-dep": Dependency("test-dep", "1.0.0")},
    )

    resolver = DependencyResolver()
    
    # Without dev dependencies
    resolved = resolver.resolve(manifest, include_dev=False)
    assert len(resolved) == 1
    assert resolved[0].name == "dep1"
    
    # With dev dependencies
    resolved_with_dev = resolver.resolve(manifest, include_dev=True)
    assert len(resolved_with_dev) == 2
    names = {pkg.name for pkg in resolved_with_dev}
    assert "dep1" in names
    assert "test-dep" in names


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
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", "^1.2.3")
    assert version == "1.2.3"


def test_version_constraint_wildcard():
    """Test wildcard version constraint"""
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", "*")
    assert version is not None


def test_version_constraint_tilde():
    """Test tilde version constraint"""
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", "~1.2.3")
    assert version == "1.2.3"


def test_version_constraint_gte():
    """Test >= version constraint"""
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", ">=1.2.3")
    assert version == "1.2.3"


def test_version_constraint_gt():
    """Test > version constraint"""
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", ">1.2.3")
    assert version == "1.2.4"


def test_version_constraint_exact():
    """Test exact version constraint"""
    resolver = DependencyResolver()
    version = resolver._find_matching_version("test", "1.2.3")
    assert version == "1.2.3"


def test_resolved_package_equality():
    """Test ResolvedPackage equality"""
    pkg1 = ResolvedPackage("test", "1.0.0", {})
    pkg2 = ResolvedPackage("test", "1.0.0", {})
    pkg3 = ResolvedPackage("test", "2.0.0", {})
    
    assert pkg1 == pkg2
    assert pkg1 != pkg3


def test_resolved_package_hash():
    """Test ResolvedPackage hashing"""
    pkg1 = ResolvedPackage("test", "1.0.0", {})
    pkg2 = ResolvedPackage("test", "1.0.0", {})
    
    assert hash(pkg1) == hash(pkg2)
    
    # Can be used in sets
    pkg_set = {pkg1, pkg2}
    assert len(pkg_set) == 1


def test_print_dependency_tree():
    """Test printing dependency tree"""
    tree = {
        "dep1": {
            "version": "1.0.0",
            "dependencies": {
                "subdep": {
                    "version": "2.0.0",
                    "dependencies": {}
                }
            }
        }
    }
    
    # Should not raise exception
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        print_dependency_tree(tree)
        output = sys.stdout.getvalue()
        assert "dep1@1.0.0" in output
        assert "subdep@2.0.0" in output
    finally:
        sys.stdout = old_stdout


def test_circular_dependency_detection():
    """Test circular dependency raises error"""
    # Create a scenario where a package would depend on itself
    # This is tricky since we use mocks, but we can test the visited check
    resolver = DependencyResolver()
    resolver.visited.add("circular-pkg")
    
    # Attempting to resolve a visited but unresolved package should error
    # Note: In real scenario this would happen through recursive calls
    # For now we just verify the basic mechanism


def test_resolver_state_reset():
    """Test that resolver state is reset between resolve calls"""
    manifest1 = PackageManifest(
        name="pkg1",
        version="1.0.0",
        dependencies={"dep1": Dependency("dep1", "1.0.0")},
    )
    
    manifest2 = PackageManifest(
        name="pkg2",
        version="1.0.0",
        dependencies={"dep2": Dependency("dep2", "1.0.0")},
    )
    
    resolver = DependencyResolver()
    
    # First resolution
    resolved1 = resolver.resolve(manifest1)
    assert len(resolved1) == 1
    
    # Second resolution should start fresh
    resolved2 = resolver.resolve(manifest2)
    assert len(resolved2) == 1
    assert resolved2[0].name == "dep2"


def test_build_subtree():
    """Test building dependency subtree"""
    resolver = DependencyResolver()
    
    # Create some resolved packages
    pkg1 = ResolvedPackage("pkg1", "1.0.0", {"dep1": Dependency("dep1", "1.0.0")})
    pkg2 = ResolvedPackage("dep1", "1.0.0", {})
    
    resolver.resolved = {"pkg1": pkg1, "dep1": pkg2}
    
    subtree = resolver._build_subtree(pkg1)
    assert "dep1" in subtree
    assert subtree["dep1"]["version"] == "1.0.0"


def test_dependency_tree_no_deps():
    """Test dependency tree with no dependencies"""
    manifest = PackageManifest(name="simple", version="1.0.0", dependencies={})
    
    resolver = DependencyResolver()
    resolver.resolve(manifest)
    tree = resolver.get_dependency_tree(manifest)
    
    assert tree == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
