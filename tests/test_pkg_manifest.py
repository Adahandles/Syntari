"""Tests for package manifest parser"""

import pytest
from pathlib import Path
from src.pkg.manifest import PackageManifest, Dependency, create_default_manifest


def test_dependency_version_matching():
    """Test dependency version constraint matching"""
    dep = Dependency("test-pkg", "^1.0.0")
    
    assert dep.matches_version("1.0.0")
    assert dep.matches_version("1.5.0")
    assert not dep.matches_version("2.0.0")
    
    dep_tilde = Dependency("test-pkg", "~1.2.0")
    assert dep_tilde.matches_version("1.2.0")
    assert dep_tilde.matches_version("1.2.5")
    assert not dep_tilde.matches_version("1.3.0")
    
    dep_gte = Dependency("test-pkg", ">=1.0.0")
    assert dep_gte.matches_version("1.0.0")
    assert dep_gte.matches_version("2.0.0")
    assert not dep_gte.matches_version("0.9.0")
    
    dep_exact = Dependency("test-pkg", "1.0.0")
    assert dep_exact.matches_version("1.0.0")
    assert not dep_exact.matches_version("1.0.1")


def test_manifest_validation():
    """Test manifest validation"""
    # Valid manifest
    manifest = PackageManifest(
        name="test-package",
        version="1.0.0",
        description="A test package"
    )
    errors = manifest.validate()
    assert len(errors) == 0
    
    # Invalid name
    manifest_bad_name = PackageManifest(
        name="Test Package",  # Spaces not allowed
        version="1.0.0"
    )
    errors = manifest_bad_name.validate()
    assert len(errors) > 0
    assert any("Invalid package name" in e for e in errors)
    
    # Invalid version
    manifest_bad_version = PackageManifest(
        name="test-package",
        version="1.0"  # Not semver
    )
    errors = manifest_bad_version.validate()
    assert len(errors) > 0
    assert any("Invalid version" in e for e in errors)


def test_manifest_from_dict():
    """Test parsing manifest from dictionary"""
    data = {
        'package': {
            'name': 'my-package',
            'version': '1.0.0',
            'description': 'Test package',
            'authors': ['Test Author'],
            'license': 'MIT'
        },
        'dependencies': {
            'core': '^1.0.0',
            'utils': '~2.0.0'
        },
        'dev-dependencies': {
            'test-framework': '1.0.0'
        },
        'build': {
            'entry_point': 'main.syn',
            'compile_to_bytecode': True
        }
    }
    
    manifest = PackageManifest.from_dict(data)
    
    assert manifest.name == 'my-package'
    assert manifest.version == '1.0.0'
    assert manifest.description == 'Test package'
    assert len(manifest.dependencies) == 2
    assert 'core' in manifest.dependencies
    assert manifest.dependencies['core'].version_constraint == '^1.0.0'
    assert len(manifest.dev_dependencies) == 1
    assert manifest.entry_point == 'main.syn'
    assert manifest.compile_to_bytecode is True


def test_create_default_manifest():
    """Test default manifest generation"""
    content = create_default_manifest("my-pkg", "0.1.0")
    
    assert 'name = "my-pkg"' in content
    assert 'version = "0.1.0"' in content
    assert '[package]' in content
    assert '[dependencies]' in content
    assert '[dev-dependencies]' in content
    assert '[build]' in content


def test_manifest_to_dict():
    """Test converting manifest to dictionary"""
    manifest = PackageManifest(
        name="test-pkg",
        version="1.0.0",
        description="Test",
        dependencies={
            'dep1': Dependency('dep1', '^1.0.0')
        }
    )
    
    data = manifest.to_dict()
    
    assert data['package']['name'] == 'test-pkg'
    assert data['package']['version'] == '1.0.0'
    assert 'dep1' in data['dependencies']
    assert data['dependencies']['dep1'] == '^1.0.0'


def test_circular_dependency_detection():
    """Test self-dependency detection"""
    manifest = PackageManifest(
        name="my-package",
        version="1.0.0",
        dependencies={
            'my-package': Dependency('my-package', '1.0.0')
        }
    )
    
    errors = manifest.validate()
    assert len(errors) > 0
    assert any("cannot depend on itself" in e for e in errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
