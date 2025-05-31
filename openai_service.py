import os
import logging
from openai import OpenAI

class OpenAIService:
    """Handles OpenAI API interactions for article comparison"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def compare_articles(self, articles, output_language='en', mode='normal'):
        """Compare Wikipedia articles using GPT-4"""
        try:
            # Prepare article summaries for comparison
            article_summaries = []
            for lang, article in articles.items():
                summary = f"**{article['language']} ({lang})**: {article['title']}\n"
                # Limit content to avoid token limits
                content = article['content'][:3000] if len(article['content']) > 3000 else article['content']
                summary += content
                article_summaries.append(summary)
            
            # Create the comparison prompt
            if mode == 'funny':
                system_prompt = self._get_funny_mode_prompt(output_language)
            else:
                system_prompt = self._get_normal_mode_prompt(output_language)
            
            user_prompt = f"""Please compare these Wikipedia articles about the same topic across different languages:

{chr(10).join(article_summaries)}

Focus on:
1. Factual differences and contradictions
2. Cultural perspectives and biases
3. Different emphasis or coverage areas
4. Unique information in each version
5. Notable omissions or additions

Please provide your analysis in {self._get_language_name(output_language)}."""
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=3000,
                temperature=0.7 if mode == 'funny' else 0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logging.error(f"Error in OpenAI comparison: {e}")
            raise Exception(f"AI comparison failed: {str(e)}")
    
    def _get_normal_mode_prompt(self, output_language):
        """Get system prompt for normal comparison mode"""
        lang_name = self._get_language_name(output_language)
        return f"""You are a knowledgeable research analyst specializing in cross-cultural information analysis. Your task is to compare Wikipedia articles across different languages and identify meaningful differences.

Provide a comprehensive, structured analysis in {lang_name} that includes:

1. **Executive Summary**: Brief overview of the most significant differences
2. **Factual Differences**: Specific contradictions, different dates, numbers, or claims
3. **Cultural Perspectives**: How different regions present the topic differently
4. **Coverage Variations**: What each version emphasizes or omits
5. **Structural Differences**: How the information is organized differently
6. **Unique Insights**: Information only found in specific language versions

Be objective, scholarly, and detailed in your analysis. Highlight both similarities and differences. When noting differences, be specific about which language version contains what information."""
    
    def _get_funny_mode_prompt(self, output_language):
        """Get system prompt for funny comparison mode"""
        lang_name = self._get_language_name(output_language)
        return f"""You are a witty, sarcastic cultural commentator with a PhD in "Wikipedia Anthropology." Your job is to hilariously expose how different cultures present the same topic on Wikipedia, while still being educational and respectful.

Write your analysis in {lang_name} with humor, but maintain these guidelines:
- Be entertaining and sarcastic about cultural biases and differences
- Use humor to highlight absurdities or contradictions
- Make clever observations about regional perspectives  
- Include amusing commentary on what each culture chooses to emphasize
- Be respectful and avoid offensive stereotypes
- Still provide genuine educational value
- Use a conversational, entertaining tone

Think of yourself as a comedian doing cultural commentary, but one who actually knows their stuff and wants to teach people something while making them laugh."""
    
    def _get_language_name(self, code):
        """Get full language name from code"""
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'ko': 'Korean',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'pl': 'Polish',
            'tr': 'Turkish',
            'he': 'Hebrew',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'uk': 'Ukrainian',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'fa': 'Persian',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'ur': 'Urdu',
            'ne': 'Nepali',
            'si': 'Sinhala',
            'my': 'Burmese',
            'km': 'Khmer',
            'lo': 'Lao',
            'ka': 'Georgian',
            'am': 'Amharic',
            'sw': 'Swahili',
            'yo': 'Yoruba',
            'ig': 'Igbo',
            'ha': 'Hausa',
            'zu': 'Zulu'
        }
        return language_names.get(code, 'English')
