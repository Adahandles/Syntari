"""Tests for package manifest parser"""

import pytest
from pathlib import Path
from src.pkg.manifest import PackageManifest, Dependency, create_default_manifest
import tempfile


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


def test_dependency_wildcard():
    """Test wildcard version constraint"""
    dep = Dependency("test-pkg", "*")
    assert dep.matches_version("1.0.0")
    assert dep.matches_version("2.5.3")
    assert dep.matches_version("0.0.1")


def test_dependency_greater_than():
    """Test > version constraint"""
    dep = Dependency("test-pkg", ">1.0.0")
    assert dep.matches_version("1.0.1")
    assert dep.matches_version("2.0.0")
    assert not dep.matches_version("1.0.0")
    assert not dep.matches_version("0.9.0")


def test_dependency_less_than_or_equal():
    """Test <= version constraint"""
    dep = Dependency("test-pkg", "<=2.0.0")
    assert dep.matches_version("1.0.0")
    assert dep.matches_version("2.0.0")
    assert not dep.matches_version("2.0.1")


def test_dependency_less_than():
    """Test < version constraint"""
    dep = Dependency("test-pkg", "<2.0.0")
    assert dep.matches_version("1.9.9")
    assert dep.matches_version("1.0.0")
    assert not dep.matches_version("2.0.0")


def test_dependency_tilde_single_version():
    """Test tilde constraint with single version part"""
    dep = Dependency("test-pkg", "~1")
    assert dep.matches_version("1.0.0")
    assert dep.matches_version("1.9.9")


def test_dependency_version_compare():
    """Test version comparison logic"""
    assert Dependency._compare_versions("1.0.0", "1.0.0") == 0
    assert Dependency._compare_versions("1.0.1", "1.0.0") == 1
    assert Dependency._compare_versions("1.0.0", "1.0.1") == -1
    assert Dependency._compare_versions("2.0.0", "1.9.9") == 1


def test_manifest_validation():
    """Test manifest validation"""
    # Valid manifest
    manifest = PackageManifest(name="test-package", version="1.0.0", description="A test package")
    errors = manifest.validate()
    assert len(errors) == 0

    # Invalid name
    manifest_bad_name = PackageManifest(name="Test Package", version="1.0.0")  # Spaces not allowed
    errors = manifest_bad_name.validate()
    assert len(errors) > 0
    assert any("Invalid package name" in e for e in errors)

    # Invalid version
    manifest_bad_version = PackageManifest(name="test-package", version="1.0")  # Not semver
    errors = manifest_bad_version.validate()
    assert len(errors) > 0
    assert any("Invalid version" in e for e in errors)


def test_manifest_empty_name():
    """Test manifest with empty name"""
    manifest = PackageManifest(name="", version="1.0.0")
    errors = manifest.validate()
    assert len(errors) > 0
    assert any("name is required" in e for e in errors)


def test_manifest_empty_version():
    """Test manifest with empty version"""
    manifest = PackageManifest(name="test-pkg", version="")
    errors = manifest.validate()
    assert len(errors) > 0
    assert any("version is required" in e for e in errors)


def test_manifest_from_dict():
    """Test parsing manifest from dictionary"""
    data = {
        "package": {
            "name": "my-package",
            "version": "1.0.0",
            "description": "Test package",
            "authors": ["Test Author"],
            "license": "MIT",
        },
        "dependencies": {"core": "^1.0.0", "utils": "~2.0.0"},
        "dev-dependencies": {"test-framework": "1.0.0"},
        "build": {"entry_point": "main.syn", "compile_to_bytecode": True},
    }

    manifest = PackageManifest.from_dict(data)

    assert manifest.name == "my-package"
    assert manifest.version == "1.0.0"
    assert manifest.description == "Test package"
    assert len(manifest.dependencies) == 2
    assert "core" in manifest.dependencies
    assert manifest.dependencies["core"].version_constraint == "^1.0.0"
    assert len(manifest.dev_dependencies) == 1
    assert manifest.entry_point == "main.syn"
    assert manifest.compile_to_bytecode is True


def test_manifest_from_dict_detailed_deps():
    """Test parsing manifest with detailed dependency specs"""
    data = {
        "package": {"name": "my-package", "version": "1.0.0"},
        "dependencies": {
            "dep1": {"version": "^1.0.0", "source": "git"},
            "dep2": {"version": "*", "source": "path"},
        },
    }

    manifest = PackageManifest.from_dict(data)
    assert manifest.dependencies["dep1"].source == "git"
    assert manifest.dependencies["dep2"].source == "path"


