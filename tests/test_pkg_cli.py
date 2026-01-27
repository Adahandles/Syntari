"""
Comprehensive tests for src/pkg/cli.py
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import sys
import argparse

from src.pkg.cli import (
    cmd_init,
    cmd_list,
    cmd_search,
    cmd_cache,
    cmd_install,
    cmd_remove,
    cmd_publish,
    main,
)
from src.pkg.manifest import PackageManifest, Dependency


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = Path(tempfile.mkdtemp())
    original_cwd = Path.cwd()
    try:
        # Change to temp directory
        os.chdir(temp)
        yield temp
    finally:
        # Restore original directory
        os.chdir(original_cwd)
        # Cleanup
        if temp.exists():
            shutil.rmtree(temp)


def test_cmd_init_with_name(temp_dir):
    """Test init command with explicit name"""
    args = argparse.Namespace(name="my-package")

    result = cmd_init(args)

    assert result == 0
    manifest = Path("syntari.toml")
    assert manifest.exists()
    content = manifest.read_text()
    assert "my-package" in content


def test_cmd_init_without_name(temp_dir):
    """Test init command uses directory name"""
    args = argparse.Namespace(name=None)

    result = cmd_init(args)

    assert result == 0
    manifest = Path("syntari.toml")
    assert manifest.exists()


def test_cmd_init_already_exists(temp_dir):
    """Test init command fails if manifest exists"""
    # Create manifest first
    Path("syntari.toml").write_text("[package]")

    args = argparse.Namespace(name="test")

    with patch("sys.stderr"):
        result = cmd_init(args)

    assert result == 1


def test_cmd_list_empty():
    """Test list command with no packages"""
    args = argparse.Namespace()

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = []
        MockCache.return_value = mock_cache

        result = cmd_list(args)

        assert result == 0


def test_cmd_list_with_packages():
    """Test list command with cached packages"""
    args = argparse.Namespace(verbose=False)

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = [
            {"name": "pkg1", "version": "1.0.0", "size_bytes": 1024},
            {"name": "pkg2", "version": "2.0.0", "size_bytes": 2048},
        ]
        mock_cache.format_size.return_value = "1 KB"
        MockCache.return_value = mock_cache

        result = cmd_list(args)

        assert result == 0


def test_cmd_search_no_results():
    """Test search command with no results"""
    args = argparse.Namespace(query="nonexistent")

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry:
        mock_registry = MagicMock()
        mock_registry.search.return_value = []
        MockRegistry.return_value = mock_registry

        result = cmd_search(args)

        assert result == 0


def test_cmd_search_with_results():
    """Test search command with results"""
    args = argparse.Namespace(query="test")

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry:
        mock_registry = MagicMock()
        mock_pkg = MagicMock()
        mock_pkg.name = "test-pkg"
        mock_pkg.version = "1.0.0"
        mock_pkg.description = "A test package"
        mock_pkg.author = "Test Author"
        mock_registry.search.return_value = [mock_pkg]
        MockRegistry.return_value = mock_registry

        result = cmd_search(args)

        assert result == 0


def test_cmd_cache_clear():
    """Test cache clear command"""
    args = argparse.Namespace(clear=True)

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.clear_cache.return_value = 5
        MockCache.return_value = mock_cache

        result = cmd_cache(args)

        assert result == 0
        mock_cache.clear_cache.assert_called_once()


def test_cmd_cache_show_info():
    """Test cache info display"""
    args = argparse.Namespace(clear=False)

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = [{"name": "pkg1", "version": "1.0.0"}]
        mock_cache.get_cache_size.return_value = 1024 * 1024
        mock_cache.format_size.return_value = "1.0 MB"
        MockCache.return_value = mock_cache

        result = cmd_cache(args)

        assert result == 0


def test_cmd_list_verbose():
    """Test list command with verbose output"""
    args = argparse.Namespace(verbose=True)

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = [
            {
                "name": "pkg1",
                "version": "1.0.0",
                "size_bytes": 1024,
                "cached_at": "2024-01-01",
                "checksum": "abc123def456789",
            }
        ]
        mock_cache.format_size.return_value = "1 KB"
        MockCache.return_value = mock_cache

        result = cmd_list(args)

        assert result == 0


def test_cmd_install_specific_package_with_version():
    """Test installing specific package with version"""
    args = argparse.Namespace(package="test-pkg@1.2.3", dev=False)

    with patch("src.pkg.cli.PackageCache") as MockCache, patch(
        "src.pkg.cli.PackageRegistry"
    ) as MockRegistry, patch("builtins.print"):
        mock_cache = MagicMock()
        mock_cache.is_cached.return_value = False
        mock_cache.cache_dir = MagicMock()
        mock_cache.cache_dir.__truediv__ = lambda self, x: Path("/tmp/cache") / x  # nosec B108
        MockCache.return_value = mock_cache

        mock_registry = MagicMock()
        mock_registry.download_package.return_value = Path("/tmp/pkg.tar.gz")  # nosec B108
        MockRegistry.return_value = mock_registry

        with patch("pathlib.Path.mkdir"):
            result = cmd_install(args)

        assert result == 0
        mock_cache.add_package.assert_called_once()


def test_cmd_install_specific_package_already_cached():
    """Test installing package that's already cached"""
    args = argparse.Namespace(package="test-pkg@1.0.0", dev=False)

    with patch("src.pkg.cli.PackageCache") as MockCache, patch(
        "src.pkg.cli.PackageRegistry"
    ) as MockRegistry:
        mock_cache = MagicMock()
        mock_cache.is_cached.return_value = True
        MockCache.return_value = mock_cache

        result = cmd_install(args)

        assert result == 0


