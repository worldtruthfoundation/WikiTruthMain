// Wiki Truth - Main JavaScript functionality

// Global variables
let searchTimeout;
let selectedLanguage = 'en';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeLanguageSelection();
    initializeComparisonMode();
    initializeShareButtons();
    initializeCopyFunctionality();
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('search-input');
    const languageSelect = document.getElementById('language-select');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (!searchInput) return;
    
    // Update selected language when dropdown changes
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            selectedLanguage = this.value;
            // Clear suggestions when language changes
            if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
        });
        selectedLanguage = languageSelect.value;
    }
    
    // Search input handling
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear existing timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Hide suggestions if query is too short
        if (query.length < 2) {
            if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
            return;
        }
        
        // Debounce the search
        searchTimeout = setTimeout(() => {
            searchArticles(query, selectedLanguage);
        }, 300);
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (suggestionsContainer && !suggestionsContainer.contains(e.target) && e.target !== searchInput) {
            suggestionsContainer.style.display = 'none';
        }
    });
    
    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (!suggestionsContainer) return;
        
        const suggestions = suggestionsContainer.querySelectorAll('.search-suggestion');
        if (suggestions.length === 0) return;
        
        let selected = suggestionsContainer.querySelector('.search-suggestion.selected');
        let selectedIndex = selected ? Array.from(suggestions).indexOf(selected) : -1;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (selected) selected.classList.remove('selected');
                selectedIndex = (selectedIndex + 1) % suggestions.length;
                suggestions[selectedIndex].classList.add('selected');
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (selected) selected.classList.remove('selected');
                selectedIndex = selectedIndex <= 0 ? suggestions.length - 1 : selectedIndex - 1;
                suggestions[selectedIndex].classList.add('selected');
                break;
                
            case 'Enter':
                e.preventDefault();
                if (selected) {
                    selectArticle(selected.dataset.title);
                } else if (suggestions.length > 0) {
                    selectArticle(suggestions[0].dataset.title);
                }
                break;
                
            case 'Escape':
                suggestionsContainer.style.display = 'none';
                break;
        }
    });
}