def test_manifest_from_dict_missing_name():
    """Test parsing manifest without name"""
    data = {"package": {"version": "1.0.0"}}
    
    with pytest.raises(ValueError, match="name is required"):
        PackageManifest.from_dict(data)


def test_manifest_from_dict_missing_version():
    """Test parsing manifest without version"""
    data = {"package": {"name": "test-pkg"}}
    
    with pytest.raises(ValueError, match="version is required"):
        PackageManifest.from_dict(data)


def test_manifest_from_dict_invalid_name():
    """Test parsing manifest with invalid name"""
    data = {"package": {"name": "Invalid-Name!", "version": "1.0.0"}}
    
    with pytest.raises(ValueError, match="Invalid package name"):
        PackageManifest.from_dict(data)


def test_manifest_from_dict_invalid_version():
    """Test parsing manifest with invalid version"""
    data = {"package": {"name": "test-pkg", "version": "invalid"}}
    
    with pytest.raises(ValueError, match="Invalid version"):
        PackageManifest.from_dict(data)


def test_manifest_from_file():
    """Test loading manifest from file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("""[package]
name = "test-pkg"
version = "1.0.0"
description = "Test"

[dependencies]
core = "^1.0.0"
""")
        temp_path = Path(f.name)
    
    try:
        manifest = PackageManifest.from_file(temp_path)
        assert manifest.name == "test-pkg"
        assert manifest.version == "1.0.0"
        assert "core" in manifest.dependencies
    finally:
        temp_path.unlink(missing_ok=True)


def test_manifest_from_file_not_found():
    """Test loading manifest from non-existent file"""
    with pytest.raises(FileNotFoundError):
        PackageManifest.from_file(Path("/nonexistent/path.toml"))


def test_manifest_is_valid_package_name():
    """Test package name validation"""
    assert PackageManifest._is_valid_package_name("mypackage")
    assert PackageManifest._is_valid_package_name("my-package")
    assert PackageManifest._is_valid_package_name("my_package")
    assert PackageManifest._is_valid_package_name("mypackage123")
    
    assert not PackageManifest._is_valid_package_name("MyPackage")  # Uppercase
    assert not PackageManifest._is_valid_package_name("my package")  # Space
    assert not PackageManifest._is_valid_package_name("123package")  # Starts with number
    assert not PackageManifest._is_valid_package_name("my-package!")  # Special char


def test_manifest_is_valid_version():
    """Test version validation"""
    assert PackageManifest._is_valid_version("1.0.0")
    assert PackageManifest._is_valid_version("0.0.1")
    assert PackageManifest._is_valid_version("1.2.3-alpha")
    assert PackageManifest._is_valid_version("1.2.3+build.123")
    assert PackageManifest._is_valid_version("1.2.3-beta.1+build.456")
    
    assert not PackageManifest._is_valid_version("1.0")  # Missing patch
    assert not PackageManifest._is_valid_version("1")  # Missing minor and patch
    assert not PackageManifest._is_valid_version("v1.0.0")  # Has 'v' prefix
    assert not PackageManifest._is_valid_version("invalid")


def test_create_default_manifest():
    """Test default manifest generation"""
    content = create_default_manifest("my-pkg", "0.1.0")

    assert 'name = "my-pkg"' in content
    assert 'version = "0.1.0"' in content
    assert "[package]" in content
    assert "[dependencies]" in content
    assert "[dev-dependencies]" in content
    assert "[build]" in content


def test_manifest_to_dict():
    """Test converting manifest to dictionary"""
    manifest = PackageManifest(
        name="test-pkg",
        version="1.0.0",
        description="Test",
        dependencies={"dep1": Dependency("dep1", "^1.0.0")},
    )

    data = manifest.to_dict()

    assert data["package"]["name"] == "test-pkg"
    assert data["package"]["version"] == "1.0.0"
    assert "dep1" in data["dependencies"]
    assert data["dependencies"]["dep1"] == "^1.0.0"


def test_circular_dependency_detection():
    """Test self-dependency detection"""
    manifest = PackageManifest(
        name="my-package",
        version="1.0.0",
        dependencies={"my-package": Dependency("my-package", "1.0.0")},
    )

    errors = manifest.validate()
    assert len(errors) > 0
    assert any("cannot depend on itself" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
