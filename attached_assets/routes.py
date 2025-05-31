import json
import logging
from flask import render_template, request, jsonify, session, redirect, url_for, flash, make_response
from app import app
from wikipedia_api import WikipediaAPI
from openai_service import OpenAIService
from document_export import DocumentExporter

wiki_api = WikipediaAPI()
openai_service = OpenAIService()
doc_exporter = DocumentExporter()

# routes.py
from uuid import uuid4
from flask import Blueprint, session, redirect, url_for, render_template

bp = Blueprint("cmp", __name__)

@bp.route("/perform_comparison", methods=["POST"])
def perform_comparison():
    # 1. Готовим статьи …
    html = run_gpt(full_articles)

    # 2. Уникальный ID результата
    rid = str(uuid4())
    session[f"cmp_{rid}"] = html            # кладём

    return redirect(url_for("cmp.result", rid=rid))


@bp.route("/comparison_result/<rid>")
def result(rid):
    html = session.get(f"cmp_{rid}")
    if html is None:
        flash("Результат не найден, давай попробуем ещё раз?")
        return redirect(url_for("index"))

    return render_template("comparison_result.html", html=html)


@app.route('/')
def index():
    """Homepage with language selection and search functionality"""
    languages = wiki_api.get_supported_languages()
    return render_template('index.html', languages=languages)

@app.route('/search_suggestions')
def search_suggestions():
    """AJAX endpoint for real-time article suggestions"""
    query = request.args.get('query', '').strip()
    language = request.args.get('language', 'en').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        suggestions = wiki_api.search_articles(query, language, limit=10)
        return jsonify(suggestions)
    except Exception as e:
        logging.error(f"Error getting search suggestions: {e}")
        return jsonify([])

@app.route('/article/<language>/<path:title>')
def article_selection(language, title):
    """Show available language versions of the selected article"""
    try:
        # Decode URL-encoded title to handle special characters
        from urllib.parse import unquote
        decoded_title = unquote(title)
        
        # Get article info and available languages
        article_info = wiki_api.get_article_info(decoded_title, language)
        if not article_info:
            flash('Article not found.', 'error')
            return redirect(url_for('index'))
        
        # Get available language versions
        language_versions = wiki_api.get_language_links(decoded_title, language)
        if not language_versions:
            flash('No other language versions found for this article.', 'error')
            return redirect(url_for('index'))
        
        # Store article info in session
        session['selected_article'] = {
            'title': decoded_title,
            'language': language,
            'article_info': article_info
        }
        
        output_languages = wiki_api.get_supported_languages()
        
        return render_template('language_selection.html', 
                             article_info=article_info,
                             language_versions=language_versions,
                             output_languages=output_languages,
                             selected_language=language)
    
    except Exception as e:
        logging.error(f"Error in article selection: {e}")
        flash('An error occurred while loading the article.', 'error')
        return redirect(url_for('index'))

@app.route('/compare', methods=['POST'])
def compare_articles():
    """Compare selected articles using OpenAI GPT-4"""
    try:
        # Get form data
        selected_languages = request.form.getlist('languages')
        output_language = request.form.get('output_language', 'en')
        comparison_mode = request.form.get('mode', 'normal')  # normal or funny
        
        if len(selected_languages) < 2:
            flash('Please select at least 2 language versions to compare.', 'error')
            return redirect(request.referrer)
        
        if len(selected_languages) > 5:
            flash('Please select no more than 5 language versions.', 'error')
            return redirect(request.referrer)
        
        # Get article info from session
        article_data = session.get('selected_article')
        if not article_data:
            flash('Article data not found. Please start over.', 'error')
            return redirect(url_for('index'))
        
        # Store comparison parameters in session
        session['comparison_params'] = {
            'languages': selected_languages,
            'output_language': output_language,
            'mode': comparison_mode,
            'article_title': article_data['title'],
            'base_language': article_data['language']
        }
        
        return render_template('loading.html')
    
    except Exception as e:
        logging.error(f"Error starting comparison: {e}")
        flash('An error occurred while starting the comparison.', 'error')
        return redirect(request.referrer)

