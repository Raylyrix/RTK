# Troubleshooting Guide - RTX Innovations Electron App

## Quick Fixes

### 1. Module Not Found Errors

**Problem**: `Cannot find module 'mini-css-extract-plugin'` or similar

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or install specific missing module
npm install mini-css-extract-plugin
```

### 2. Webpack Build Failures

**Problem**: Webpack fails to build or shows errors

**Solution**:
```bash
# Clear webpack cache
rm -rf dist/
npm run build

# Check for syntax errors in CSS/JS files
npm run build -- --verbose
```

### 3. Development Server Issues

**Problem**: `ERR_CONNECTION_REFUSED` or server won't start

**Solution**:
```bash
# Kill any existing processes on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Then restart
npm run dev
```

### 4. CSS Not Loading

**Problem**: App appears unstyled

**Solution**:
1. Check that CSS files are imported in `app.js`:
   ```javascript
   import '../styles/main.css';
   import '../styles/animations.css';
   import '../styles/components.css';
   ```

2. Verify webpack configuration has CSS loaders
3. Clear cache and rebuild:
   ```bash
   rm -rf dist/
   npm run build
   ```

### 5. Electron Window Issues

**Problem**: Window doesn't open or shows errors

**Solution**:
```bash
# Check if Electron is properly installed
npm list electron

# Reinstall Electron if needed
npm install electron@latest

# Run with verbose logging
npm run dev -- --verbose
```

## Common Error Messages

### "Cannot find module"
- **Cause**: Missing dependency
- **Fix**: `npm install <module-name>`

### "Port 3000 is already in use"
- **Cause**: Another process using the port
- **Fix**: Kill the process or change port in webpack.config.js

### "webpack-cli Failed to load config"
- **Cause**: Syntax error in webpack.config.js
- **Fix**: Check webpack configuration syntax

### "ERR_CONNECTION_REFUSED"
- **Cause**: Development server not running
- **Fix**: Ensure `npm run watch` is running before `npm run electron`

## Development Workflow

### Proper Development Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development**:
   ```bash
   npm run dev
   ```

3. **Alternative Method**:
   ```bash
   # Terminal 1: Start webpack watcher
   npm run watch
   
   # Terminal 2: Start Electron (after bundle is ready)
   npm run electron
   ```

### Debug Mode

Enable debug logging:
```bash
# Set debug environment variable
set DEBUG=rtx-innovations:*
npm run dev

# Or run with verbose output
npm run dev -- --verbose
```

### Production Build Issues

If production build fails:

```bash
# Clean build
rm -rf dist/ dist-builds/
npm run build
npm run build-win
```

## File Structure Verification

Ensure your project structure is correct:

```
rtx_innovations_electron/
├── src/
│   ├── js/
│   │   └── app.js          # Main entry point
│   ├── styles/
│   │   ├── main.css        # Main styles
│   │   ├── animations.css  # Animations
│   │   └── components.css  # Components
│   ├── index.html          # HTML template
│   ├── main.js             # Electron main process
│   └── preload.js          # Preload script
├── webpack.config.js       # Webpack configuration
└── package.json            # Dependencies
```

## Environment-Specific Issues

### Windows Issues

1. **Path Length Issues**:
   - Use shorter project paths
   - Enable long paths: `git config --system core.longpaths true`

2. **Permission Issues**:
   - Run as Administrator if needed
   - Check antivirus exclusions

3. **File Watching Issues**:
   - Increase file watcher limit: `fs.inotify.max_user_watches=524288`

### macOS Issues

1. **Code Signing**:
   - May need to allow unsigned apps
   - Go to System Preferences > Security & Privacy

2. **Permission Issues**:
   - Grant necessary permissions when prompted

### Linux Issues

1. **Missing Dependencies**:
   ```bash
   sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev
   ```

2. **Display Issues**:
   - Set `DISPLAY` environment variable
   - Use `--no-sandbox` flag if needed

## Performance Issues

### Slow Build Times

1. **Exclude node_modules from webpack**:
   ```javascript
   module: {
     rules: [
       {
         test: /\.js$/,
         exclude: /node_modules/,
         use: 'babel-loader'
       }
     ]
   }
   ```

2. **Use webpack cache**:
   ```javascript
   cache: {
     type: 'filesystem'
   }
   ```

### Memory Issues

1. **Increase Node.js memory limit**:
   ```bash
   node --max-old-space-size=4096 node_modules/.bin/webpack
   ```

2. **Optimize webpack configuration**:
   - Use `optimization.splitChunks`
   - Enable tree shaking

## Getting Help

### Debug Information

When reporting issues, include:

1. **System Information**:
   - OS version
   - Node.js version: `node --version`
   - npm version: `npm --version`

2. **Error Logs**:
   - Full error message
   - Stack trace
   - Console output

3. **Environment**:
   - Development or production
   - Steps to reproduce

### Useful Commands

```bash
# Check all dependencies
npm list

# Check for outdated packages
npm outdated

# Clear all caches
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Run with maximum verbosity
npm run dev -- --verbose --trace-warnings
```

## Prevention Tips

1. **Always use the same Node.js version** across team
2. **Lock dependency versions** in package-lock.json
3. **Test builds regularly** to catch issues early
4. **Use consistent development workflow**
5. **Keep dependencies updated** but test thoroughly

## Emergency Recovery

If everything breaks:

```bash
# Complete reset
rm -rf node_modules package-lock.json dist/ dist-builds/
npm install
npm run build
npm run dev
```

This should resolve most development environment issues. 