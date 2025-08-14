# Google API Setup Guide

This guide will walk you through setting up Google API credentials for AutoMailer Pro.

## Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter a project name (e.g., "AutoMailer Pro")
   - Click "Create"

3. **Select Your Project**
   - Make sure your new project is selected in the dropdown

## Step 2: Enable Required APIs

1. **Go to API Library**
   - In the left sidebar, click "APIs & Services" > "Library"

2. **Enable Gmail API**
   - Search for "Gmail API"
   - Click on "Gmail API"
   - Click "Enable"

3. **Enable Google Sheets API**
   - Search for "Google Sheets API"
   - Click on "Google Sheets API"
   - Click "Enable"

## Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - In the left sidebar, click "APIs & Services" > "OAuth consent screen"

2. **Choose User Type**
   - Select "External" (unless you have a Google Workspace account)
   - Click "Create"

3. **Fill in App Information**
   - **App name**: "AutoMailer Pro" (or your preferred name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
   - Leave other fields as default
   - Click "Save and Continue"

4. **Scopes (Step 2)**
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/spreadsheets.readonly`
   - Or simply click "Save and Continue" to skip this step

5. **Test Users (Step 3)**
   - Click "Add Users"
   - Add your Gmail address that you'll use for sending emails
   - Add any other email addresses you want to test with
   - Click "Save and Continue"

6. **Summary (Step 4)**
   - Review your settings
   - Click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services" > "Credentials"

2. **Create OAuth 2.0 Client ID**
   - Click "Create Credentials" > "OAuth 2.0 Client ID"

3. **Configure OAuth Client**
   - **Application type**: Select "Desktop application"
   - **Name**: "AutoMailer Pro Desktop Client" (or your preferred name)
   - Click "Create"

4. **Download Credentials**
   - A popup will appear with your client ID and secret
   - Click "Download JSON"
   - Save the file as `credentials.json` in your AutoMailer Pro folder

## Step 5: Important Security Notes

### For Development/Personal Use:
- Your app will show as "unverified" - this is normal for personal projects
- You can continue past the warning screen by clicking "Advanced" > "Go to [App Name] (unsafe)"

### For Production Use:
- You'll need to verify your app with Google
- This requires additional documentation and review
- See: https://support.google.com/cloud/answer/9110914

## Step 6: Testing Your Setup

1. **Run AutoMailer Pro**
   - Launch the application: `python main.py`

2. **Authenticate**
   - Click "Authenticate with Google"
   - Your browser will open

3. **Grant Permissions**
   - Sign in with your Google account
   - You may see a warning about the app being unverified
   - Click "Advanced" > "Go to [App Name] (unsafe)"
   - Grant the requested permissions

4. **Verify Success**
   - The app should show "Status: Authenticated as [your-email]"

## Troubleshooting

### Common Issues:

1. **"This app isn't verified"**
   - Click "Advanced" > "Go to [App Name] (unsafe)"
   - This is normal for development/personal use

2. **"Access blocked: This app's request is invalid"**
   - Check that you've enabled the correct APIs
   - Verify your OAuth consent screen is configured

3. **"The OAuth client was not found"**
   - Ensure your `credentials.json` file is in the correct location
   - Check that the file wasn't corrupted during download

4. **"Quota exceeded"**
   - Check your API quotas in Google Cloud Console
   - Wait for quotas to reset (usually daily)

### API Quotas:

- **Gmail API**: 1 billion quota units per day
- **Sheets API**: 300 requests per minute per project
- **Rate limits**: Apply to prevent abuse

## File Locations:

After setup, you should have:
```
automailer-pro/
├── credentials.json       # Downloaded from Google Cloud Console
├── token.json            # Auto-generated after first authentication
└── ... (other files)
```

## Security Best Practices:

1. **Keep credentials.json secure** - Don't share or commit to version control
2. **Use specific scopes** - Only request permissions you need
3. **Monitor API usage** - Check your quotas regularly
4. **Rotate credentials** - Refresh periodically for security

## Need Help?

- **Google Cloud Console Help**: https://cloud.google.com/support
- **Gmail API Documentation**: https://developers.google.com/gmail/api
- **Google Sheets API Documentation**: https://developers.google.com/sheets/api

Remember: The initial setup might seem complex, but you only need to do it once! 