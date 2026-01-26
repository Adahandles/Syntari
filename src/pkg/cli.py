#!/usr/bin/env python3
"""
Syntari Package Manager CLI

Commands:
  syntari pkg init [name]          - Create a new package
  syntari pkg install [package]    - Install a package
  syntari pkg list                 - List installed packages
  syntari pkg search <query>       - Search for packages
  syntari pkg update               - Update all packages
  syntari pkg remove <package>     - Remove a package
  syntari pkg publish              - Publish package to registry
  syntari pkg cache --clear        - Clear package cache
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from src.pkg.manifest import PackageManifest, create_default_manifest
from src.pkg.resolver import DependencyResolver, print_dependency_tree
from src.pkg.cache import PackageCache
from src.pkg.registry import PackageRegistry


def cmd_init(args):
    """Initialize a new Syntari package"""
    name = args.name
    
    if not name:
        # Get name from current directory
        name = Path.cwd().name.lower().replace(' ', '-')
    
    manifest_path = Path('syntari.toml')
    
    if manifest_path.exists():
        print(f"Error: syntari.toml already exists", file=sys.stderr)
        return 1
    
    # Create manifest
    manifest_content = create_default_manifest(name, "0.1.0")
    manifest_path.write_text(manifest_content)
    
    print(f"✓ Created syntari.toml for package '{name}'")
    print(f"\nNext steps:")
    print(f"  1. Edit syntari.toml to add package details")
    print(f"  2. Add your code (.syn files)")
    print(f"  3. Run 'syntari pkg install' to install dependencies")
    
    return 0


def cmd_install(args):
    """Install package dependencies"""
    package_name = args.package
    cache = PackageCache()
    registry = PackageRegistry()
    
    if package_name:
        # Install specific package
        print(f"Installing {package_name}...")
        
        # Parse version constraint if provided
        if '@' in package_name:
            name, version = package_name.split('@', 1)
        else:
            name = package_name
            # Get latest version
            versions = registry.get_available_versions(name)
            if not versions:
                print(f"Error: Package '{name}' not found", file=sys.stderr)
                return 1
            version = versions[0]
        
        # Check if already cached
        if cache.is_cached(name, version):
            print(f"✓ {name}@{version} already installed")
            return 0
        
        # Download from registry
        try:
            temp_dir = cache.cache_dir / 'temp'
            temp_dir.mkdir(exist_ok=True)
            
            pkg_path = registry.download_package(name, version, temp_dir)
            cache.add_package(name, version, pkg_path)
            
            print(f"✓ Installed {name}@{version}")
            return 0
        except Exception as e:
            print(f"Error installing {name}@{version}: {e}", file=sys.stderr)
            return 1
    
    else:
        # Install from syntari.toml
        manifest_path = Path('syntari.toml')
        
        if not manifest_path.exists():
            print("Error: syntari.toml not found", file=sys.stderr)
            print("Run 'syntari pkg init' to create a new package", file=sys.stderr)
            return 1
        
        try:
            manifest = PackageManifest.from_file(manifest_path)
            print(f"Installing dependencies for {manifest.name}...")
            
            # Resolve dependencies
            resolver = DependencyResolver(registry)
            resolved = resolver.resolve(manifest, include_dev=args.dev)
            
            if not resolved:
                print("No dependencies to install")
                return 0
            
            # Show dependency tree
            print("\nDependency tree:")
            tree = resolver.get_dependency_tree(manifest)
            print_dependency_tree(tree)
            print()
            
            # Install each package
            installed = 0
            for pkg in resolved:
                if cache.is_cached(pkg.name, pkg.version):
                    print(f"  ✓ {pkg.name}@{pkg.version} (cached)")
                else:
                    print(f"  → Installing {pkg.name}@{pkg.version}...", end=" ")
                    try:
                        temp_dir = cache.cache_dir / 'temp'
                        temp_dir.mkdir(exist_ok=True)
                        
                        pkg_path = registry.download_package(pkg.name, pkg.version, temp_dir)
                        cache.add_package(pkg.name, pkg.version, pkg_path)
                        print("✓")
                        installed += 1
                    except Exception as e:
                        print(f"✗ ({e})")
            
            print(f"\n✓ Installed {installed} package(s)")
            return 0
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


def cmd_list(args):
    """List installed packages"""
    cache = PackageCache()
    packages = cache.list_cached_packages()
    
    if not packages:
        print("No packages installed")
        return 0
    
    print(f"Installed packages ({len(packages)}):\n")
    
    for pkg in packages:
        size = cache.format_size(pkg['size_bytes'])
        print(f"  {pkg['name']}@{pkg['version']} ({size})")
        if args.verbose:
            print(f"    Cached: {pkg['cached_at']}")
            print(f"    Checksum: {pkg['checksum'][:16]}...")
    
    if not args.verbose:
        total_size = cache.get_cache_size()
        print(f"\nTotal cache size: {cache.format_size(total_size)}")
    
    return 0


def cmd_search(args):
    """Search for packages in registry"""
    query = args.query
    registry = PackageRegistry()
    
    print(f"Searching for '{query}'...\n")
    
    results = registry.search(query)
    
    if not results:
        print("No packages found")
        return 0
    
    print(f"Found {len(results)} package(s):\n")
    
    for pkg in results:
        print(f"  {pkg.name}@{pkg.version}")
        print(f"    {pkg.description}")
        print(f"    By: {pkg.author}")
        print()
    
    return 0


def cmd_remove(args):
    """Remove an installed package"""
    package = args.package
    cache = PackageCache()
    
    # Parse version if provided
    if '@' in package:
        name, version = package.split('@', 1)
    else:
        # Find all versions and remove them
        packages = cache.list_cached_packages()
        versions_to_remove = [
            p['version'] for p in packages if p['name'] == package
        ]
        
        if not versions_to_remove:
            print(f"Package '{package}' not installed")
            return 1
        
        # Remove all versions
        for version in versions_to_remove:
            if cache.remove_package(package, version):
                print(f"✓ Removed {package}@{version}")
        
        return 0
    
    # Remove specific version
    if cache.remove_package(name, version):
        print(f"✓ Removed {name}@{version}")
        return 0
    else:
        print(f"Package '{name}@{version}' not installed")
        return 1


def cmd_cache(args):
    """Manage package cache"""
    cache = PackageCache()
    
    if args.clear:
        count = cache.clear_cache()
        print(f"✓ Cleared cache ({count} package(s) removed)")
        return 0
    
    # Show cache info
    packages = cache.list_cached_packages()
    total_size = cache.get_cache_size()
    
    print(f"Cache location: {cache.cache_dir}")
    print(f"Packages: {len(packages)}")
    print(f"Total size: {cache.format_size(total_size)}")
    
    return 0


def cmd_publish(args):
    """Publish package to registry"""
    manifest_path = Path('syntari.toml')
    
    if not manifest_path.exists():
        print("Error: syntari.toml not found", file=sys.stderr)
        return 1
    
    try:
        manifest = PackageManifest.from_file(manifest_path)
        
        # Validate manifest
        errors = manifest.validate()
        if errors:
            print("Error: Invalid manifest:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        
        registry = PackageRegistry()
        
        print(f"Publishing {manifest.name}@{manifest.version}...")
        
        # TODO: Get API key from config or environment
        api_key = "stub-api-key"
        
        if registry.publish_package(manifest_path, Path.cwd(), api_key):
            print(f"✓ Published {manifest.name}@{manifest.version}")
            return 0
        else:
            print("Error: Publishing failed", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for package manager CLI"""
    parser = argparse.ArgumentParser(
        prog='syntari pkg',
        description='Syntari Package Manager'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Create a new package')
    init_parser.add_argument('name', nargs='?', help='Package name')
    
    # install command
    install_parser = subparsers.add_parser('install', help='Install dependencies')
    install_parser.add_argument('package', nargs='?', help='Package to install (optional)')
    install_parser.add_argument('--dev', action='store_true', help='Include dev dependencies')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List installed packages')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed info')
    
    # search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    
    # remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a package')
    remove_parser.add_argument('package', help='Package to remove')
    
    # cache command
    cache_parser = subparsers.add_parser('cache', help='Manage package cache')
    cache_parser.add_argument('--clear', action='store_true', help='Clear cache')
    
    # publish command
    publish_parser = subparsers.add_parser('publish', help='Publish package to registry')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    commands = {
        'init': cmd_init,
        'install': cmd_install,
        'list': cmd_list,
        'search': cmd_search,
        'remove': cmd_remove,
        'cache': cmd_cache,
        'publish': cmd_publish,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
