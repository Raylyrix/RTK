"""
RTX Innovations - UI Components
Beautiful, responsive UI components with animations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
import pandas as pd
from datetime import datetime
import threading
import time

from config import UI_CONFIG, EMAIL_CONFIG, STATUS_COLUMNS
from google_auth import auth_manager

class LoginFrame(ctk.CTkFrame):
    """Beautiful login frame with animations"""
    
    def __init__(self, parent, on_success: Callable):
        super().__init__(parent, fg_color="transparent")
        self.on_success = on_success
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        # Center content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo and title
        logo_label = ctk.CTkLabel(
            content_frame,
            text="🚀",
            font=ctk.CTkFont(size=64)
        )
        logo_label.pack(pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            content_frame,
            text="RTX INNOVATIONS",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=UI_CONFIG['accent_color']
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text="Professional Email Marketing Platform",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Login form
        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=50)
        
        # Credentials file selection
        cred_label = ctk.CTkLabel(
            form_frame,
            text="Google API Credentials:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cred_label.pack(anchor="w", pady=(0, 5))
        
        cred_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cred_frame.pack(fill="x", pady=(0, 20))
        
        self.cred_path_var = tk.StringVar(value="credentials.json")
        cred_entry = ctk.CTkEntry(
            cred_frame,
            textvariable=self.cred_path_var,
            placeholder_text="Path to credentials.json",
            height=40
        )
        cred_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            cred_frame,
            text="📁 Browse",
            command=self.browse_credentials,
            width=100,
            height=40
        )
        browse_btn.pack(side="right")
        
        # Login button
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="🔑 Login with Google",
            command=self.login,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=UI_CONFIG['accent_color']
        )
        self.login_btn.pack(fill="x", pady=(20, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(form_frame)
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()
    
    def browse_credentials(self):
        """Browse for credentials file"""
        file_path = filedialog.askopenfilename(
            title="Select Google API Credentials",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.cred_path_var.set(file_path)
    
    def login(self):
        """Perform Google authentication"""
        credentials_path = self.cred_path_var.get().strip()
        
        if not credentials_path:
            self.show_status("Please select credentials file", "error")
            return
        
        # Show progress
        self.login_btn.configure(state="disabled", text="⏳ Authenticating...")
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0.3)
        
        # Start authentication in background
        threading.Thread(target=self._authenticate, args=(credentials_path,), daemon=True).start()
    
    def _authenticate(self, credentials_path: str):
        """Perform authentication in background thread"""
        try:
            # Simulate progress
            for i in range(3, 10):
                time.sleep(0.2)
                self.progress_bar.set(i / 10)
            
            # Perform actual authentication
            success, message = auth_manager.authenticate_account(credentials_path)
            
            if success:
                self.progress_bar.set(1.0)
                time.sleep(0.5)
                
                # Call success callback on main thread
                self.after(0, self._on_success)
            else:
                self.after(0, lambda: self._on_error(message))
                
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))
    
    def _on_success(self):
        """Handle successful authentication"""
        self.show_status("✅ Authentication successful!", "success")
        self.progress_bar.pack_forget()
        self.login_btn.configure(state="normal", text="🔑 Login with Google")
        
        # Call success callback
        self.on_success()
    
    def _on_error(self, error_message: str):
        """Handle authentication error"""
        self.show_status(f"❌ {error_message}", "error")
        self.progress_bar.pack_forget()
        self.login_btn.configure(state="normal", text="🔑 Login with Google")
    
    def show_status(self, message: str, status_type: str = "info"):
        """Show status message"""
        colors = {
            "success": UI_CONFIG['success_color'],
            "error": UI_CONFIG['error_color'],
            "warning": UI_CONFIG['warning_color'],
            "info": "gray"
        }
        
        self.status_label.configure(text=message, text_color=colors.get(status_type, "gray"))

class DashboardFrame(ctk.CTkFrame):
    """Main dashboard with overview and quick actions"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="Welcome to RTX Innovations!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        welcome_label.pack(anchor="w")
        
        # Stats grid
        self.create_stats_grid()
        
        # Quick actions
        self.create_quick_actions()
        
        # Recent activity
        self.create_recent_activity()
    
    def create_stats_grid(self):
        """Create statistics grid"""
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Grid layout
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stat cards
        stats = [
            ("📧 Total Emails", "0", "gray"),
            ("✅ Sent", "0", UI_CONFIG['success_color']),
            ("❌ Failed", "0", UI_CONFIG['error_color']),
            ("📊 Success Rate", "0%", UI_CONFIG['accent_color'])
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color="transparent")
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            value_label.pack()
            
            desc_label = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            desc_label.pack()
    
    def create_quick_actions(self):
        """Create quick action buttons"""
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        actions_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Action buttons grid
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        actions = [
            ("📊 Load Sheets", "Load Google Sheets data"),
            ("✉️ New Campaign", "Create email campaign"),
            ("📦 Manage Batches", "View batch status"),
            ("📈 View Analytics", "Check performance"),
            ("⚙️ Settings", "Configure application"),
            ("📋 View Logs", "Check activity logs")
        ]
        
        for i, (text, tooltip) in enumerate(actions):
            row = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                height=40,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25")
            )
            btn.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
    
    def create_recent_activity(self):
        """Create recent activity section"""
        activity_frame = ctk.CTkFrame(self)
        activity_frame.pack(fill="both", expand=True)
        
        activity_label = ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        activity_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Activity list
        activity_list = ctk.CTkTextbox(activity_frame, height=200)
        activity_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sample activities
        activities = [
            "✅ Successfully authenticated with Google",
            "📊 Loaded customer data from Google Sheets",
            "✉️ Sent test email campaign",
            "📦 Created batch 'Marketing Q1'",
            "📈 Updated analytics dashboard"
        ]
        
        for activity in activities:
            activity_list.insert("end", f"{activity}\n")
        
        activity_list.configure(state="disabled")

