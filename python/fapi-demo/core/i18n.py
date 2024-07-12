from contextvars import ContextVar
from typing import Dict, Union, Tuple, Optional, List

# Define types for translations
TranslationEntry = Union[str, Tuple[str, str]]
TranslationDict = Dict[str, Dict[str, TranslationEntry]]

# Initialize an empty translation dictionary
TRANSLATIONS: TranslationDict = {}

# Use ContextVar to store the current language
current_lang = ContextVar('current_lang', default='en')
fallback_lang = 'en'

def add_translation(entries: List[Tuple[str, Dict[str, TranslationEntry]]]):
    """
    Add or update translations for multiple keys at once
    
    Args:
        entries: A list of tuples, each containing a key and its translations
    """
    for key, translations in entries:
        for lang, trans in translations.items():
            if lang not in TRANSLATIONS:
                TRANSLATIONS[lang] = {}
            TRANSLATIONS[lang][key] = trans

def add_language_translations(lang: str, translations: Dict[str, TranslationEntry]):
    """
    Add or update translations for a single language
    
    Args:
        lang: The language code
        translations: A dictionary of translations for the specified language
    """
    if lang not in TRANSLATIONS:
        TRANSLATIONS[lang] = {}
    TRANSLATIONS[lang].update(translations)

def merge_translations(*translation_dicts: TranslationDict):
    """
    Merge multiple translation dictionaries
    
    Args:
        translation_dicts: TranslationDict objects to be merged
    """
    for d in translation_dicts:
        for lang, trans in d.items():
            if lang not in TRANSLATIONS:
                TRANSLATIONS[lang] = {}
            TRANSLATIONS[lang].update(trans)

def set_language(lang: str):
    """
    Set the current language
    
    Args:
        lang: The language code to set as current
    """
    if lang in TRANSLATIONS:
        current_lang.set(lang)
    else:
        raise ValueError(f"Unsupported language: {lang}")

def get_translation(key: str, lang: Optional[str] = None) -> TranslationEntry:
    """
    Get the translation for a key, with language fallback
    
    Args:
        key: The key to translate
        lang: Optional language override
    
    Returns:
        The translated string or the original key if no translation is found
    """
    lang = lang or current_lang.get()
    
    # Try to get the translation in the specified language
    translation = TRANSLATIONS.get(lang, {}).get(key)
    
    # If not found, try the fallback language
    if translation is None and lang != fallback_lang:
        translation = TRANSLATIONS.get(fallback_lang, {}).get(key)
    
    # If still not found, return the original key
    return translation if translation is not None else key

def _(key: str, lang: Optional[str] = None) -> str:
    """
    Translate a singular form
    
    Args:
        key: The key to translate
        lang: Optional language override
    
    Returns:
        The translated string
    """
    translation = get_translation(key, lang)
    if isinstance(translation, tuple):
        return translation[0]
    return translation

def _N(singular: str, plural: str, count: int, lang: Optional[str] = None) -> str:
    """
    Translate a plural form
    
    Args:
        singular: The singular form key
        plural: The plural form key
        count: The count to determine singular or plural
        lang: Optional language override
    
    Returns:
        The translated string with count formatted
    """
    translation = get_translation(singular, lang)
    if isinstance(translation, tuple):
        return translation[0 if count == 1 else 1].format(count=count)
    return translation.format(count=count)

# Usage example
if __name__ == "__main__":

    # Add en translations
    add_language_translations('en', {
        'find {count} cat': ('find {count} cat', 'find {count} cats'),
        'goodbye': 'goodbye~~',
    })    
    # Add translations in batch
    add_translation([
        ('hello', {'en': 'hello', 'zh': '你好'}),
        ('find {count} cat', {
            'en': ('find {count} cat', 'find {count} cats'),
            'zh': ('找到{count}只猫', '找到{count}只猫'),
            }),
    ])

    print(_('hello'))  # Output: hello
    print(_N('find {count} cat', 'find {count} cats', 1))  # Output: find 1 cat
    print(_N('find {count} cat', 'find {count} cats', 3))  # Output: find 3 cats

    set_language('zh')
    print(_('hello'))  # Output: 你好
    print(_('goodbye'))  # Output: goodbye~~
    print(_N('find {count} cat', 'find {count} cats', 1))  # Output: 找到1只猫
    print(_N('find {count} cat', 'find {count} cats', 3))  # Output: 找到3只猫

    # Use specified language
    print(_('hello', lang='en'))  # Output: hello
    
    # Use undefined translation, will fallback to original string
    print(_('undefined_key'))  # Output: undefined_key