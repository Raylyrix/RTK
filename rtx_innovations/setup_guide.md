# 🚀 RTX Innovations - Complete Setup Guide

**Step-by-step instructions to get RTX Innovations running on your system**

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Windows 10/11** (or macOS/Linux for development)
- ✅ **Internet connection** for Google API access
- ✅ **Google account** with Gmail and Google Sheets
- ✅ **Basic computer skills** (file management, web browsing)

## 🔑 Step 1: Google Cloud Console Setup

### 1.1 Access Google Cloud Console
1. **Open your web browser**
2. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
3. **Sign in** with your Google account

### 1.2 Create or Select Project
1. **Click the project dropdown** at the top of the page
2. **Click "New Project"** (or select existing project)
3. **Enter project name**: `RTX Innovations`
4. **Click "Create"** (or "Select" for existing)

### 1.3 Enable Required APIs
1. **Go to "APIs & Services" > "Library"**
2. **Search and enable these APIs one by one:**

#### **Gmail API**
- Search for "Gmail API"
- Click on "Gmail API"
- Click "Enable"

#### **Google Sheets API**
- Search for "Google Sheets API"
- Click on "Google Sheets API"
- Click "Enable"

#### **Google Drive API**
- Search for "Google Drive API"
- Click on "Google Drive API"
- Click "Enable"

### 1.4 Configure OAuth Consent Screen
1. **Go to "APIs & Services" > "OAuth consent screen"**
2. **Select "External"** user type
3. **Click "Create"**
4. **Fill in required information:**
   - **App name**: `RTX Innovations`
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. **Click "Save and Continue"**
6. **Skip "Scopes" section** (click "Save and Continue")
7. **Add test users** (your email address)
8. **Click "Save and Continue"**

### 1.5 Create OAuth 2.0 Credentials
1. **Go to "APIs & Services" > "Credentials"**
2. **Click "Create Credentials" > "OAuth 2.0 Client IDs"**
3. **Select "Desktop application"**
4. **Enter name**: `RTX Innovations Desktop`
5. **Click "Create"**
6. **Download the JSON file** (click download button)
7. **Rename the file** to `credentials.json`

## 📁 Step 2: Prepare Your System

