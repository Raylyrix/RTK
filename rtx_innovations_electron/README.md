## Distribution

- Windows: `npm run build-win` produces NSIS installer (.exe) and Portable .exe in `dist-builds/`
- macOS: `npm run build-mac` produces `.dmg` and `.zip`

## Login without Google Cloud credentials

Use a Gmail App Password:
- Open Login, enter Gmail and App Password, click Login.
- Optionally click Fetch Signature to auto-extract a signature from recent sent mail via IMAP.

Sheets access without credentials:
- Paste your Google Sheets URL. If not signed in with Google OAuth, app will try CSV export (share sheet as "Anyone with link"). Writes to sheet require OAuth.

# RTX Innovations - Professional Email Marketing Platform

A modern, desktop-based email marketing platform built with Electron, featuring Google Sheets integration, automated email campaigns, and a beautiful macOS-inspired interface.

## Features

- 🎨 **Modern UI/UX** - Beautiful macOS-inspired design with smooth animations
- 📊 **Google Sheets Integration** - Direct data import from Google Sheets
- 📧 **Email Campaigns** - Create and manage email marketing campaigns
- ⏰ **Scheduling** - Schedule campaigns for future delivery
- 📈 **Analytics** - Track campaign performance and subscriber growth
- 🔐 **Secure Authentication** - Google OAuth integration
- 📱 **Responsive Design** - Works seamlessly across different screen sizes
- 🚀 **Fast Performance** - Optimized for speed and efficiency

## Prerequisites

- **Node.js** (v16 or higher)
- **npm** (v8 or higher)
- **Google Cloud Project** with Gmail and Sheets APIs enabled

## Quick Start

### 1. Install Dependencies

```bash
cd rtx_innovations_electron
npm install
```

### 2. Development Mode

```bash
# Start in development mode with hot reloading
npm run dev

# Or use the Windows batch file
dev.bat
```

### 3. Build for Production

```bash
# Build for Windows
npm run build-win

# Or use the Windows batch file
build.bat
```

 

## Project Structure

```
rtx_innovations_electron/
├── src/
│   ├── js/                 # JavaScript modules
│   │   ├── app.js          # Main application logic
│   │   ├── auth.js         # Authentication handling
│   │   ├── sheets.js       # Google Sheets integration
│   │   ├── email.js        # Email functionality
│   │   └── ...            # Other modules
│   ├── styles/             # CSS files
│   │   ├── main.css        # Main styles
│   │   ├── animations.css  # Animation styles
│   │   └── components.css  # Component styles
│   ├── index.html          # Main HTML file
│   ├── main.js             # Electron main process
│   └── preload.js          # Preload script
├── assets/                 # Static assets
├── dist/                   # Webpack build output
├── dist-builds/            # Electron build output
├── webpack.config.js       # Webpack configuration
└── package.json            # Project configuration
```

## Development

### CSS Architecture

The app uses a modern CSS architecture with:

- **CSS Custom Properties** for consistent theming
- **Modular CSS** for component-based styling
- **Responsive design** principles
- **Smooth animations** and transitions

### JavaScript Architecture

- **ES6 Modules** for clean code organization
- **Class-based components** for maintainability
- **Event-driven architecture** for loose coupling
- **Error handling** throughout the application

### Building and Bundling

The app uses **Webpack** for:

- **CSS bundling** with style-loader and css-loader
- **JavaScript bundling** with ES6 module support
- **Asset optimization** for production builds
- **Hot reloading** for development

## Troubleshooting

### Common Issues

#### 1. CSS Not Rendering

**Problem**: App appears unstyled with default browser styling.

**Solutions**:
- Ensure CSS files are properly imported in `app.js`
- Check webpack configuration for CSS loaders
- Verify that `style-loader` and `css-loader` are installed
- Clear webpack cache: `rm -rf dist/ && npm run build`

#### 2. JavaScript Errors

**Problem**: "Cannot read properties of null (reading 'webContents')"

**Solutions**:
- Added null checks in `main.js` for all `mainWindow.webContents` calls
- Ensure proper window lifecycle management
- Check for proper error handling in menu actions

#### 3. Build Issues

**Problem**: Build fails or produces errors.

**Solutions**:
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Update dependencies: `npm update`
- Check for version conflicts in package.json
- Ensure all required dependencies are installed

#### 4. Development Server Issues

**Problem**: Hot reloading not working or server won't start.

**Solutions**:
- Check if port 3000 is available
- Restart the development server
- Clear webpack cache
- Check for file watching issues on Windows

### Debug Mode

To run the app in debug mode:

```bash
# Enable developer tools
npm run dev

# Or manually open dev tools in the app
# Press F12 or use View > Toggle Developer Tools
```

### Logs

Check the following for debugging:

1. **Browser Console** - Press F12 in the app
2. **Electron Logs** - Check terminal output
3. **Application Logs** - Check the logs tab in the app

## Production Build

### Windows

```bash
npm run build-win
```

This creates an installer in `dist-builds/` directory.

### macOS

```bash
npm run build-mac
```

### Linux

```bash
npm run build-linux
```

## Configuration

### Google API Setup

1. Create a Google Cloud Project
2. Enable Gmail and Sheets APIs
3. Create OAuth 2.0 credentials
4. Download `credentials.json` and place in the app directory

### Environment Variables

Create a `.env` file for environment-specific settings:

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
NODE_ENV=development
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs and console output
3. Create an issue with detailed information
4. Include screenshots and error messages

## Version History

- **v2.0.0** - Complete rewrite with modern architecture
  - Fixed CSS rendering issues
  - Added proper error handling
  - Improved build process
  - Enhanced UI/UX design

- **v1.0.0** - Initial release
  - Basic email marketing functionality
  - Google Sheets integration
  - Simple UI 