# AutoMailer Pro

A comprehensive automatic email sender with Google Sheets integration, scheduling capabilities, modern GUI interface, and **enhanced attachment support**.

### Download and Install (Desktop App)

Use the packaged Electron desktop app for the easiest setup on Windows and macOS.

- Go to Releases: https://github.com/Raylyrix/RTK/releases
- Download one of the installer files:
  - Windows (recommended): `RTX Innovations Setup <version>.exe`
  - macOS (recommended): `RTX Innovations-<version>.pkg`
  - macOS (alternative): `RTX Innovations-<version>.dmg` (drag and drop)

#### Windows (.exe)
1) Double‑click `RTX Innovations Setup <version>.exe`
2) Choose installation directory (default is fine) → Next → Install
3) Launch RTX Innovations from the desktop or Start menu
4) If SmartScreen shows a warning: click “More info” → “Run anyway”

#### macOS (.pkg) – recommended
1) Double‑click `RTX Innovations-<version>.pkg`
2) Continue → Agree → Install (enter password if prompted)
3) Open RTX Innovations from Applications or Spotlight
4) If blocked by Gatekeeper: right‑click the installer → Open → Open

#### macOS (.dmg) – alternative
1) Double‑click `RTX Innovations-<version>.dmg`
2) Drag “RTX Innovations” into Applications
3) Eject the disk image, then launch from Applications
4) If blocked by Gatekeeper: right‑click the app → Open → Open (or System Settings → Privacy & Security → Open Anyway)

#### First‑run setup
- Click “Login” → “Upload credentials” and select your Google OAuth `credentials.json`
- A browser window opens; sign in and approve Gmail/Sheets permissions
- On success, the app saves your token and returns to the app
- Paste your Google Sheets link and start your campaign

#### Auto‑updates
- The app checks for updates on launch and will prompt when a new version is available
- Click “Download” and then “Install” when prompted; the app restarts into the new version (e.g., v3)

#### Troubleshooting (quick)
- Windows: If blocked by SmartScreen → “More info” → “Run anyway”
- macOS: If blocked by Gatekeeper → right‑click → Open → Open (or Privacy & Security → Open Anyway)
- Network: Allow the app through firewalls/proxies to sign in and check for updates
- Logs: Use the in‑app Logs panel and follow on‑screen guidance

## Features

- 🔐 **Google Authentication** - Secure OAuth integration with Google APIs
- 📊 **Google Sheets Integration** - Direct data import from Google Sheets
- 📧 **Mass Email Sending** - Send personalized emails to thousands of recipients
- 🔄 **Batch Processing** - Configurable batch sizes to avoid API limits
- ⏰ **Email Scheduling** - Schedule emails for future delivery (once, daily, weekly, monthly)
- 🎯 **Smart Placeholders** - Use `((column_name))` to personalize emails with sheet data
- ⏱️ **Time Gaps** - Configurable delays between emails to prevent spam detection
- 📝 **Template Management** - Save and reuse email templates with attachments
- 📎 **Large File Attachments** - Support for multiple file attachments up to 25MB total
- 📊 **Progress Tracking** - Real-time progress monitoring during sending
- 📋 **Comprehensive Logging** - Detailed logging of all email activities
- 🎨 **Modern GUI** - Clean, intuitive interface built with tkinter
- ✅ **Enhanced Error Handling** - Improved placeholder processing and validation

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Google Cloud Project** with Gmail and Sheets APIs enabled
3. **Google API Credentials** (credentials.json file)

## Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd automailer-pro

# Or download and extract the ZIP file
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Or use the automated installer:**

```bash
python install.py
```

### 3. Set Up Google API Credentials

#### Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Sheets API

#### Step 2: Create OAuth 2.0 Credentials
1. Go to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Desktop application" as the application type
4. Download the credentials JSON file
5. Rename it to `credentials.json` and place it in the project root directory

#### Step 3: Configure OAuth Consent Screen
1. Go to "OAuth consent screen" in Google Cloud Console
2. Fill in the required information
3. Add your email address to test users (for development)

## Usage

### 1. Launch the Application

```bash
python main.py
```

**Or double-click:**
```bash
run_automailer.bat
```

### 2. Authenticate with Google

1. Click "Authenticate with Google" in the Main tab
2. Follow the browser authentication flow
3. Grant permissions for Gmail and Sheets access

### 3. Set Up Your Email Campaign

#### Load Google Sheets Data
1. Enter your Google Sheets URL in the "Google Sheets URL" field
2. Click "Load Sheets" to retrieve available sheets
3. Select the desired sheet from the dropdown
4. Click "Preview Data" to view your data

#### Create Email Template
1. Enter your email subject (can include placeholders like `((Name))`)
2. Write your email body using placeholders for personalization
   - Example: "Hello ((Name)), welcome to ((Company))!"
3. Click "Validate Placeholders" to ensure all placeholders match your sheet columns

#### Add Attachments (NEW!)
1. Click "Add Files" in the Attachments section
2. Select multiple files (documents, images, spreadsheets, etc.)
3. Monitor total file size (25MB Gmail limit)
4. Remove or clear attachments as needed

#### Configure Sending Options
1. Set batch size (default: 50 emails per batch)
2. Set time gap between emails (default: 5 seconds)
3. Click "Send Test Email" to test your template with attachments
4. Click "Send Emails" to start the bulk sending process

### 4. Schedule Email Campaigns

1. Go to the "Scheduler" tab
2. Enter a job name
3. Choose schedule type (once, daily, weekly, monthly)
4. Set the time and date
5. Click "Create Job"
6. Monitor scheduled jobs in the jobs list

### 5. Manage Templates

1. Go to the "Templates" tab
2. Save frequently used templates (including attachments!)
3. Load templates for reuse
4. Delete outdated templates