class SheetsFrame(ctk.CTkFrame):
    """Google Sheets integration frame"""
    
    def __init__(self, parent, sheets_handler):
        super().__init__(parent, fg_color="transparent")
        self.sheets_handler = sheets_handler
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sheets UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Google Sheets Integration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        # URL input
        url_frame = ctk.CTkFrame(self)
        url_frame.pack(fill="x", pady=(0, 20))
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Google Sheets URL:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        url_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        url_input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.url_var = tk.StringVar()
        url_entry = ctk.CTkEntry(
            url_input_frame,
            textvariable=self.url_var,
            placeholder_text="https://docs.google.com/spreadsheets/d/...",
            height=40
        )
        url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        load_btn = ctk.CTkButton(
            url_input_frame,
            text="🔄 Load",
            command=self.load_sheets,
            width=100,
            height=40
        )
        load_btn.pack(side="right")
        
        # Sheet selection
        sheet_frame = ctk.CTkFrame(self)
        sheet_frame.pack(fill="x", pady=(0, 20))
        
        sheet_label = ctk.CTkLabel(
            sheet_frame,
            text="Select Sheet:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sheet_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        sheet_select_frame = ctk.CTkFrame(sheet_frame, fg_color="transparent")
        sheet_select_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ctk.CTkComboBox(
            sheet_select_frame,
            variable=self.sheet_var,
            values=[],
            height=40
        )
        self.sheet_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        preview_btn = ctk.CTkButton(
            sheet_select_frame,
            text="👁️ Preview",
            command=self.preview_data,
            width=100,
            height=40
        )
        preview_btn.pack(side="right")
        
        # Data preview
        self.create_data_preview()
    
    def create_data_preview(self):
        """Create data preview section"""
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True)
        
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Data Preview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        preview_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Preview controls
        controls_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Search
        search_label = ctk.CTkLabel(controls_frame, text="Search:")
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.search_var,
            placeholder_text="Search data...",
            width=200
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        # Export button
        export_btn = ctk.CTkButton(
            controls_frame,
            text="💾 Export",
            command=self.export_data,
            width=80
        )
        export_btn.pack(side="right")
        
        # Data table
        self.create_data_table(preview_frame)
    
    def create_data_table(self, parent):
        """Create data table with scrollbars"""
        # Table container
        table_container = ctk.CTkFrame(parent)
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create treeview
        columns = ("Row", "Sample Data")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
    
    def load_sheets(self):
        """Load available sheets"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a Google Sheets URL")
            return
        
        try:
            sheets = self.sheets_handler.get_available_sheets(url)
            if sheets:
                self.sheet_combo.configure(values=sheets)
                self.sheet_combo.set(sheets[0])
                messagebox.showinfo("Success", f"Found {len(sheets)} sheets")
            else:
                messagebox.showerror("Error", "No sheets found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sheets: {e}")
    
    def preview_data(self):
        """Preview sheet data"""
        url = self.url_var.get().strip()
        sheet_name = self.sheet_var.get()
        
        if not url or not sheet_name:
            messagebox.showwarning("Warning", "Please select both URL and sheet")
            return
        
        try:
            # Load data
            success = self.sheets_handler.load_sheet_data(url, sheet_name)
            if success:
                self.display_data_preview()
                messagebox.showinfo("Success", "Data loaded successfully")
            else:
                messagebox.showerror("Error", "Failed to load data")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview data: {e}")
    
    def display_data_preview(self):
        """Display data in preview table"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get preview data
        preview_data = self.sheets_handler.get_data_preview(100)
        if preview_data is None:
            return
        
        # Add data to tree
        for i, row in preview_data.iterrows():
            # Sample first few columns
            sample_data = " | ".join([f"{col}: {val}" for col, val in row.head(3).items()])
            self.tree.insert("", "end", values=(f"Row {i+1}", sample_data))
    
    def export_data(self):
        """Export data to file"""
        if not self.sheets_handler.sheet_data:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if file_path:
            try:
                format_type = file_path.split('.')[-1]
                success = self.sheets_handler.export_data(file_path, format_type)
                if success:
                    messagebox.showinfo("Success", f"Data exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export data")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

# Additional frames will be implemented in the next part
class EmailFrame(ctk.CTkFrame):
    """Email campaigns frame"""
    def __init__(self, parent, sheets_handler):
        super().__init__(parent, fg_color="transparent")
        self.sheets_handler = sheets_handler
        self.setup_ui()
    
    def setup_ui(self):
        """Setup email UI"""
        title_label = ctk.CTkLabel(
            self,
            text="✉️ Email Campaigns",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self,
            text="Email campaigns functionality coming soon!",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        placeholder.pack(expand=True)

class BatchFrame(ctk.CTkFrame):
    """Batch management frame"""
    def __init__(self, parent, sheets_handler):
        super().__init__(parent, fg_color="transparent")
        self.sheets_handler = sheets_handler
        self.setup_ui()
    
    def setup_ui(self):
        """Setup batch UI"""
        title_label = ctk.CTkLabel(
            self,
            text="📦 Batch Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self,
            text="Batch management functionality coming soon!",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        placeholder.pack(expand=True)

class AnalyticsFrame(ctk.CTkFrame):
    """Analytics frame"""
    def __init__(self, parent, sheets_handler):
        super().__init__(parent, fg_color="transparent")
        self.sheets_handler = sheets_handler
        self.setup_ui()
    
    def setup_ui(self):
        """Setup analytics UI"""
        title_label = ctk.CTkLabel(
            self,
            text="📈 Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            self,
            text="Analytics functionality coming soon!",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        placeholder.pack(expand=True) 