@app.route('/perform_comparison')
def perform_comparison():
    """Perform the actual comparison (called via AJAX from loading page)"""
    try:
        params = session.get('comparison_params')
        article_data = session.get('selected_article')
        
        if not params or not article_data:
            return jsonify({'error': 'Missing comparison parameters'})
        
        # Fetch article contents for selected languages
        articles = {}
        base_title = article_data['title']
        base_language = article_data['language']
        
        # Get language links to map titles
        language_links = wiki_api.get_language_links(base_title, base_language)
        
        for lang_code in params['languages']:
            if lang_code == base_language:
                title = base_title
            else:
                # Find the title in this language
                title = None
                for link in language_links:
                    if link['lang'] == lang_code:
                        title = link['title']
                        break
                
                if not title:
                    continue
            
            # Fetch article content
            content = wiki_api.get_article_content(title, lang_code)
            if content:
                articles[lang_code] = {
                    'title': title,
                    'content': content,
                    'language': lang_code
                }
        
        if len(articles) < 2:
            return jsonify({'error': 'Could not fetch enough articles for comparison'})
        
        # Perform comparison using OpenAI
        if params['mode'] == 'funny':
            comparison_result = openai_service.compare_articles_funny(
                articles, params['output_language']
            )
        else:
            comparison_result = openai_service.compare_articles(
                articles, params['output_language']
            )
        
        # Store result in session for potential export
        session['comparison_result'] = comparison_result
        
        return jsonify({'success': True, 'redirect_url': url_for('show_comparison')})
    
    except Exception as e:
        logging.error(f"Error performing comparison: {e}")
        return jsonify({'error': 'An error occurred during comparison'})

@app.route('/comparison_result')
def show_comparison():
    """Show the comparison result"""
    try:
        comparison_result = session.get('comparison_result')
        comparison_params = session.get('comparison_params')
        
        if not comparison_result or not comparison_params:
            flash('No comparison result found. Please start a new comparison.', 'error')
            return redirect(url_for('index'))
        
        return render_template('comparison.html', 
                             result=comparison_result,
                             params=comparison_params)
    
    except Exception as e:
        logging.error(f"Error showing comparison: {e}")
        flash('An error occurred while displaying the result.', 'error')
        return redirect(url_for('index'))

@app.route('/export_docx')
def export_docx():
    """Export comparison result as .docx file"""
    try:
        comparison_result = session.get('comparison_result')
        comparison_params = session.get('comparison_params')
        
        if not comparison_result or not comparison_params:
            flash('No comparison result found to export.', 'error')
            return redirect(url_for('index'))
        
        # Generate document
        doc_content = doc_exporter.create_document(comparison_result, comparison_params)
        
        # Create response
        response = make_response(doc_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response.headers['Content-Disposition'] = f'attachment; filename=wiki_truth_comparison_{comparison_params["article_title"]}.docx'
        
        return response
    
    except Exception as e:
        logging.error(f"Error exporting document: {e}")
        flash('An error occurred while exporting the document.', 'error')
        return redirect(url_for('show_comparison'))

@app.route('/get_share_content')
def get_share_content():
    """Get content for sharing (returns JSON with text and URL)"""
    try:
        comparison_result = session.get('comparison_result')
        comparison_params = session.get('comparison_params')
        
        if not comparison_result or not comparison_params:
            return jsonify({'error': 'No comparison result found'})
        
        # Create shareable text
        share_text = f"Wiki Truth Comparison: {comparison_params['article_title']}\n\n"
        share_text += f"Languages compared: {', '.join(comparison_params['languages'])}\n"
        share_text += f"Output language: {comparison_params['output_language']}\n"
        share_text += f"Mode: {comparison_params['mode']}\n\n"
        share_text += comparison_result[:500] + "..." if len(comparison_result) > 500 else comparison_result
        share_text += "\n\nGenerated by Wiki Truth - Compare Wikipedia across languages"
        
        current_url = request.url_root + 'comparison_result'
        
        return jsonify({
            'text': share_text,
            'url': current_url
        })
    
    except Exception as e:
        logging.error(f"Error getting share content: {e}")
        return jsonify({'error': 'An error occurred while preparing share content'})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', 
                         content='<h1>Page Not Found</h1><p>The page you are looking for does not exist.</p>'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', 
                         content='<h1>Internal Server Error</h1><p>An unexpected error occurred.</p>'), 500
