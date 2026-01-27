"""
Tests for src/pkg/registry.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.pkg.registry import PackageRegistry, RegistryPackage


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def registry():
    """Create a registry instance with test data"""
    reg = PackageRegistry("https://test.registry.dev")
    
    # Add some test packages
    pkg1 = RegistryPackage(
        name="test-pkg",
        version="1.0.0",
        description="Test package",
        author="Test Author",
        download_url="https://test.dev/pkg-1.0.0.tar.gz",
        checksum="abc123",
        dependencies={}
    )
    
    pkg2 = RegistryPackage(
        name="test-pkg",
        version="1.1.0",
        description="Test package v1.1",
        author="Test Author",
        download_url="https://test.dev/pkg-1.1.0.tar.gz",
        checksum="def456",
        dependencies={}
    )
    
    pkg3 = RegistryPackage(
        name="another-pkg",
        version="2.0.0",
        description="Another test package",
        author="Another Author",
        download_url="https://test.dev/another-2.0.0.tar.gz",
        checksum="ghi789",
        dependencies={"test-pkg": "^1.0.0"}
    )
    
    reg.add_local_package(pkg1)
    reg.add_local_package(pkg2)
    reg.add_local_package(pkg3)
    
    return reg


def test_registry_initialization():
    """Test registry initialization"""
    reg = PackageRegistry()
    assert reg.registry_url == "https://registry.syntari.dev"
    assert reg.local_index == {}


def test_registry_custom_url():
    """Test registry with custom URL"""
    reg = PackageRegistry("https://custom.registry.com")
    assert reg.registry_url == "https://custom.registry.com"


def test_add_local_package():
    """Test adding a package to local index"""
    reg = PackageRegistry()
    pkg = RegistryPackage(
        name="test",
        version="1.0.0",
        description="Test",
        author="Author",
        download_url="https://test.dev/test.tar.gz",
        checksum="abc",
        dependencies={}
    )
    
    reg.add_local_package(pkg)
    assert "test" in reg.local_index
    assert "1.0.0" in reg.local_index["test"]
    assert reg.local_index["test"]["1.0.0"] == pkg


def test_search_package(registry):
    """Test searching for packages"""
    results = registry.search("test")
    assert len(results) == 1
    assert results[0].name == "test-pkg"
    # Should return latest version
    assert results[0].version == "1.1.0"


def test_search_package_case_insensitive(registry):
    """Test search is case insensitive"""
    results = registry.search("TEST")
    assert len(results) == 1
    assert results[0].name == "test-pkg"


def test_search_package_no_results(registry):
    """Test search with no matches"""
    results = registry.search("nonexistent")
    assert len(results) == 0


def test_search_multiple_packages(registry):
    """Test search returns multiple packages"""
    results = registry.search("pkg")
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"test-pkg", "another-pkg"}


def test_get_package_info(registry):
    """Test getting package info"""
    pkg = registry.get_package_info("test-pkg", "1.0.0")
    assert pkg is not None
    assert pkg.name == "test-pkg"
    assert pkg.version == "1.0.0"
    assert pkg.description == "Test package"


def test_get_package_info_not_found(registry):
    """Test getting info for non-existent package"""
    pkg = registry.get_package_info("nonexistent", "1.0.0")
    assert pkg is None


def test_get_package_info_wrong_version(registry):
    """Test getting info with wrong version"""
    pkg = registry.get_package_info("test-pkg", "9.9.9")
    assert pkg is None


def test_get_available_versions(registry):
    """Test getting available versions"""
    versions = registry.get_available_versions("test-pkg")
    assert len(versions) == 2
    # Should be sorted descending
    assert versions[0] == "1.1.0"
    assert versions[1] == "1.0.0"


def test_get_available_versions_not_found(registry):
    """Test getting versions for non-existent package"""
    versions = registry.get_available_versions("nonexistent")
    assert len(versions) == 0


def test_get_available_versions_sorting(registry):
    """Test version sorting"""
    reg = PackageRegistry()
    
    for version in ["1.0.0", "1.10.0", "1.2.0", "2.0.0", "1.0.10"]:
        pkg = RegistryPackage(
            name="sorttest",
            version=version,
            description="Test",
            author="Author",
            download_url="https://test.dev",
            checksum="abc",
            dependencies={}
        )
        reg.add_local_package(pkg)
    
    versions = reg.get_available_versions("sorttest")
    assert versions == ["2.0.0", "1.10.0", "1.2.0", "1.0.10", "1.0.0"]


def test_download_package(registry, temp_dir):
    """Test downloading a package"""
    pkg_path = registry.download_package("test-pkg", "1.0.0", temp_dir)
    
    assert pkg_path.exists()
    assert pkg_path.is_dir()
    assert pkg_path.name == "test-pkg-1.0.0"
    
    # Check manifest was created
    manifest = pkg_path / "syntari.toml"
    assert manifest.exists()
    content = manifest.read_text()
    assert "test-pkg" in content
    assert "1.0.0" in content


def test_download_package_not_found(registry, temp_dir):
    """Test downloading non-existent package"""
    with pytest.raises(ValueError) as exc_info:
        registry.download_package("nonexistent", "1.0.0", temp_dir)
    assert "not found in registry" in str(exc_info.value)


def test_download_package_creates_directory(registry, temp_dir):
    """Test download creates necessary directories"""
    dest = temp_dir / "nested" / "path"
    pkg_path = registry.download_package("test-pkg", "1.0.0", dest)
    
    assert pkg_path.exists()
    assert pkg_path.parent == dest


def test_publish_package(registry, temp_dir):
    """Test publishing a package"""
    manifest_path = temp_dir / "syntari.toml"
    manifest_path.write_text("[package]\nname = 'test'\nversion = '1.0.0'")
    
    package_dir = temp_dir / "src"
    package_dir.mkdir()
    
    result = registry.publish_package(manifest_path, package_dir, "fake-api-key")
    assert result is True


def test_registry_package_dataclass():
    """Test RegistryPackage dataclass"""
    pkg = RegistryPackage(
        name="test",
        version="1.0.0",
        description="A test package",
        author="Test Author",
        download_url="https://example.com/test.tar.gz",
        checksum="abc123def456",
        dependencies={"dep1": "^1.0.0", "dep2": "~2.0.0"}
    )
    
    assert pkg.name == "test"
    assert pkg.version == "1.0.0"
    assert pkg.description == "A test package"
    assert pkg.author == "Test Author"
    assert pkg.download_url == "https://example.com/test.tar.gz"
    assert pkg.checksum == "abc123def456"
    assert len(pkg.dependencies) == 2
    assert pkg.dependencies["dep1"] == "^1.0.0"
