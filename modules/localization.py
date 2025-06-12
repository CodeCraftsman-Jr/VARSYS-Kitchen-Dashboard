"""
Localization utilities for Kitchen Dashboard application.
This module provides internationalization (i18n) and localization (l10n) functionality.
"""
import os
import gettext
import locale
from pathlib import Path

from config import BASE_DIR

# Default language
DEFAULT_LANGUAGE = 'en'

# Available languages
AVAILABLE_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'hi': 'हिन्दी'
}

# Locales directory
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')


def get_system_language():
    """
    Get the system language code.
    
    Returns:
        str: Language code (e.g., 'en', 'es', 'hi')
    """
    try:
        # Get system locale
        language_code, _ = locale.getdefaultlocale()
        if language_code:
            # Extract language code (e.g., 'en_US' -> 'en')
            language = language_code.split('_')[0].lower()
            if language in AVAILABLE_LANGUAGES:
                return language
    except Exception:
        pass
    
    # Fall back to default language
    return DEFAULT_LANGUAGE


def setup_localization(language=None):
    """
    Set up localization for the application.
    
    Args:
        language (str, optional): Language code to use. If None, system language is used.
        
    Returns:
        gettext.GNUTranslations: Translation object
    """
    # If no language specified, use system language
    if language is None:
        language = get_system_language()
    
    # Ensure language is supported, otherwise fall back to default
    if language not in AVAILABLE_LANGUAGES:
        language = DEFAULT_LANGUAGE
    
    # Set up gettext
    try:
        locale_path = os.path.join(LOCALES_DIR, language, 'LC_MESSAGES', 'messages.mo')
        
        # Check if compiled .mo file exists, and if not, create it
        if not os.path.exists(locale_path):
            po_file = os.path.join(LOCALES_DIR, language, 'LC_MESSAGES', 'messages.po')
            if os.path.exists(po_file):
                import subprocess
                subprocess.call(['msgfmt', po_file, '-o', locale_path])
        
        # Create translation object
        translation = gettext.translation('messages', LOCALES_DIR, languages=[language])
        translation.install()
        return translation
    except Exception as e:
        print(f"Error setting up localization: {str(e)}")
        # Fall back to a simple pass-through function if translations fail
        return gettext.NullTranslations()


# Function to change language at runtime
def change_language(language):
    """
    Change the application language at runtime.
    
    Args:
        language (str): Language code to use
        
    Returns:
        bool: True if successful, False otherwise
    """
    if language in AVAILABLE_LANGUAGES:
        translation = setup_localization(language)
        return True
    return False


# Convenience function to get language names
def get_language_names():
    """
    Get a list of available languages with their names.
    
    Returns:
        list: List of tuples (language_code, language_name)
    """
    return [(code, name) for code, name in AVAILABLE_LANGUAGES.items()]


# Example usage
if __name__ == "__main__":
    # Set up localization
    translation = setup_localization()
    
    # Get the translation function
    _ = translation.gettext
    
    # Example translations
    print(_("Inventory"))
    print(_("Shopping List"))
    print(_("Settings"))
