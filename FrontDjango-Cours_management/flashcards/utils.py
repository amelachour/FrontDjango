import requests

def fetch_content_by_theme(theme):
    """
    Récupère le contenu lié au thème spécifié en utilisant l'API Wikipedia.

    Args:
        theme (str): Le thème à rechercher.

    Returns:
        str: Le résumé récupéré de Wikipedia ou None si non trouvé.
    """
    try:
        # Remplacer les espaces par des underscores pour l'URL
        theme_formatted = theme.replace(' ', '_')
        response = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{theme_formatted}',
            headers={'User-Agent': 'FlashcardGenerator/1.0'}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('extract', '')
        else:
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération du contenu pour le thème '{theme}': {e}")
        return None
