from .config import LANG


def t(key: str) -> str:
    translated = {
        "en": {"tools": "Tools/Tests/Measurements"},
        "fr": {
            "reference": "référence",
            "theme": "thème",
            "results": "résultats",
            "highlights": "points importants",
            "criticisms": "critiques",
            "authors": "auteur·ices",
            "definitions": "définitions",
            "concepts": "concepts",
            "tools": "Outils/Tests/Mesures",
        },
    }[LANG].get(key.lower(), key.lower())

    if key[0].isupper():
        translated = translated[0].upper() + translated[1:]

    return translated
