# 🚀 RTX Innovations v2.0.0

**Professional Email Marketing & Automation Platform**

A beautiful, feature-rich email marketing application with Google Sheets integration, designed with inspiration from macOS software aesthetics.

## ✨ Features

### 🔐 **Multi-Account Authentication**
- **Secure Google OAuth 2.0** integration
- **Multiple account support** - switch between different Google accounts
- **Session management** with automatic timeout
- **Account lockout protection** for security

### 📊 **Advanced Google Sheets Integration**
- **Full CRUD operations** - read, write, and edit sheet data
- **Real-time data preview** with all rows and columns visible
- **Automatic status tracking** columns for email campaigns
- **Smart placeholder detection** with fuzzy matching
- **Data export** in multiple formats (Excel, CSV, JSON)

### ✉️ **Professional Email Campaigns**
- **Personalized emails** using sheet data placeholders
- **Gmail signature integration** - automatically includes your signature
- **Verified send-as aliases** - send from multiple email addresses
- **Large file attachments** up to 25MB per email
- **HTML and plain text** email support

### 📦 **Smart Batch Management**
- **Custom batch labeling** - organize emails by campaign, region, etc.
- **Batch status tracking** - monitor progress in real-time
- **Automatic retry logic** for failed emails
- **Configurable batch sizes** and time gaps
- **Concurrent batch processing**

### 📈 **Real-Time Analytics**
- **Campaign performance metrics**
- **Email delivery statistics**
- **Open and click tracking**
- **Bounce and unsubscribe monitoring**
- **Exportable reports**

### 🎨 **Beautiful macOS-Inspired UI**
- **Modern dark theme** with smooth animations
- **Responsive design** that adapts to window size
- **Intuitive navigation** with sidebar menu
- **Professional color scheme** and typography
- **Smooth transitions** and hover effects

## 🚀 Quick Start

### 1. **Installation**

#### Option A: Run from Source
```bash
# Clone the repository
git clone <repository-url>
cd rtx_innovations

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

#### Option B: Use Executable (Recommended for Users)
1. Download `RTX_Innovations.exe` from the releases
2. Extract to a folder
3. Double-click to run

### 2. **Google API Setup**

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select existing one
3. **Enable APIs:**
   - Gmail API
   - Google Sheets API
   - Google Drive API
4. **Create OAuth 2.0 credentials:**
   - Application type: Desktop application
   - Download the `credentials.json` file
5. **Place `credentials.json` in the same folder as the executable**

### 3. **First Launch**

1. **Launch RTX Innovations**
2. **Click "🔑 Login with Google"**
3. **Select your credentials file**
4. **Complete OAuth authentication**
5. **Start using the application!**

## 📖 User Guide

### **Dashboard**
- **Overview statistics** of your email campaigns
- **Quick action buttons** for common tasks
- **Recent activity** log

### **Google Sheets Integration**
1. **Enter your Google Sheets URL**
2. **Select the sheet** to work with
3. **Preview all data** with full row/column visibility
4. **Edit column labels** and organize your data
5. **Export data** in various formats

### **Email Campaigns**
1. **Load your sheet data**
2. **Create email template** with placeholders like `((Name))`, `((Company))`
3. **Configure sender details** and Gmail signature
4. **Add attachments** (up to 25MB)
5. **Set batch parameters** and time gaps
6. **Send or schedule** your campaign

### **Batch Management**
1. **Create custom batch labels** (e.g., "Q1 Marketing", "VIP Customers")
2. **Select specific rows** for each batch
3. **Monitor batch progress** in real-time
4. **Track email status** for each recipient
5. **Retry failed emails** automatically

### **Status Tracking**
The application automatically adds these columns to your Google Sheets:
- **Email Status**: Sent, Failed, Pending
- **Sent Date**: When email was sent
- **Sent Time**: Exact time of sending
- **Batch ID**: Which batch the email belongs to
- **Attempts**: Number of sending attempts
- **Error Message**: Details if sending failed
- **Tracking ID**: Unique identifier for each email

## ⚙️ Configuration

### **Email Settings**
```python
EMAIL_CONFIG = {
    'default_batch_size': 25,        # Emails per batch
    'max_batch_size': 100,          # Maximum batch size
    'default_time_gap': 3,          # Seconds between emails
    'max_attachment_size': 25MB,    # Maximum file size
    'retry_attempts': 3,            # Retry failed emails
}
```

### **UI Settings**
```python
UI_CONFIG = {
    'theme': 'dark',                # dark, light, system
    'accent_color': '#007AFF',      # iOS Blue
    'animation_duration': 300,      # Milliseconds
    'window_width': 1400,          # Default width
    'window_height': 900,          # Default height
}
```

## 🔧 Advanced Features

### **Custom Placeholder Matching**
- **Exact match**: `((Email))` matches column "Email"
- **Case-insensitive**: `((email))` matches "Email" or "EMAIL"
- **Partial match**: `((company name))` matches "Company Name" or "Company"

### **Smart Data Processing**
- **Automatic column detection** for email addresses
- **Data validation** and error handling
- **Real-time updates** to Google Sheets
- **Backup and restore** functionality

### **Performance Optimization**
- **Caching system** for faster data access
- **Background processing** for large datasets
- **Memory management** for optimal performance
- **Multi-threading** for concurrent operations

## 📁 Project Structure

```
rtx_innovations/
├── src/                    # Source code
│   ├── main.py            # Main application entry point
│   ├── rtx_app.py         # Main application class
│   ├── ui_components.py   # UI components and frames
│   ├── google_auth.py     # Google authentication
│   ├── sheets_handler.py  # Google Sheets integration
│   └── config.py          # Configuration settings
├── assets/                 # Images, icons, and assets
├── build/                  # Build outputs and executables
├── templates/              # Email templates
├── logs/                   # Application logs
├── exports/                # Exported data files
├── cache/                  # Temporary files and tokens
├── requirements.txt        # Python dependencies
├── build_app.py           # Build script for executable
└── README.md              # This file
```

## 🛠️ Development

### **Prerequisites**
- Python 3.8+
- pip package manager
- Google Cloud Console access

### **Development Setup**
```bash
# Clone repository
git clone <repository-url>
cd rtx_innovations

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python src/main.py
```

### **Building Executable**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_app.py
```

