"""
VARSYS Solutions - Kitchen Dashboard
Version Management System

Company: VARSYS Solutions
Software: Kitchen Dashboard (First software in VARSYS ecosystem)
License: Proprietary - Free for limited testing period
"""

__version__ = "1.2.1"
__build__ = "20250617"
__company__ = "VARSYS Solutions"
__product__ = "Kitchen Dashboard"
__description__ = "Professional Kitchen Management System with Firebase Authentication & Cloud Sync"
__copyright__ = "© 2025 VARSYS Solutions. All rights reserved."
__website__ = "https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard"
__support_email__ = "support@varsys-solutions.com"

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 3
VERSION_BUILD = 20250617

# Release information
RELEASE_TYPE = "stable"  # alpha, beta, rc, stable
IS_BETA = False
IS_DEVELOPMENT = False

# Update configuration
UPDATE_CHECK_URL = "https://api.github.com/repos/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/releases/latest"
DOWNLOAD_BASE_URL = "https://github.com/CodeCraftsman-Jr/VARSYS-Kitchen-Dashboard/releases/download"

# Feature flags for ecosystem
FIREBASE_ENABLED = True  # Enabled for v1.1.1 with full cloud sync
SUBSCRIPTION_REQUIRED = True  # Enabled for subscription-based access
MULTI_USER_SUPPORT = True  # Enabled with Firebase authentication

# Compatibility information
MIN_PYTHON_VERSION = "3.8"
SUPPORTED_OS = ["Windows 10", "Windows 11"]
ARCHITECTURE = ["x64", "x86"]

def get_version_string():
    """Get formatted version string"""
    return f"{__version__}"

def get_full_version_string():
    """Get full version string with build"""
    return f"{__version__}.{__build__}"

def get_version_info():
    """Get complete version information"""
    return {
        "version": __version__,
        "build": __build__,
        "company": __company__,
        "product": __product__,
        "description": __description__,
        "copyright": __copyright__,
        "website": __website__,
        "support_email": __support_email__,
        "release_type": RELEASE_TYPE,
        "is_beta": IS_BETA,
        "is_development": IS_DEVELOPMENT,
        "firebase_enabled": FIREBASE_ENABLED,
        "subscription_required": SUBSCRIPTION_REQUIRED,
        "multi_user_support": MULTI_USER_SUPPORT
    }

def is_newer_version(remote_version):
    """Check if remote version is newer than current"""
    try:
        current = [int(x) for x in __version__.split('.')]
        remote = [int(x) for x in remote_version.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(current), len(remote))
        current.extend([0] * (max_len - len(current)))
        remote.extend([0] * (max_len - len(remote)))
        
        return remote > current
    except (ValueError, AttributeError):
        return False
