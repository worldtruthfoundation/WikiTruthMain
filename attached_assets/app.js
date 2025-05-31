// Wiki Truth JavaScript functionality

class WikiTruthApp {
    constructor() {
        this.searchTimeout = null;
        this.currentRequest = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeTooltips();
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
            searchInput.addEventListener('blur', () => this.hideSuggestions());
        }

        // Language selection form
        const languageForm = document.getElementById('language-form');
        if (languageForm) {
            languageForm.addEventListener('submit', (e) => this.handleLanguageSubmit(e));
        }

        // Share buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-share')) {
                e.preventDefault();
                this.handleShare(e.target.dataset.platform);
            }
        });

        // Copy to clipboard functionality
        const copyBtn = document.getElementById('copy-text-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }

        // Loading page functionality
        if (document.body.classList.contains('loading-page')) {
            this.startComparison();
        }
    }

    handleSearchInput(event) {
        const query = event.target.value.trim();
        const language = document.getElementById('language-select')?.value || 'en';

        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Cancel previous request
        if (this.currentRequest) {
            this.currentRequest.abort();
        }

        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        // Debounce search requests
        this.searchTimeout = setTimeout(() => {
            this.fetchSuggestions(query, language);
        }, 300);
    }

    async fetchSuggestions(query, language) {
        try {
            const controller = new AbortController();
            this.currentRequest = controller;

            const response = await fetch(
                `/search_suggestions?query=${encodeURIComponent(query)}&language=${encodeURIComponent(language)}`,
                { signal: controller.signal }
            );

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const suggestions = await response.json();
            this.displaySuggestions(suggestions, language);
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error fetching suggestions:', error);
                this.hideSuggestions();
            }
        } finally {
            this.currentRequest = null;
        }
    }

    displaySuggestions(suggestions, language) {
        const container = document.getElementById('search-suggestions');
        if (!container) return;

        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        container.innerHTML = '';
        container.style.display = 'block';

        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'search-suggestion';
            div.innerHTML = `
                <div class="suggestion-title">${this.escapeHtml(suggestion.title)}</div>
                ${suggestion.description ? `<div class="suggestion-description">${this.escapeHtml(suggestion.description)}</div>` : ''}
            `;
            
            // Use mousedown instead of click to prevent blur from interfering
            div.addEventListener('mousedown', (e) => {
                e.preventDefault();
                this.selectSuggestion(suggestion, language);
            });
            
            div.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectSuggestion(suggestion, language);
            });

            container.appendChild(div);
        });
    }

    selectSuggestion(suggestion, language) {
        // Navigate to article selection page
        console.log('Selecting suggestion:', suggestion.title, 'in language:', language);
        const url = `/article/${encodeURIComponent(language)}/${encodeURIComponent(suggestion.title)}`;
        console.log('Navigating to:', url);
        window.location.href = url;
    }

    hideSuggestions() {
        // Delay hiding to allow for click events
        setTimeout(() => {
            const container = document.getElementById('search-suggestions');
            if (container) {
                container.style.display = 'none';
            }
        }, 300);
    }

    handleLanguageSubmit(event) {
        const selectedLanguages = document.querySelectorAll('input[name="languages"]:checked');
        
        if (selectedLanguages.length < 2) {
            event.preventDefault();
            alert('Please select at least 2 language versions to compare.');
            return false;
        }

        if (selectedLanguages.length > 5) {
            event.preventDefault();
            alert('Please select no more than 5 language versions.');
            return false;
        }

        return true;
    }

    async startComparison() {
        try {
            const response = await fetch('/perform_comparison');
            const result = await response.json();

            if (result.success) {
                window.location.href = result.redirect_url;
            } else {
                throw new Error(result.error || 'Comparison failed');
            }
        } catch (error) {
            console.error('Comparison error:', error);
            document.querySelector('.loading-text').textContent = 'An error occurred during comparison.';
            document.querySelector('.loading-details').innerHTML = `
                <p>Error: ${error.message}</p>
                <p><a href="/" class="btn btn-primary">Return to Homepage</a></p>
            `;
        }
    }

    async handleShare(platform) {
        try {
            const response = await fetch('/get_share_content');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            const text = data.text;
            const url = data.url;

            switch (platform) {
                case 'twitter':
                    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text.substring(0, 240) + '...')}&url=${encodeURIComponent(url)}`;
                    window.open(twitterUrl, '_blank');
                    break;

                case 'linkedin':
                    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}&summary=${encodeURIComponent(text.substring(0, 256))}`;
                    window.open(linkedinUrl, '_blank');
                    break;

                case 'telegram':
                    const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text.substring(0, 300))}`;
                    window.open(telegramUrl, '_blank');
                    break;

                case 'whatsapp':
                    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(text.substring(0, 300) + ' ' + url)}`;
                    window.open(whatsappUrl, '_blank');
                    break;

                case 'reddit':
                    const redditUrl = `https://www.reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent('Wiki Truth Comparison: Interesting differences in Wikipedia across languages')}`;
                    window.open(redditUrl, '_blank');
                    break;

                case 'copy':
                    await this.copyTextToClipboard(text + '\n\n' + url);
                    this.showCopySuccess();
                    break;

                default:
                    console.error('Unknown platform:', platform);
            }
        } catch (error) {
            console.error('Share error:', error);
            alert('An error occurred while sharing. Please try again.');
        }
    }

    async copyToClipboard() {
        try {
            const response = await fetch('/get_share_content');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            await this.copyTextToClipboard(data.text + '\n\n' + data.url);
            this.showCopySuccess();
        } catch (error) {
            console.error('Copy error:', error);
            alert('An error occurred while copying. Please try again.');
        }
    }

    async copyTextToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }
    }

    showCopySuccess() {
        const btn = document.getElementById('copy-text-btn') || event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.style.backgroundColor = '#28a745';
        btn.style.borderColor = '#28a745';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.backgroundColor = '';
            btn.style.borderColor = '';
            btn.style.color = '';
        }, 2000);
    }

    initializeTooltips() {
        // Add tooltips to help explain functionality
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => this.showTooltip(e));
            element.addEventListener('mouseleave', () => this.hideTooltip());
        });
    }

    showTooltip(event) {
        const text = event.target.dataset.tooltip;
        if (!text) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            pointer-events: none;
            white-space: nowrap;
        `;

        document.body.appendChild(tooltip);

        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';

        this.currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WikiTruthApp();
});

// Additional utility functions
function toggleLanguageSelection(checkbox) {
    const selectedCount = document.querySelectorAll('input[name="languages"]:checked').length;
    const submitBtn = document.getElementById('compare-btn');
    
    if (submitBtn) {
        submitBtn.disabled = selectedCount < 2;
        if (selectedCount < 2) {
            submitBtn.textContent = 'Select at least 2 languages';
        } else if (selectedCount > 5) {
            submitBtn.textContent = 'Too many languages selected';
            submitBtn.disabled = true;
        } else {
            submitBtn.textContent = `Compare ${selectedCount} Articles`;
            submitBtn.disabled = false;
        }
    }
}

function setComparisonMode(mode) {
    document.getElementById('comparison-mode').value = mode;
    
    // Update button states
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
    });
    
    event.target.classList.remove('btn-secondary');
    event.target.classList.add('btn-primary');
}
