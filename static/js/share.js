/**  WikiTruth ‒ модуль шаринга  */
(function (window, document) {

  // --- служебные данные, если нужно переопределить со страницы ---
  const defaults = {
    get text()      { return "Check out this WikiTruth comparison!"; },
    get url()       { return window.location.href; },
    get modeTitle() { return document.title || "WikiTruth"; }
  };

  /**
   * Открывает нужный сервис или копирует ссылку
   * @param {string}  platform  twitter | linkedin | reddit | telegram | whatsapp | email | copy
   * @param {Object?} opts      {text, url, modeTitle} ‒ можно переопределить на лету
   */
  function shareOn(platform, opts = {}) {
    const { text, url, modeTitle } = { ...defaults, ...opts };
    switch (platform) {

      case 'twitter':
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
        break;

      case 'linkedin':
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank');
        break;

      case 'reddit':
        window.open(`https://www.reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`, '_blank');
        break;

      case 'telegram':
        window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, '_blank');
        break;

      case 'whatsapp':
        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text + ' ' + url)}`, '_blank');
        break;

      case 'email':
        const subject = `WikiTruth - ${modeTitle}`;
        const body    = `${text}\n\n${url}`;
        window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        break;

      case 'copy':
        navigator.clipboard.writeText(url)
          .then(() => notify('Link copied to clipboard', 'success'))
          .catch(err => {
            console.error('Clipboard error:', err);
            notify('Failed to copy link', 'error');
          });
        break;
    }
  }

  /** Простенький to-go нотайфай (можешь заменить на Toast из Bootstrap) */
  function notify(msg, type = 'info') {
    alert(msg);          // пока хватит alert'а
  }

  // --- экспорт ---
  window.WikiTruth = window.WikiTruth || {};
  window.WikiTruth.shareOn = shareOn;

})(window, document);
