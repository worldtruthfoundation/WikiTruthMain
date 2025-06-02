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
            if mode == 'bio':
                system_prompt = self._get_biography_mode_prompt(output_language)
            elif mode == 'funny':
                system_prompt = self._get_funny_mode_prompt(output_language)
            else:
                system_prompt = self._get_normal_mode_prompt(output_language)

            
            user_prompt = f"""Please compare these Wikipedia articles about the same topic across different languages:

{chr(10).join(article_summaries)}
Your task is to analyze them deeply and produce a detailed, structured, and thorough comparison. Do NOT summarize. Instead, identify and describe every factual difference, contradiction, addition, and omission.

For each article, pay close attention to:
- Specific dates, names, places, figures, numbers
- Contradictory claims or missing details
- Regional or ideological framing of the topic
- Emphasized vs. downplayed aspects
- Sections or facts present only in one version
- Organization or structural formatting

Your analysis must:
- Mention **which language version** contains which fact
- Be written in {self._get_language_name(output_language)}
- Include **explicit examples** from the text
- Cover **each of the following** sections:
  1. Executive Summary
  2. Factual Differences (quote or paraphrase specific facts)
  3. Cultural Perspectives
  4. Coverage Differences
  5. Structural Differences
  6. Unique Insights
  7. Meta-analysis Conclusion

Your tone should be intelligent, analytical, and descriptive — like a comparative study in a top academic journal. Do not omit minor differences — **list all factual variations explicitly**."""
            
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

The goal is not to summarize, but to analyze and **highlight all factual, structural, and cultural differences** among the versions. Imagine you are writing a new, meta-encyclopedic article called "**How Wikipedia Talks About title of givven article Around the World**".

Your output should follow this structure:

1. **Executive Summary** — Key findings in 1-2 paragraphs.
2. **Factual Differences** — Contradictions or variances in dates, events, names, numbers.
3. **Cultural Perspectives** — Differences in tone, emphasis, point of view, or interpretation based on regional/national context.
4. **Coverage Differences** — What sections or facts are present in one language and missing in others.
5. **Structural Differences** — Different chapter structures or layout between versions.
6. **Unique Insights** — Rare facts or viewpoints only found in a specific version.
7. **Meta-analysis Conclusion** — What do these differences say about how different cultures understand this topic?

Your analisis should be very discriptive and lool like a new article. FIND ALL DIFFERENCES AND SHOW THEM

Style: Write fluidly and engagingly. Like a feature article in a scholarly magazine. Avoid dry bullet points. Use comparisons and rich language to make the analysis insightful and enjoyable to read.


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
    
    def _get_biography_mode_prompt(self, output_language):
        """Get system prompt for biography comparison mode"""
        lang_name = self._get_language_name(output_language)
        return f"""You are an expert analyst in biography comparison and geopolitical profiling. Your task is to compare Wikipedia biographies across languages and evaluate all details from a security and eligibility standpoint.

Write the analysis in {lang_name} and follow the structure below. List **all factual differences and contradictions**. Be comprehensive and precise.

Use the following structure:

1. **Basic Information**
   - Date and place of birth
   - Ethnic origin, social status of family
   - Parents (names, professions, cultural context)
   - Spouse and their origin (including maiden name)

2. **Education**
   - School/lyceum (especially elite or special)
   - University, faculty, specialization
   - Notable classmates
   - Academic achievements

3. **Career**
   - Early positions (esp. in national or regional structures)
   - Career progression: high offices, international roles
   - Academic/advisory positions (e.g. rector advisor)

4. **Social and Political Ties**
   - Politically significant family ties
   - Dual citizenship or foreign relations
   - Religious or ethnic identity (e.g., by Halakha)

5. **Security Risk Assessment**
   - Presence of "personnel filters":
     - Spouse’s citizenship from countries with no diplomatic ties
     - National-cultural issues
     - Conflicts with national security policies
   - Potential risks: defection, betrayal, loss of trust

6. **Public Statements and Views**
   - Quotes, ideological positions, speeches
   - Media presence, scandals or controversies

7. **Public Perception**
   - How media/society views them
   - Trust rating, positive/negative contexts

8. **Final Assessment**
   - Suitability for public or governmental roles
   - Risk level: security and reputation
   - Conclusion: Fit/Unfit with clear reasoning

Provide **explicit references** to which article/language each fact or contradiction came from. Be analytical, not speculative. This is not a summary — it’s a comparative dossier."""


    
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