### 2.1 Create Application Folder
1. **Open File Explorer**
2. **Navigate to** `C:\` or your preferred drive
3. **Create new folder**: `RTX Innovations`
4. **Open the folder**

### 2.2 Place Credentials File
1. **Copy `credentials.json`** from your Downloads
2. **Paste it** into the `RTX Innovations` folder
3. **Verify the file** is in the folder

### 2.3 Download RTX Innovations
1. **Download** `RTX_Innovations.exe` from the official source
2. **Place it** in the `RTX Innovations` folder
3. **Your folder should now contain:**
   ```
   RTX Innovations/
   ├── RTX_Innovations.exe
   └── credentials.json
   ```

## 🚀 Step 3: First Launch

### 3.1 Launch the Application
1. **Double-click** `RTX_Innovations.exe`
2. **Wait for the application** to load
3. **You should see** the login screen

### 3.2 Initial Authentication
1. **Click "🔑 Login with Google"**
2. **Browse and select** your `credentials.json` file
3. **Click "Login with Google"**
4. **A browser window** will open
5. **Sign in** with your Google account
6. **Grant permissions** when prompted
7. **Return to the application**

### 3.3 Verify Authentication
1. **Check the sidebar** - you should see your email
2. **Status should show** "Connected"
3. **You're now ready** to use RTX Innovations!

## 📊 Step 4: Prepare Your Google Sheets

### 4.1 Create or Open a Sheet
1. **Go to [Google Sheets](https://sheets.google.com)**
2. **Create new sheet** or open existing one
3. **Ensure you have edit permissions**

### 4.2 Organize Your Data
1. **First row should contain** column headers
2. **Include these recommended columns:**
   - `Name` - Recipient's name
   - `Email` - Recipient's email address
   - `Company` - Company name
   - `Position` - Job title
   - `Phone` - Phone number
   - `Notes` - Additional information

### 4.3 Sample Data Structure
```
| Name        | Email              | Company      | Position        | Phone          |
|-------------|-------------------|--------------|-----------------|----------------|
| John Doe    | john@company.com  | Tech Corp    | Developer       | +1-555-0123   |
| Jane Smith  | jane@company.com  | Design Inc   | Designer        | +1-555-0124   |
```

## ✉️ Step 5: Create Your First Email Campaign

### 5.1 Load Your Sheet Data
1. **In RTX Innovations, go to "📊 Google Sheets"**
2. **Paste your Google Sheets URL**
3. **Click "🔄 Load"**
4. **Select the sheet** from dropdown
5. **Click "👁️ Preview"** to see your data

### 5.2 Create Email Template
1. **Go to "✉️ Email Campaigns"**
2. **Enter subject**: `Welcome to our company, ((Name))!`
3. **Enter body** with placeholders:
   ```
   Dear ((Name)),
   
   Thank you for your interest in ((Company)). 
   We're excited to have you as a ((Position)).
   
   Best regards,
   Your Team
   ```

### 5.3 Configure Sending Options
1. **Set "From Email"** to your Gmail address
2. **Set "Display Name"** to your preferred name
3. **Check "📝 Include Gmail Signature"**
4. **Set "Batch Size"** to 25 (recommended)
5. **Set "Time Gap"** to 3 seconds

### 5.4 Send Test Email
1. **Click "🧪 Send Test Email"**
2. **Check your inbox** for the test email
3. **Verify placeholders** are replaced correctly
4. **Check signature** is included

### 5.5 Send Campaign
1. **Click "🚀 Send Emails"**
2. **Confirm the details** in the popup
3. **Monitor progress** in the status bar
4. **Check your Google Sheet** for status updates

## 📦 Step 6: Batch Management

### 6.1 Create Custom Batches
1. **Go to "📦 Batch Management"**
2. **Click "Create New Batch"**
3. **Enter batch name**: `Q1 Marketing Campaign`
4. **Select rows** to include in this batch
5. **Set batch parameters** (size, timing)

### 6.2 Monitor Batch Progress
1. **View batch status** in real-time
2. **Check individual email status** in your sheet
3. **Handle failed emails** with retry options
4. **Export batch reports** for analysis

## 📈 Step 7: Analytics and Reporting

### 7.1 View Campaign Statistics
1. **Go to "📈 Analytics"**
2. **Select date range** for your campaign
3. **View delivery rates** and success metrics
4. **Analyze performance** by batch or time period

### 7.2 Export Reports
1. **Click "Export Report"**
2. **Choose format**: Excel, CSV, or PDF
3. **Select data** to include
4. **Download and share** with your team

## 🔧 Step 8: Advanced Configuration

### 8.1 Custom Settings
1. **Go to "⚙️ Settings"**
2. **Adjust batch sizes** and time gaps
3. **Configure email templates** and signatures
4. **Set up auto-retry** for failed emails

### 8.2 Multiple Accounts
1. **Click account dropdown** in sidebar
2. **Click "Add Account"**
3. **Follow authentication** process for new account
4. **Switch between accounts** as needed

## 🚨 Troubleshooting

### **Common Issues and Solutions**

#### **"Authentication Failed"**
- ✅ **Check credentials file** is in the same folder
- ✅ **Verify Google APIs** are enabled
- ✅ **Check OAuth consent screen** is configured
- ✅ **Ensure test user** is added

#### **"Sheet Data Not Loading"**
- ✅ **Verify sheet URL** is correct
- ✅ **Check edit permissions** on the sheet
- ✅ **Ensure sheet contains** data
- ✅ **Check internet connection**

#### **"Emails Not Sending"**
- ✅ **Verify Gmail API** is enabled
- ✅ **Check daily sending limits** (Gmail: 500/day)
- ✅ **Ensure recipient emails** are valid
- ✅ **Check spam folder** for test emails

#### **"Application Crashes"**
- ✅ **Check system requirements** (Windows 10+)
- ✅ **Run as administrator** if needed
- ✅ **Check antivirus** isn't blocking the app
- ✅ **Reinstall the application**

### **Getting Help**
1. **Check the logs** in the application
2. **Review this setup guide** carefully
3. **Contact support** with specific error messages
4. **Include screenshots** of any error dialogs

## 📱 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10 (64-bit) or later
- **RAM**: 4 GB
- **Storage**: 500 MB free space
- **Internet**: Broadband connection

### **Recommended Requirements**
- **OS**: Windows 11 (64-bit)
- **RAM**: 8 GB or more
- **Storage**: 1 GB free space
- **Internet**: High-speed connection

## 🔒 Security Notes

### **Data Protection**
- **All data stays local** - nothing sent to external servers
- **Credentials encrypted** and stored securely
- **OAuth 2.0** for secure Google access
- **Session timeout** for security

### **Google Account Security**
- **Only necessary permissions** are requested
- **No access to** personal Gmail content
- **Revoke access** anytime in Google Account settings
- **Monitor API usage** in Google Cloud Console

## 📞 Support and Updates

### **Getting Updates**
- **Check for updates** in the application
- **Download latest version** from official source
- **Follow release notes** for new features

### **Contact Support**
- **Email**: support@rtxinnovations.com
- **Documentation**: [docs.rtxinnovations.com](https://docs.rtxinnovations.com)
- **Community**: [community.rtxinnovations.com](https://community.rtxinnovations.com)

---

## 🎉 Congratulations!

You've successfully set up RTX Innovations! 

**Next steps:**
1. **Explore the interface** and get familiar with features
2. **Create your first email campaign** with a small test group
3. **Experiment with different templates** and placeholders
4. **Set up batch management** for larger campaigns
5. **Monitor analytics** to optimize your campaigns

**Remember**: Start small, test thoroughly, and scale up gradually!

---

*Need help? Check the troubleshooting section above or contact our support team.*

**Happy email marketing! 🚀✉️** 