// Search for articles using Wikipedia API
function searchArticles(query, language) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (!suggestionsContainer) return;
    
    // Show loading state
    suggestionsContainer.innerHTML = '<div class="search-suggestion">Searching...</div>';
    suggestionsContainer.style.display = 'block';
    
    // Make API request
    fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${language}`)
        .then(response => response.json())
        .then(suggestions => {
            displaySuggestions(suggestions);
        })
        .catch(error => {
            console.error('Search error:', error);
            suggestionsContainer.innerHTML = '<div class="search-suggestion">Error searching articles</div>';
        });
}

// Display search suggestions
function displaySuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (!suggestionsContainer) return;
    
    if (suggestions.length === 0) {
        suggestionsContainer.innerHTML = '<div class="search-suggestion">No articles found</div>';
        return;
    }
    
    const html = suggestions.map(suggestion => `
        <div class="search-suggestion" data-title="${suggestion.title}" onclick="selectArticle('${suggestion.title.replace(/'/g, "\\'")}')">
            <div class="suggestion-title">${suggestion.title}</div>
            ${suggestion.description ? `<div class="suggestion-description">${suggestion.description}</div>` : ''}
        </div>
    `).join('');
    
    suggestionsContainer.innerHTML = html;
    suggestionsContainer.style.display = 'block';
}

// Select an article and navigate to language selection
function selectArticle(title) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
    
    // Navigate to article selection page
    window.location.href = `/article/${selectedLanguage}/${encodeURIComponent(title)}`;
}

// Language selection functionality
function initializeLanguageSelection() {
    // This function manages the language selection checkboxes
    updateCompareButton();
}

function toggleLanguageSelection(checkbox) {
    updateCompareButton();
    
    // Visual feedback
    const label = checkbox.closest('.language-option');
    if (checkbox.checked) {
        label.style.backgroundColor = 'hsl(213 100% 97%)'; // Light blue
        label.style.borderColor = 'hsl(213 94% 33%)'; // Primary blue
    } else {
        label.style.backgroundColor = '';
        label.style.borderColor = '';
    }
}

function updateCompareButton() {
    const compareBtn = document.getElementById('compare-btn');
    if (!compareBtn) return;
    
    const checkedBoxes = document.querySelectorAll('input[name="languages"]:checked');
    const count = checkedBoxes.length;
    
    if (count < 2) {
        compareBtn.disabled = true;
        compareBtn.textContent = 'Select at least 2 languages';
    } else if (count > 5) {
        compareBtn.disabled = true;
        compareBtn.textContent = 'Maximum 5 languages allowed';
    } else {
        compareBtn.disabled = false;
        compareBtn.textContent = `Compare ${count} Language Versions`;
    }
}

// Comparison mode selection
function initializeComparisonMode() {
    // Set initial mode
    setComparisonMode('normal');
}

function setComparisonMode(mode) {
    const modeInput = document.getElementById('comparison-mode');
    const modeButtons = document.querySelectorAll('.mode-btn');
    
    if (modeInput) {
        modeInput.value = mode;
    }
    
    // Update button states
    modeButtons.forEach(btn => {
        if (btn.onclick.toString().includes(mode)) {
            btn.classList.remove('btn-secondary');
            btn.classList.add('btn-primary', 'active');
        } else {
            btn.classList.remove('btn-primary', 'active');
            btn.classList.add('btn-secondary');
        }
    });
}

// Share functionality
function initializeShareButtons() {
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.share-btn');   // ← ищем кнопку
    if (!btn) return;                             // мимо — выходим
    const platform = btn.dataset.platform;
    WikiTruth.shareOn(platform);                  // или shareToSocial(platform);
  });
}

function shareToSocial(platform) {
    const url = window.location.href;
    const title = document.title;
    const text = 'Check out this fascinating Wikipedia comparison from Wiki Truth!';
    
    let shareUrl;
    
    switch(platform) {
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
            break;
            
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
            break;
            
        case 'telegram':
            shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
            break;
            
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`;
            break;
            
        case 'reddit':
            shareUrl = `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
            break;
            
        case 'copy':
            copyLinkAndText();
            return;
    }
    
    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
    }
}

function copyLinkAndText() {
    const url = window.location.href;
    const result = document.querySelector('.comparison-result');
    const text = result ? result.textContent.trim() : '';
    const shareText = `Wiki Truth Comparison\n\n${text}\n\nView full comparison: ${url}`;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Link and text copied to clipboard!');
        }).catch(err => {
            console.error('Copy failed:', err);
            fallbackCopy(shareText);
        });
    } else {
        fallbackCopy(shareText);
    }
}

// Copy functionality
function initializeCopyFunctionality() {
    // Initialize copy buttons
}

function copyToClipboard() {
    const result = document.querySelector('.comparison-result');
    if (!result) return;
    
    const text = result.textContent.trim();
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Comparison copied to clipboard!');
        }).catch(err => {
            console.error('Copy failed:', err);
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!');
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showNotification('Copy failed. Please select and copy manually.');
    }
    
    document.body.removeChild(textArea);
}

// Utility functions
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: hsl(213 94% 33%);
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 1000;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Form validation
function validateForm(form) {
    const languageCheckboxes = form.querySelectorAll('input[name="languages"]:checked');
    const outputLanguage = form.querySelector('select[name="output_language"]');
    const mode = form.querySelector('input[name="mode"]');
    
    if (languageCheckboxes.length < 2) {
        showNotification('Please select at least 2 languages for comparison.');
        return false;
    }
    
    if (languageCheckboxes.length > 5) {
        showNotification('Please select no more than 5 languages for comparison.');
        return false;
    }
    
    if (!outputLanguage.value) {
        showNotification('Please select an output language.');
        return false;
    }
    
    if (!mode.value) {
        showNotification('Please select a comparison mode.');
        return false;
    }
    
    return true;
}

// Form submission handling
document.addEventListener('submit', function(e) {
    if (e.target.id === 'language-form') {
        if (!validateForm(e.target)) {
            e.preventDefault();
        } else {
            // Show loading state
            const submitBtn = e.target.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Starting comparison...';
                submitBtn.disabled = true;
            }
        }
    }
});

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals/suggestions
    if (e.key === 'Escape') {
        const suggestions = document.getElementById('search-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }
});

// Performance optimization: Lazy load images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if supported
if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', lazyLoadImages);
}

// Error handling for failed API requests
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e);
    showNotification('An error occurred. Please try again.');
});

// Analytics and usage tracking (placeholder for future implementation)
function trackEvent(eventName, eventData = {}) {
    // Placeholder for analytics tracking
    console.log('Event:', eventName, eventData);
}

// Track page views
document.addEventListener('DOMContentLoaded', function() {
    trackEvent('page_view', {
        page: window.location.pathname,
        title: document.title
    });
});
