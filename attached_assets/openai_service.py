import os
import json
import logging
from openai import OpenAI

class OpenAIService:
    """Handles OpenAI GPT-4 interactions for article comparison"""
    
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def chunk_text(self, text, max_tokens=3000):
        """Split text into chunks that fit within token limits"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            # Rough estimation: 1 token ≈ 0.75 words
            if current_length + len(word) * 1.3 > max_tokens and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) * 1.3
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def compare_articles(self, articles, output_language='en'):
        """Compare Wikipedia articles across languages using GPT-4"""
        try:
            # Prepare the content for comparison
            article_summaries = []
            full_content = ""
            
            for lang_code, article in articles.items():
                content = article['content']
                title = article['title']
                
                # Create a summary of each article for the prompt
                summary = f"\n\n=== ARTICLE IN {lang_code.upper()} ===\n"
                summary += f"Title: {title}\n"
                summary += f"Content: {content[:2000]}{'...' if len(content) > 2000 else ''}\n"
                
                article_summaries.append(summary)
                full_content += summary
            
            # Determine output language name
            language_names = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
                'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi', 'ko': 'Korean'
            }
            output_lang_name = language_names.get(output_language, output_language)
            
            # Create the comparison prompt
            prompt = f"""
You are an expert researcher analyzing Wikipedia articles across different languages. Compare the following Wikipedia articles and provide a detailed analysis ENTIRELY in {output_lang_name}. 

IMPORTANT: Your entire response must be written in {output_lang_name}, not in English. If the output language is Russian, write everything in Russian. If it's Chinese, write everything in Chinese, etc.

{full_content}

Please provide a comprehensive comparison that includes:

1. **Overview**: Briefly describe what the article is about and which languages were compared.

2. **Content Differences**: 
   - What information is present in some versions but not others?
   - Which language versions are more comprehensive?
   - Are there different perspectives or emphasis on certain aspects?

3. **Factual Variations**:
   - Are there any contradictory facts or figures?
   - Do dates, numbers, or specific details differ?
   - Are there different claims about the same events or concepts?

4. **Cultural and Regional Perspectives**:
   - How do different language versions reflect regional viewpoints?
   - Are there cultural biases or emphasis differences?
   - What unique insights does each language version provide?

5. **Structure and Focus**:
   - How do the articles differ in organization?
   - What topics get more attention in each version?
   - Are there sections present in some but not others?

6. **Sources and References**:
   - Do the articles cite different types of sources?
   - Are there region-specific references?

Please be specific about which language version contains what information, and provide examples where possible. Make the analysis extensive, well-formatted, and traceable to specific language versions.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert researcher and analyst specializing in cross-cultural information comparison. Provide detailed, objective, and well-structured analyses."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error comparing articles: {e}")
            raise Exception(f"Failed to compare articles: {str(e)}")
    
    def compare_articles_funny(self, articles, output_language='en'):
        """Compare articles with humorous, sarcastic commentary"""
        try:
            # Prepare the content for comparison
            article_summaries = []
            full_content = ""
            
            for lang_code, article in articles.items():
                content = article['content']
                title = article['title']
                
                summary = f"\n\n=== ARTICLE IN {lang_code.upper()} ===\n"
                summary += f"Title: {title}\n"
                summary += f"Content: {content[:2000]}{'...' if len(content) > 2000 else ''}\n"
                
                article_summaries.append(summary)
                full_content += summary
            
            # Determine output language name
            language_names = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
                'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi', 'ko': 'Korean'
            }
            output_lang_name = language_names.get(output_language, output_language)
            
            # Create the funny comparison prompt
            prompt = f"""
You are a witty, sarcastic cultural critic analyzing Wikipedia articles across different languages. Your job is to provide a humorous, roast-style commentary on the differences between these Wikipedia articles, written ENTIRELY in {output_lang_name}.

IMPORTANT: Your entire response must be written in {output_lang_name}, not in English. If the output language is Russian, write everything in Russian. If it's Chinese, write everything in Chinese, etc.

{full_content}

Write a hilarious analysis that:

1. **Roasts the Inconsistencies**: Point out contradictions and differences with sarcastic humor
2. **Cultural Stereotypes**: Playfully highlight how each language version reflects cultural biases (while being respectful)
3. **Information Gaps**: Mock the gaps and omissions in different versions
4. **Regional Pride**: Comment on how each version seems to favor their own region/culture
5. **Surprising Twists**: Point out the most unexpected differences between versions

Use a tone that's:
- Witty and sarcastic but not mean-spirited
- Entertaining and engaging
- Educational while being funny
- Respectful of cultures while poking fun at biases

Be specific about which language version does what, and make it feel like a comedy roast of Wikipedia's inconsistencies across cultures. Include plenty of humor about how different cultures apparently can't agree on the same basic facts!
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a brilliant comedy writer and cultural critic. Your specialty is finding humor in cultural differences and inconsistencies while remaining respectful and educational."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error in funny comparison: {e}")
            raise Exception(f"Failed to create funny comparison: {str(e)}")