def test_cmd_install_specific_package_not_found():
    """Test installing package that doesn't exist"""
    args = argparse.Namespace(package="nonexistent-pkg", dev=False)

    with patch("src.pkg.cli.PackageCache") as MockCache, patch(
        "src.pkg.cli.PackageRegistry"
    ) as MockRegistry, patch("sys.stderr"):
        mock_registry = MagicMock()
        mock_registry.get_available_versions.return_value = []
        MockRegistry.return_value = mock_registry

        result = cmd_install(args)

        assert result == 1


def test_cmd_install_specific_package_download_error():
    """Test install fails on download error"""
    args = argparse.Namespace(package="test-pkg", dev=False)

    with patch("src.pkg.cli.PackageCache") as MockCache, patch(
        "src.pkg.cli.PackageRegistry"
    ) as MockRegistry, patch("sys.stderr"):
        mock_cache = MagicMock()
        mock_cache.is_cached.return_value = False
        mock_cache.cache_dir = Path("/tmp/cache")  # nosec B108
        MockCache.return_value = mock_cache

        mock_registry = MagicMock()
        mock_registry.get_available_versions.return_value = ["1.0.0"]
        mock_registry.download_package.side_effect = Exception("Download failed")
        MockRegistry.return_value = mock_registry

        result = cmd_install(args)

        assert result == 1


def test_cmd_install_from_manifest_no_file(temp_dir):
    """Test install from manifest when file doesn't exist"""
    args = argparse.Namespace(package=None, dev=False)

    with patch("sys.stderr"):
        result = cmd_install(args)

        assert result == 1


def test_cmd_install_from_manifest_success(temp_dir):
    """Test successful install from manifest"""
    # Create manifest
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"

[dependencies]
dep1 = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace(package=None, dev=False)

    with patch("src.pkg.cli.PackageCache") as MockCache, patch(
        "src.pkg.cli.PackageRegistry"
    ) as MockRegistry, patch("src.pkg.cli.DependencyResolver") as MockResolver:
        mock_cache = MagicMock()
        mock_cache.is_cached.return_value = True
        MockCache.return_value = mock_cache

        mock_resolver = MagicMock()
        mock_pkg = MagicMock()
        mock_pkg.name = "dep1"
        mock_pkg.version = "1.0.0"
        mock_resolver.resolve.return_value = [mock_pkg]
        mock_resolver.get_dependency_tree.return_value = {}
        MockResolver.return_value = mock_resolver

        result = cmd_install(args)

        assert result == 0


