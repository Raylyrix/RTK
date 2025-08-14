# How to Use the Credential Update Function

## Automatic Credential Management

The app now includes an automatic credential update function that allows you to easily update your Google OAuth credentials without restarting the application.

## Frontend Usage

### 1. Update Credentials Function

```javascript
// Example: Update credentials from a JSON file
async function updateCredentials(credentialsJson) {
    try {
        const result = await window.electronAPI.updateClientCredentials(credentialsJson);
        if (result.success) {
            console.log('Credentials updated successfully');
            // Now you can authenticate
            await authenticateWithGoogle();
        } else {
            console.error('Failed to update credentials:', result.error);
        }
    } catch (error) {
        console.error('Error updating credentials:', error);
    }
}

// Example: Load credentials from file and update
async function loadAndUpdateCredentials() {
    try {
        // Show file dialog to select credentials JSON
        const result = await window.electronAPI.showOpenDialog({
            properties: ['openFile'],
            filters: [
                { name: 'JSON Files', extensions: ['json'] }
            ]
        });
        
        if (!result.canceled && result.filePaths.length > 0) {
            const filePath = result.filePaths[0];
            const fileContent = await window.electronAPI.readJsonFile(filePath);
            
            if (fileContent.success) {
                await updateCredentials(fileContent.data);
            } else {
                console.error('Failed to read credentials file:', fileContent.error);
            }
        }
    } catch (error) {
        console.error('Error loading credentials:', error);
    }
}
```

### 2. Authentication After Credential Update

```javascript
// After updating credentials, authenticate
async function authenticateWithGoogle() {
    try {
        const result = await window.electronAPI.authenticateGoogle();
        if (result.success) {
            console.log('Authenticated successfully:', result.userEmail);
            // Initialize services
            await window.electronAPI.initializeGmailService();
            await window.electronAPI.initializeSheetsService();
        } else {
            console.error('Authentication failed:', result.error);
        }
    } catch (error) {
        console.error('Authentication error:', error);
    }
}
```

## Complete Workflow

1. **Download Desktop App Credentials** from Google Cloud Console
2. **Update Credentials** using `window.electronAPI.updateClientCredentials()`
3. **Authenticate** using `window.electronAPI.authenticateGoogle()`
4. **Initialize Services** for Gmail and Sheets

## Benefits

- ✅ **No app restart required** - Update credentials on the fly
- ✅ **Automatic token clearing** - Forces re-authentication with new credentials
- ✅ **Service reset** - Clears cached services to use new credentials
- ✅ **Better error handling** - Desktop app specific error messages
- ✅ **Automatic redirect URI handling** - No manual configuration needed

## Error Handling

The app now provides specific error messages for desktop applications:

- **"Unauthorized client"**: Make sure you're using Desktop application credentials
- **"Invalid client"**: Check your client ID and secret
- **"Access denied"**: Enable required APIs in Google Cloud Console
- **"Redirect URI mismatch"**: Should be handled automatically for desktop apps
