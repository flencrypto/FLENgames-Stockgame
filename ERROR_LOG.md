# Error Log

## Resolved Issues

- **Incorrect PWA entry points**: `manifest.json` and `sw.js` referenced `Index.html` (capital `I`), which fails on case-sensitive hosts such as GitHub Pages and breaks installation/offline fallbacks. Updated both files to use the correct lowercase `index.html` paths.
- **Hard-coded Alpha Vantage API key**: The production API key was committed directly in `index.html`, exposing the secret and breaking the user's own quota. Added a secure settings field that stores the key in local storage, added runtime guards, and updated documentation so live data only runs when a user supplies their own key.