def test_cmd_install_from_manifest_no_dependencies(temp_dir):
    """Test install from manifest with no dependencies"""
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace(package=None, dev=False)

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry, patch(
        "src.pkg.cli.DependencyResolver"
    ) as MockResolver:
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = []
        MockResolver.return_value = mock_resolver

        result = cmd_install(args)

        assert result == 0


def test_cmd_install_from_manifest_error(temp_dir):
    """Test install from manifest with error"""
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace(package=None, dev=False)

    with patch("src.pkg.cli.DependencyResolver") as MockResolver, patch("sys.stderr"):
        MockResolver.side_effect = Exception("Resolution failed")

        result = cmd_install(args)

        assert result == 1


def test_cmd_remove_specific_version():
    """Test removing specific package version"""
    args = argparse.Namespace(package="test-pkg@1.0.0")

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.remove_package.return_value = True
        MockCache.return_value = mock_cache

        result = cmd_remove(args)

        assert result == 0
        mock_cache.remove_package.assert_called_once_with("test-pkg", "1.0.0")


def test_cmd_remove_all_versions():
    """Test removing all versions of a package"""
    args = argparse.Namespace(package="test-pkg")

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = [
            {"name": "test-pkg", "version": "1.0.0"},
            {"name": "test-pkg", "version": "2.0.0"},
        ]
        mock_cache.remove_package.return_value = True
        MockCache.return_value = mock_cache

        result = cmd_remove(args)

        assert result == 0
        assert mock_cache.remove_package.call_count == 2


def test_cmd_remove_not_installed():
    """Test removing package that's not installed"""
    args = argparse.Namespace(package="nonexistent-pkg")

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.list_cached_packages.return_value = []
        MockCache.return_value = mock_cache

        result = cmd_remove(args)

        assert result == 1


def test_cmd_remove_version_not_installed():
    """Test removing specific version that's not installed"""
    args = argparse.Namespace(package="test-pkg@1.0.0")

    with patch("src.pkg.cli.PackageCache") as MockCache:
        mock_cache = MagicMock()
        mock_cache.remove_package.return_value = False
        MockCache.return_value = mock_cache

        result = cmd_remove(args)

        assert result == 1


def test_cmd_publish_no_manifest(temp_dir):
    """Test publish without manifest"""
    args = argparse.Namespace()

    with patch("sys.stderr"):
        result = cmd_publish(args)

        assert result == 1


def test_cmd_publish_invalid_manifest(temp_dir):
    """Test publish with invalid manifest"""
    manifest_content = """[package]
name = "Invalid-Name-123"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace()

    with patch("sys.stderr"):
        result = cmd_publish(args)

        assert result == 1


def test_cmd_publish_success(temp_dir):
    """Test successful publish"""
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace()

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry:
        mock_registry = MagicMock()
        mock_registry.publish_package.return_value = True
        MockRegistry.return_value = mock_registry

        result = cmd_publish(args)

        assert result == 0


def test_cmd_publish_failed(temp_dir):
    """Test publish failure"""
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace()

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry, patch("sys.stderr"):
        mock_registry = MagicMock()
        mock_registry.publish_package.return_value = False
        MockRegistry.return_value = mock_registry

        result = cmd_publish(args)

        assert result == 1


def test_cmd_publish_exception(temp_dir):
    """Test publish with exception"""
    manifest_content = """[package]
name = "test-pkg"
version = "1.0.0"
"""
    Path("syntari.toml").write_text(manifest_content)

    args = argparse.Namespace()

    with patch("src.pkg.cli.PackageRegistry") as MockRegistry, patch("sys.stderr"):
        MockRegistry.side_effect = Exception("Registry error")

        result = cmd_publish(args)

        assert result == 1


def test_main_no_command():
    """Test main with no command"""
    with patch("sys.argv", ["syntari"]):
        with patch("argparse.ArgumentParser.print_help"):
            result = main()
            assert result == 1
