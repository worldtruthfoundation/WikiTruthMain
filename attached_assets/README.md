# Wiki Truth

A Flask web application that uses OpenAI GPT-4 to compare Wikipedia articles across multiple languages, revealing fascinating differences in how topics are presented worldwide.

## Features

- **Intelligent Analysis**: GPT-4 powered comparison highlighting factual differences, cultural perspectives, and unique insights across language versions
- **Real-time Search**: Instant article suggestions as you type, powered by Wikipedia's search API
- **50+ Languages**: Compare articles across major world languages including English, Spanish, French, German, Chinese, Arabic, Hindi, and many more
- **Funny Mode**: Get a humorous, sarcastic take on the differences between articles
- **Export & Share**: Download comparisons as Word documents or share directly to social media platforms
- **Wikipedia-style Design**: Perfect replication of Wikipedia's design and user experience
- **Mobile Responsive**: Optimized for mobile devices with touch-friendly interface

## How It Works

1. **Select a language** and search for any Wikipedia article
2. **Choose 2-5 language versions** of the same article to compare
3. **Select your preferred output language** for the comparison
4. **Get an AI-powered analysis** highlighting differences and similarities
5. **Export or share** your findings with others

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd wiki-truth
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export SESSION_SECRET="your-session-secret"
```

4. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Dependencies

- **Flask**: Web framework
- **OpenAI**: GPT-4 API for article comparison
- **Requests**: HTTP library for Wikipedia API calls
- **python-docx**: Word document generation
- **gunicorn**: WSGI HTTP Server

## API Integration

### Wikipedia APIs Used

- **OpenSearch API**: For real-time article suggestions
- **Query API**: For article content and metadata
- **REST API**: For article summaries and extracts
- **Langlinks API**: For finding available language versions

### OpenAI Integration

- Uses GPT-4 (gpt-4o) for intelligent article comparison
- Supports both normal analytical mode and humorous commentary mode
- Handles multiple languages for output

## Architecture

```
wiki-truth/
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── routes.py           # URL routes and handlers
├── wikipedia_api.py    # Wikipedia API integration
├── openai_service.py   # OpenAI GPT-4 integration
├── document_export.py  # Word document generation
├── static/
│   ├── css/
│   │   └── wikipedia.css    # Wikipedia-style CSS
│   └── js/
│       └── app.js           # Frontend JavaScript
└── templates/          # HTML templates
    ├── base.html
    ├── index.html
    ├── language_selection.html
    ├── loading.html
    └── comparison.html
```

## Usage Examples

### Popular Comparison Topics

Articles that often show significant differences across languages:

- **Historical Events**: World War II, Napoleon Bonaparte
- **Cultural Topics**: Pizza, Yoga, Traditional Chinese Medicine
- **Scientific Concepts**: Climate change, Artificial Intelligence
- **Notable Figures**: Albert Einstein, Mahatma Gandhi
- **Political Concepts**: Democracy, various political systems
- **Technology**: Bitcoin, Internet, Social Media

### Output Languages

The application supports analysis output in 50+ languages including:
- European: English, Spanish, French, German, Italian, Russian
- Asian: Chinese, Japanese, Korean, Hindi, Arabic, Thai
- And many more regional languages

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for GPT-4 analysis
- `SESSION_SECRET`: Flask session security (auto-generated if not provided)
- `PORT`: Application port (default: 5000)

### Wikipedia API Settings

The application automatically handles:
- Rate limiting and retries
- Multiple language Wikipedia domains
- Content encoding and special characters
- Parallel article fetching for performance

## Mobile Optimization

- Responsive grid layout that adapts to screen size
- Touch-friendly buttons and interface elements
- Optimized typography for mobile reading
- Prevents zoom on form inputs (iOS)
- Grid-based share buttons for easy access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Deployment

### Using Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Environment Setup

Ensure all environment variables are properly set in your deployment environment.

## Troubleshooting

### Common Issues

1. **Search suggestions not working**: Check network connectivity to Wikipedia APIs
2. **Comparison fails**: Verify OpenAI API key is valid and has sufficient credits
3. **Non-Latin characters**: The app handles URL encoding automatically
4. **Mobile display issues**: Clear browser cache and ensure CSS is loading

### Debugging

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is open source. Wikipedia content is available under Wikipedia's licenses. AI comparisons are generated by OpenAI's GPT-4.

## Disclaimer

**All comparisons are generated by AI and should be used for educational and informational purposes.** We encourage users to verify important information through multiple sources and to approach all content with critical thinking. Wikipedia content is created by volunteers and may contain biases or inaccuracies in any language.

## Mission

Wiki Truth believes that understanding different perspectives is crucial for building a more connected and informed world. By comparing how the same topics are presented across different languages and cultures, we hope to:

- Promote cross-cultural understanding and awareness
- Highlight the importance of diverse perspectives in knowledge
- Encourage critical thinking about information sources
- Celebrate the richness of different cultural viewpoints