"""
Syntari Package - Version and Metadata Information
"""

__version__ = "0.4.0"
__author__ = "DeuOS, LLC"
__email__ = "legal@deuos.io"
__license__ = "Proprietary"
__copyright__ = "Copyright 2025-2026 DeuOS, LLC"
__description__ = "AI-integrated, type-safe, functional-first programming language"
__url__ = "https://github.com/Adahandles/Syntari"

# Version info tuple
VERSION = (0, 4, 0)
VERSION_STRING = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"

# Build metadata
BUILD_DATE = "2026-01-26"
BUILD_STATUS = "stable"
PRODUCTION_READY = True

# Feature flags
FEATURES = {
    "bytecode_compiler": True,
    "vm_runtime": True,
    "debugger": True,
    "profiler": True,
    "lsp_server": True,
    "package_manager": True,
    "web_repl": True,
    "networking": True,
    "structured_logging": True,
    "error_handling": True,
}

# API compatibility
API_VERSION = "0.4"
MIN_PYTHON_VERSION = (3, 8)
MAX_PYTHON_VERSION = (3, 12)

def get_version():
    """Return the version string"""
    return __version__

def get_version_info():
    """Return detailed version information"""
    return {
        "version": __version__,
        "version_tuple": VERSION,
        "build_date": BUILD_DATE,
        "build_status": BUILD_STATUS,
        "production_ready": PRODUCTION_READY,
        "api_version": API_VERSION,
        "features": FEATURES,
    }

def print_version_info():
    """Print formatted version information"""
    info = get_version_info()
    print(f"Syntari v{info['version']}")
    print(f"Build: {info['build_date']} ({info['build_status']})")
    print(f"Production Ready: {'Yes' if info['production_ready'] else 'No'}")
    print(f"API Version: {info['api_version']}")
    print(f"\nEnabled Features:")
    for feature, enabled in info['features'].items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature.replace('_', ' ').title()}")

if __name__ == "__main__":
    print_version_info()
