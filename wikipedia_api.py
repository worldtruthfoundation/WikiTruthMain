import requests
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
import os

class WikipediaAPI:
    """Handles all Wikipedia API interactions"""
    
    def __init__(self):
        self.base_url = "https://{lang}.wikipedia.org/api/rest_v1"
        self.api_url = "https://{lang}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikiTruth/1.0 (https://wikitruth.app; contact@wikitruth.app)'
        })
    
    def get_supported_languages(self):
        """Get list of supported Wikipedia languages"""
        # Most common Wikipedia languages with their native names
        return {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français', 
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'ja': '日本語',
            'zh': '中文',
            'ar': 'العربية',
            'hi': 'हिन्दी',
            'ko': '한국어',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'pl': 'Polski',
            'tr': 'Türkçe',
            'he': 'עברית',
            'da': 'Dansk',
            'no': 'Norsk',
            'fi': 'Suomi',
            'cs': 'Čeština',
            'hu': 'Magyar',
            'ro': 'Română',
            'uk': 'Українська',
            'th': 'ไทย',
            'vi': 'Tiếng Việt',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu',
            'fa': 'فارسی',
            'bn': 'বাংলা',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'ml': 'മലയാളം',
            'kn': 'ಕನ್ನಡ',
            'gu': 'ગુજરાતી',
            'mr': 'मराठी',
            'pa': 'ਪੰਜਾਬੀ',
            'or': 'ଓଡ଼ିଆ',
            'as': 'অসমীয়া',
            'ur': 'اردو',
            'ne': 'नेपाली',
            'si': 'සිංහල',
            'my': 'မြန်မာ',
            'km': 'ខ្មែរ',
            'lo': 'ລາວ',
            'ka': 'ქართული',
            'am': 'አማርኛ',
            'sw': 'Kiswahili',
            'yo': 'Yorùbá',
            'ig': 'Igbo',
            'ha': 'Hausa',
            'zu': 'IsiZulu'
        }
    
    def search_articles(self, query, language='en', limit=10):
        """Search for Wikipedia articles and return suggestions"""
        try:
            # Определяем, запущено ли на Render (через переменную среды)
            url = f"https://{language}.wikipedia.org/w/api.php"

            params = {
                'action': 'opensearch',
                'search': query,
                'limit': limit,
                'namespace': 0,
                'format': 'json',
                'redirects': 'resolve'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if len(data) >= 2:
                titles = data[1]
                descriptions = data[2] if len(data) > 2 else [''] * len(titles)
                urls = data[3] if len(data) > 3 else [''] * len(titles)
                
                suggestions = []
                for i, title in enumerate(titles):
                    suggestions.append({
                        'title': title,
                        'description': descriptions[i] if i < len(descriptions) else '',
                        'url': urls[i] if i < len(urls) else ''
                    })
                return suggestions
            
            return []
        
        except Exception as e:
            logging.error(f"Error searching articles: {e}")
            return []
    
    def get_article_info(self, title, language='en'):
        """Get basic article information"""
        try:
            url = self.api_url.format(lang=language)
            params = {
                'action': 'query',
                'titles': title,
                'format': 'json',
                'prop': 'info|extracts',
                'exintro': True,
                'explaintext': True,
                'exsectionformat': 'plain'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page in pages.items():
                if page_id != '-1':  # Page exists
                    return {
                        'title': page.get('title', title),
                        'extract': page.get('extract', ''),
                        'pageid': page.get('pageid'),
                        'url': f"https://{language}.wikipedia.org/wiki/{quote(page.get('title', title))}"
                    }
            
            return None
        
        except Exception as e:
            logging.error(f"Error getting article info: {e}")
            return None
    
    def get_language_links(self, title, language='en'):
        """Get available language versions of an article"""
        try:
            url = self.api_url.format(lang=language)
            params = {
                'action': 'query',
                'titles': title,
                'format': 'json',
                'prop': 'langlinks',
                'lllimit': 'max'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            language_versions = []
            supported_languages = self.get_supported_languages()
            
            # Add the original language
            language_versions.append({
                'lang': language,
                'title': title,
                'language_name': supported_languages.get(language, language)
            })
            
            for page_id, page in pages.items():
                if page_id != '-1' and 'langlinks' in page:
                    for langlink in page['langlinks']:
                        lang_code = langlink.get('lang')
                        if lang_code in supported_languages:
                            language_versions.append({
                                'lang': lang_code,
                                'title': langlink.get('*'),
                                'language_name': supported_languages[lang_code]
                            })
            
            # Sort by language name
            language_versions.sort(key=lambda x: x['language_name'])
            return language_versions
        
        except Exception as e:
            logging.error(f"Error getting language links: {e}")
            return []
    
    def get_article_content(self, title, language='en'):
        """Get full article content"""
        try:
            # Use only the action=query API to avoid URL encoding issues
            api_url = self.api_url.format(lang=language)
            params = {
                'action': 'query',
                'titles': title,
                'format': 'json',
                'prop': 'extracts',
                'explaintext': True,
                'exsectionformat': 'plain'
            }
            
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page in pages.items():
                if page_id != '-1':
                    content = page.get('extract', '')
                    if content:
                        return content
            
            return None
        
        except Exception as e:
            logging.error(f"Error getting article content for {title} in {language}: {e}")
            return None
    
    def fetch_articles_parallel(self, article_requests):
        """Fetch multiple articles in parallel"""
        articles = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_request = {
                executor.submit(self.get_article_content, req['title'], req['language']): req 
                for req in article_requests
            }
            
            for future in as_completed(future_to_request):
                request = future_to_request[future]
                try:
                    content = future.result()
                    if content:
                        articles[request['language']] = {
                            'title': request['title'],
                            'content': content,
                            'language': request['language']
                        }
                except Exception as e:
                    logging.error(f"Error fetching article {request['title']} in {request['language']}: {e}")
        
        return articles
