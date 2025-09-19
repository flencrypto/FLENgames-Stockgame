# Mr. FLEN's Stock Prediction Game - iPhone Edition

A fully optimized Progressive Web App (PWA) for iPhone that allows users to make stock predictions and compete in a league system.

## 🚀 iPhone Installation

### Method 1: Direct Installation
1. Open Safari on your iPhone
2. Navigate to the app URL
3. Tap the **Share** button at the bottom
4. Scroll down and tap **"Add to Home Screen"**
5. Tap **"Add"** to confirm

### Method 2: Using the Install Banner
1. Open the app in Safari
2. Wait for the install banner to appear
3. Tap the **"Install"** button
4. Follow the detailed instructions provided

## ✨ iPhone Features

### 🎯 Optimized for iPhone
- **Safe Area Support**: Properly handles iPhone notches and home indicators
- **Touch Optimized**: 44px minimum touch targets for easy interaction
- **Haptic Feedback**: Vibration feedback for important actions
- **Smooth Scrolling**: Native iOS scrolling behavior
- **No Zoom on Input**: Prevents unwanted zooming when typing

### 📱 PWA Capabilities
- **Offline Support**: Works without internet connection
- **App-like Experience**: Full-screen mode when installed
- **Home Screen Icon**: Custom app icon with proper sizing
- **Splash Screen**: Native app-like loading experience

### 🎮 Game Features
- **Real-time Stock Data**: Live price feeds using Alpha Vantage API
- **Dual Scoring Systems**: Binary and percentage-based scoring
- **League Competition**: Import/export user data for competitions
- **Prediction History**: Track all your predictions and results
- **User Settings**: Customizable usernames and themes

## 🛠 Technical Features

### iPhone-Specific Optimizations
- **Viewport Meta Tags**: Proper scaling and safe area handling
- **Apple Touch Icons**: Multiple sizes for different contexts
- **iOS Safari Compatibility**: Optimized for Safari's rendering engine
- **Touch Event Handling**: Prevents double-tap zoom and improves responsiveness

### Performance
- **Service Worker**: Caches resources for offline use
- **Preconnect**: Faster loading of external resources
- **Optimized CSS**: Hardware-accelerated animations
- **Minimal Dependencies**: Fast loading times

## 📋 Usage Instructions

1. **Make a Prediction**:
   - Enter a stock symbol (e.g., AAPL, GOOGL)
   - Choose prediction period (Today/Week)
   - Select UP or DOWN prediction
   - Tap "LAUNCH PREDICTION"

2. **Resolve Predictions**:
   - Go to pending predictions
   - Tap "RESOLVE" when the period ends
   - Enter open and close prices
   - Get your score!

3. **View History**:
   - Switch to "HISTORY" tab
   - See all resolved predictions
   - Track your performance

4. **League Competition**:
   - Switch to "LEAGUE" tab
   - Copy your data to share
   - Import friends' data
   - View leaderboard rankings

## 🔧 Browser Requirements

- **iPhone**: Safari 11.3+ (iOS 11.3+)
- **iPad**: Safari 11.3+ (iPadOS 11.3+)
- **Android**: Chrome 68+ (with PWA support)

## 📱 Installation Requirements

- iOS 11.3 or later
- Safari browser
- Internet connection for initial setup
- Offline functionality available after installation

## 🎨 Customization

The app includes multiple themes and can be customized through the Settings tab:
- **Default Theme**: Cyan and purple gradient
- **Dark Theme**: Enhanced dark mode
- **Neon Theme**: Bright, vibrant colors

## 🔑 Alpha Vantage API Key

Live market data requires a personal Alpha Vantage API key:

1. Visit the [Alpha Vantage API portal](https://www.alphavantage.co/support/#api-key) and request a free key.
2. Open the **Settings** tab inside the app and paste the key into the **Alpha Vantage API Key** field.
3. Tap **Save Settings** to securely store the key in your browser's local storage.

For the current test build, a temporary key (`8HE88K05447IY34U`) ships preloaded so the live features work immediately. You can replace it with your own key in **Settings**, or clear the field to restore the bundled test key.

## 🔒 Privacy & Security

- All data stored locally on your device
- No personal information sent to external servers
- Stock data fetched from public APIs only
- No tracking or analytics

## 🆘 Troubleshooting

### Installation Issues
- Ensure you're using Safari (not Chrome or other browsers)
- Check that iOS version is 11.3 or later
- Try refreshing the page and attempting installation again

### Performance Issues
- Close other Safari tabs to free up memory
- Restart Safari if the app becomes unresponsive
- Check internet connection for real-time data

### Data Issues
- All data is stored locally - clearing Safari data will remove your predictions
- Export your data regularly to prevent loss
- Use the League tab to backup your progress

---

**Enjoy predicting stocks and competing with friends! 📈📱**