## 🐛 Troubleshooting

### **Common Issues**

#### **"No module named 'customtkinter'"**
```bash
pip install customtkinter
```

#### **"Google API credentials not found"**
- Ensure `credentials.json` is in the same folder as the executable
- Check that the file path is correct
- Verify the credentials file is valid

#### **"Authentication failed"**
- Check your internet connection
- Ensure Google APIs are enabled in Cloud Console
- Verify OAuth consent screen is configured
- Check if your account has access to the APIs

#### **"Sheet data not loading"**
- Verify the Google Sheets URL is correct
- Check that you have edit permissions on the sheet
- Ensure the sheet contains data
- Check your internet connection

### **Log Files**
- Application logs are stored in the `logs/` directory
- Check `email_sender.log` for email-related issues
- Check `application.log` for general application issues

## 📞 Support

### **Getting Help**
1. **Check the logs** for error details
2. **Review this README** for common solutions
3. **Check the setup guide** for configuration help
4. **Contact support** with detailed error information

### **Reporting Issues**
When reporting issues, please include:
- **Application version** (shown in title bar)
- **Error message** (if any)
- **Steps to reproduce** the issue
- **Log files** (if available)
- **System information** (OS, Python version)

## 🔒 Security & Privacy

### **Data Protection**
- **Local storage only** - no data sent to external servers
- **Encrypted credentials** storage
- **Secure OAuth 2.0** authentication
- **Session timeout** for security

### **Google API Access**
- **Minimal permissions** - only what's needed
- **Read-only access** to sheets (unless editing)
- **Send-only access** to Gmail
- **No data mining** or tracking

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google APIs** for Gmail and Sheets integration
- **CustomTkinter** for the beautiful UI framework
- **Pandas** for powerful data manipulation
- **Open source community** for various supporting libraries

## 🚀 Future Roadmap

### **Version 2.1** (Coming Soon)
- **Advanced analytics dashboard**
- **Email template designer**
- **A/B testing capabilities**
- **Advanced scheduling options**

### **Version 2.2** (Planned)
- **Multi-language support**
- **Cloud synchronization**
- **Team collaboration features**
- **API for third-party integrations**

---

**Made with ❤️ by RTX Innovations Team**

*Transform your email marketing with professional automation and beautiful design.* 