"""
Basic tests for src/pkg/cli.py
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import argparse

from src.pkg.cli import cmd_init, cmd_list, cmd_search, cmd_cache


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = Path(tempfile.mkdtemp())
    original_cwd = Path.cwd()
    try:
        # Change to temp directory
        import os
        os.chdir(temp)
        yield temp
    finally:
        # Restore original directory
        import os
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
            {"name": "pkg2", "version": "2.0.0", "size_bytes": 2048}
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
        mock_cache.list_cached_packages.return_value = [
            {"name": "pkg1", "version": "1.0.0"}
        ]
        mock_cache.get_cache_size.return_value = 1024 * 1024
        mock_cache.format_size.return_value = "1.0 MB"
        MockCache.return_value = mock_cache
        
        result = cmd_cache(args)
        
        assert result == 0
