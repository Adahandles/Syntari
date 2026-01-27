"""Tests for package cache"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.pkg.cache import PackageCache


@pytest.fixture
def temp_cache():
    """Create a temporary cache directory"""
    temp_dir = Path(tempfile.mkdtemp())
    cache = PackageCache(temp_dir)
    yield cache
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_package():
    """Create a sample package directory"""
    temp_dir = Path(tempfile.mkdtemp())

    # Create some files
    (temp_dir / "main.syn").write_text('print("Hello")')
    (temp_dir / "lib").mkdir()
    (temp_dir / "lib" / "utils.syn").write_text("fn helper() {}")

    yield temp_dir

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def test_cache_initialization(temp_cache):
    """Test cache directory creation"""
    assert temp_cache.cache_dir.exists()
    assert temp_cache.packages_dir.exists()
    assert temp_cache.metadata_dir.exists()


def test_add_package(temp_cache, sample_package):
    """Test adding a package to cache"""
    pkg_path = temp_cache.add_package("test-pkg", "1.0.0", sample_package)

    assert pkg_path.exists()
    assert (pkg_path / "main.syn").exists()
    assert (pkg_path / "lib" / "utils.syn").exists()

    # Check metadata was created
    metadata = temp_cache.get_metadata("test-pkg", "1.0.0")
    assert metadata is not None
    assert metadata["name"] == "test-pkg"
    assert metadata["version"] == "1.0.0"
    assert "checksum" in metadata


def test_is_cached(temp_cache, sample_package):
    """Test checking if package is cached"""
    assert not temp_cache.is_cached("test-pkg", "1.0.0")

    temp_cache.add_package("test-pkg", "1.0.0", sample_package)

    assert temp_cache.is_cached("test-pkg", "1.0.0")
    assert not temp_cache.is_cached("test-pkg", "2.0.0")


def test_remove_package(temp_cache, sample_package):
    """Test removing a package from cache"""
    temp_cache.add_package("test-pkg", "1.0.0", sample_package)
    assert temp_cache.is_cached("test-pkg", "1.0.0")

    removed = temp_cache.remove_package("test-pkg", "1.0.0")
    assert removed is True
    assert not temp_cache.is_cached("test-pkg", "1.0.0")

    # Try removing non-existent package
    removed = temp_cache.remove_package("test-pkg", "1.0.0")
    assert removed is False


def test_list_cached_packages(temp_cache, sample_package):
    """Test listing cached packages"""
    temp_cache.add_package("pkg1", "1.0.0", sample_package)
    temp_cache.add_package("pkg2", "2.0.0", sample_package)

    packages = temp_cache.list_cached_packages()

    assert len(packages) == 2
    names = {p["name"] for p in packages}
    assert "pkg1" in names
    assert "pkg2" in names


def test_clear_cache(temp_cache, sample_package):
    """Test clearing all cached packages"""
    temp_cache.add_package("pkg1", "1.0.0", sample_package)
    temp_cache.add_package("pkg2", "2.0.0", sample_package)

    count = temp_cache.clear_cache()

    assert count == 2
    assert len(temp_cache.list_cached_packages()) == 0


def test_cache_size(temp_cache, sample_package):
    """Test calculating cache size"""
    temp_cache.add_package("test-pkg", "1.0.0", sample_package)

    size = temp_cache.get_cache_size()
    assert size > 0

    # Format size as human-readable
    formatted = temp_cache.format_size(size)
    assert "B" in formatted or "KB" in formatted


def test_checksum_verification(temp_cache, sample_package):
    """Test checksum computation and verification"""
    # Add package and get checksum
    temp_cache.add_package("test-pkg", "1.0.0", sample_package)
    metadata = temp_cache.get_metadata("test-pkg", "1.0.0")
    original_checksum = metadata["checksum"]

    # Verify checksum is consistent
    computed = temp_cache._compute_checksum(temp_cache.get_package_path("test-pkg", "1.0.0"))
    assert computed == original_checksum

    # Try adding with wrong checksum
    with pytest.raises(ValueError, match="Checksum mismatch"):
        temp_cache.add_package(
            "test-pkg", "2.0.0", sample_package, checksum="wrong_checksum_value_here"
        )


def test_add_package_replaces_existing(temp_cache, sample_package):
    """Test that adding a package replaces existing one"""
    # Add package first time
    temp_cache.add_package("test-pkg", "1.0.0", sample_package)
    assert temp_cache.is_cached("test-pkg", "1.0.0")

    # Add again with same version (should replace)
    temp_cache.add_package("test-pkg", "1.0.0", sample_package)
    assert temp_cache.is_cached("test-pkg", "1.0.0")


def test_get_metadata_nonexistent(temp_cache):
    """Test getting metadata for non-existent package"""
    metadata = temp_cache.get_metadata("nonexistent", "1.0.0")
    assert metadata is None


def test_format_size_large(temp_cache):
    """Test formatting very large sizes"""
    # Test TB size
    size_tb = 5 * 1024 * 1024 * 1024 * 1024  # 5 TB
    formatted = temp_cache.format_size(size_tb)
    assert "TB" in formatted

    # Test GB size
    size_gb = 2.5 * 1024 * 1024 * 1024
    formatted = temp_cache.format_size(size_gb)
    assert "GB" in formatted

    # Test MB size
    size_mb = 100 * 1024 * 1024
    formatted = temp_cache.format_size(size_mb)
    assert "MB" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