## Google Sheets Format

Your Google Sheets should have:
- **First row**: Column headers (e.g., Name, Email, Company)
- **Email column**: Must contain "email" or "mail" in the column name
- **Data rows**: One recipient per row

Example sheet structure:
```
Name          | Email               | Company      | Position
John Doe      | john@example.com    | Acme Corp    | Manager
Jane Smith    | jane@company.com    | Tech Inc     | Developer
```

## Placeholder System

Use double parentheses to create placeholders that will be replaced with data from your sheet:

- `((Name))` - Replaced with the Name column value
- `((Company))` - Replaced with the Company column value
- `((Position))` - Replaced with the Position column value

**Example Email Template:**
```
Subject: Welcome to our newsletter, ((Name))!

Hello ((Name)),

Thank you for your interest in our services. We noticed you work at ((Company)) as a ((Position)).

Please find our company brochure attached for your reference.

Best regards,
Marketing Team
```

## Attachment Support (NEW!)

### Supported Features:
- **Multiple Files**: Attach multiple files per email
- **File Types**: All file types supported (documents, images, archives, etc.)
- **Size Validation**: Automatic validation against Gmail's 25MB limit
- **Smart MIME Detection**: Proper MIME type detection for all file formats
- **Template Integration**: Save attachments with templates
- **Progress Monitoring**: Real-time feedback during attachment processing

### File Size Limits:
- **Per Email**: 25MB total (Gmail limit)
- **Individual Files**: No specific limit (within total)
- **Batch Processing**: Attachments included in all bulk emails

### Best Practices for Attachments:
1. **Optimize File Sizes**: Compress large files when possible
2. **Test First**: Always send a test email with attachments
3. **Monitor Logs**: Check logs for attachment processing errors
4. **Batch Considerations**: Larger attachments may slow down sending

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Ensure `credentials.json` is in the project root
   - Check the file path in Settings tab

2. **"Authentication failed"**
   - Check your Google Cloud Project setup
   - Ensure APIs are enabled
   - Verify OAuth consent screen configuration

3. **"No email column found"**
   - Ensure your sheet has a column with "email" or "mail" in the name
   - Check column headers in your Google Sheet

4. **"Quota exceeded" errors**
   - Reduce batch size
   - Increase time gaps between emails
   - Check Gmail API quotas in Google Cloud Console

5. **"Invalid placeholders" (FIXED!)**
   - Use the "Validate Placeholders" button
   - Improved error handling now provides better feedback
   - Placeholders are case-insensitive and handle empty values

6. **"Attachment too large"**
   - Check individual file sizes
   - Ensure total attachments don't exceed 25MB
   - Use file compression for large documents

7. **"Error fetching placeholder" (FIXED!)**
   - Enhanced placeholder processing with better error handling
   - Supports null/empty values in sheet data
   - Improved validation and debugging

### Email Limits

- **Gmail API Daily Quota**: 1 billion quota units per day
- **Sending Limits**: Up to 2000 emails per day for new accounts
- **Rate Limits**: 250 quota units per user per 100 seconds
- **Attachment Limit**: 25MB total per email

### Best Practices

1. **Start Small**: Test with a small batch first
2. **Use Time Gaps**: Add delays to avoid spam detection
3. **Monitor Logs**: Check logs for any issues
4. **Validate Data**: Always preview and validate before sending
5. **Backup Templates**: Save your successful templates with attachments
6. **Test Attachments**: Send test emails before bulk campaigns
7. **File Management**: Organize attachment files in accessible folders

## File Structure

```
automailer-pro/
├── main.py                 # Application entry point
├── main_gui.py            # Main GUI interface (enhanced with attachments)
├── config.py              # Configuration settings
├── google_auth.py         # Google authentication
├── sheets_handler.py      # Google Sheets integration (improved error handling)
├── email_sender.py        # Email sending functionality (enhanced with attachments)
├── scheduler.py           # Email scheduling system
├── requirements.txt       # Python dependencies
├── credentials.json       # Google API credentials (you provide)
├── token.json            # OAuth tokens (auto-generated)
├── templates/            # Saved email templates (with attachment support)
├── logs/                 # Application logs
├── run_automailer.bat    # Windows launcher
└── README.md             # This file
```

## What's New in This Version

### ✅ **Enhanced Attachment Support**
- Multiple file attachments per email
- Automatic file size validation (25MB Gmail limit)
- Smart MIME type detection
- Template integration with attachment saving
- Real-time size monitoring and warnings

### ✅ **Improved Placeholder Processing**
- Better error handling for invalid placeholders
- Support for null/empty values in sheet data
- Case-insensitive placeholder matching
- Enhanced validation with detailed feedback

### ✅ **Enhanced User Interface**
- New Attachments section in main tab
- File size monitoring with color-coded warnings
- Attachment management (add, remove, clear)
- Template system now includes attachment support

### ✅ **Better Error Handling**
- Comprehensive try-catch blocks
- Detailed error logging
- User-friendly error messages
- Graceful handling of edge cases

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs in the application's Logs tab
3. Ensure all dependencies are properly installed
4. Verify Google API credentials and permissions
5. Test with small batches and single attachments first

## License

This project is provided as-is for educational and productivity purposes.

## Version History

- **v1.1.0** - Enhanced attachment support and improved error handling
  - Large file attachment support (up to 25MB)
  - Multiple file attachments per email
  - Smart MIME type detection
  - Template system with attachment saving
  - Improved placeholder error handling
  - Better validation and user feedback

- **v1.0.0** - Initial release with core features
  - Google Sheets integration
  - Mass email sending
  - Scheduling system
  - Template management
  - Modern GUI interface 