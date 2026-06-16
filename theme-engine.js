/** favicon dinamico miren esto
 */

const darkMatcher = window.matchMedia('(prefers-color-scheme: dark)');
function updateFavicon() {
    let favicon = document.querySelector('link[rel="icon"]');
    if (!favicon) {
        favicon = document.createElement('link');
        favicon.rel = 'icon';
        document.head.appendChild(favicon);
    }
    if (darkMatcher.matches) {
        favicon.href = 'RIF-DARK.png';
    } else {
 favicon.href = 'RIF.png';
}
}

updateFavicon();
darkMatcher.addEventListener('change', updateFavicon);
