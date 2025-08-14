"""
RTX Innovations - Professional Email Marketing Platform
Beautiful macOS-inspired UI with animations and professional features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
import time
import json
from pathlib import Path
from datetime import datetime

from config import UI_CONFIG, APP_NAME, APP_VERSION, APP_DESCRIPTION
from google_auth import auth_manager
from sheets_handler import SheetsHandler
from ui_components import (
    LoginFrame, DashboardFrame, SheetsFrame, 
    EmailFrame, BatchFrame, AnalyticsFrame, SettingsFrame
)

class RTXInnovationsApp:
    """Main RTX Innovations application with beautiful UI"""
    
    def __init__(self):
        # Configure customtkinter
        ctk.set_appearance_mode(UI_CONFIG['theme'])
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{UI_CONFIG['window_width']}x{UI_CONFIG['window_height']}")
        self.root.minsize(UI_CONFIG['min_width'], UI_CONFIG['min_height'])
        
        # Set window icon if available
        self.set_window_icon()
        
        # Center window
        self.center_window()
        
        # Initialize components
        self.sheets_handler = SheetsHandler()
        self.current_frame = None
        self.frame_history = []
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        
        # Start authentication check
        self.check_authentication()
        
        # Setup auto-save
        self.setup_auto_save()
    
    def set_window_icon(self):
        """Set window icon if available"""
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
    
    def center_window(self):
        """Center the window on screen with animation"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Add entrance animation
        self.root.attributes('-alpha', 0.0)
        self.root.deiconify()
        self.animate_entrance()
    
    def animate_entrance(self):
        """Animate window entrance"""
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.1
                self.root.attributes('-alpha', alpha)
                self.root.after(20, lambda: fade_in(alpha))
        
        fade_in()
    
    def setup_ui(self):
        """Setup the main UI components with beautiful design"""
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
        # Create floating action button
        self.create_floating_action_button()
    
    def create_sidebar(self):
        """Create beautiful sidebar navigation"""
        # Sidebar frame with gradient effect
        self.sidebar = ctk.CTkFrame(
            self.root, 
            width=280, 
            corner_radius=0,
            fg_color=("gray90", "gray15")
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # App logo and title with beautiful design
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=25, pady=(30, 20), sticky="ew")
        
        # App logo (emoji for now, can be replaced with actual logo)
        logo_label = ctk.CTkLabel(
            logo_frame, 
            text="🚀", 
            font=ctk.CTkFont(size=48),
            text_color=UI_CONFIG['accent_color']
        )
        logo_label.pack(pady=(0, 10))
        
        # App title with gradient effect
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack()
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="RTX", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=UI_CONFIG['accent_color']
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="INNOVATIONS", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="gray"
        )
        subtitle_label.pack(side="left", padx=(8, 0))
        
        # Version info
        version_label = ctk.CTkLabel(
            logo_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack()
        
        # Navigation buttons with beautiful design
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠 Dashboard", "dashboard", self.show_dashboard, "Main overview and statistics"),
            ("📊 Google Sheets", "sheets", self.show_sheets, "Manage and edit sheet data"),
            ("✉️ Email Campaigns", "email", self.show_email, "Create and send email campaigns"),
            ("📦 Batch Management", "batch", self.show_batch, "Organize and track email batches"),
            ("📈 Analytics", "analytics", self.show_analytics, "View detailed campaign analytics"),
            ("⚙️ Settings", "settings", self.show_settings, "Configure application settings"),
        ]
        
        for i, (text, key, command, tooltip) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                height=45,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                font=ctk.CTkFont(size=15, weight="normal"),
                corner_radius=12
            )
            btn.grid(row=i, column=0, padx=20, pady=6, sticky="ew")
            self.nav_buttons[key] = btn
            
            # Add tooltip
            self.create_tooltip(btn, tooltip)
        
        # Account section at bottom with beautiful design
        self.create_account_section()
    
    def create_account_section(self):
        """Create beautiful account management section"""
        account_frame = ctk.CTkFrame(
            self.sidebar, 
            fg_color=("gray85", "gray20"),
            corner_radius=15
        )
        account_frame.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        # Account info
        self.account_label = ctk.CTkLabel(
            account_frame,
            text="Not authenticated",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="gray"
        )
        self.account_label.pack(pady=(15, 10))
        
        # Account buttons
        btn_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.login_btn = ctk.CTkButton(
            btn_frame,
            text="🔑 Login",
            command=self.show_login,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=UI_CONFIG['accent_color'],
            corner_radius=10
        )
        self.login_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.logout_btn = ctk.CTkButton(
            btn_frame,
            text="🚪 Logout",
            command=self.logout,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=UI_CONFIG['error_color'],
            corner_radius=10
        )
        self.logout_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Initially hide logout button
        self.logout_btn.pack_forget()
    
    def create_main_content(self):
        """Create the main content area with beautiful design"""
        self.main_frame = ctk.CTkFrame(
            self.root, 
            fg_color=("gray95", "gray10"),
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Show login frame initially
        self.show_login()
    
    def create_status_bar(self):
        """Create beautiful status bar"""
        self.status_bar = ctk.CTkFrame(
            self.root, 
            height=35, 
            corner_radius=0,
            fg_color=("gray90", "gray15")
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar, 
            width=200,
            progress_color=UI_CONFIG['accent_color']
        )
        self.progress_bar.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Hide initially
        
        # Connection status
        self.connection_status = ctk.CTkLabel(
            self.status_bar,
            text="● Disconnected",
            font=ctk.CTkFont(size=12),
            text_color=UI_CONFIG['error_color']
        )
        self.connection_status.grid(row=0, column=2, padx=(0, 15), pady=8, sticky="e")
    
    def create_floating_action_button(self):
        """Create floating action button for quick actions"""
        self.fab = ctk.CTkButton(
            self.root,
            text="+",
            width=60,
            height=60,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=UI_CONFIG['accent_color'],
            corner_radius=30,
            command=self.show_quick_actions
        )
        
        # Position FAB (initially hidden)
        self.fab.place(relx=0.95, rely=0.85, anchor="center")
        self.fab.place_forget()
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip, 
                text=text, 
                justify='left',
                background="#ffffe0", 
                relief='solid', 
                borderwidth=1,
                font=("Segoe UI", "8", "normal")
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Campaign", command=self.new_campaign)
        file_menu.add_command(label="Open Campaign", command=self.open_campaign)
        file_menu.add_command(label="Save Campaign", command=self.save_campaign)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self.show_settings)
        edit_menu.add_command(label="Account Settings", command=self.show_account_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Batch Manager", command=self.show_batch)
        tools_menu.add_command(label="Analytics Dashboard", command=self.show_analytics)
        tools_menu.add_command(label="Logs Viewer", command=self.show_logs)
        tools_menu.add_command(label="Template Manager", command=self.show_templates)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="Video Tutorials", command=self.show_tutorials)
        help_menu.add_command(label="Support", command=self.show_support)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_campaign())
        self.root.bind('<Control-o>', lambda e: self.open_campaign())
        self.root.bind('<Control-s>', lambda e: self.save_campaign())
        self.root.bind('<Control-e>', lambda e: self.export_data())
        self.root.bind('<F1>', lambda e: self.show_docs())
        self.root.bind('<F5>', lambda e: self.refresh_current_view())
    
    def setup_auto_save(self):
        """Setup auto-save functionality"""
        def auto_save():
            if self.current_frame and hasattr(self.current_frame, 'auto_save'):
                self.current_frame.auto_save()
            self.root.after(300000, auto_save)  # Every 5 minutes
        
        self.root.after(300000, auto_save)
    
    def check_authentication(self):
        """Check if user is already authenticated"""
        if auth_manager.get_current_account():
            self.update_account_display()
            self.show_dashboard()
        else:
            self.show_login()
    
    def update_account_display(self):
        """Update account display information"""
        account = auth_manager.get_current_account()
        if account:
            self.account_label.configure(
                text=f"👤 {account.email}",
                text_color="white"
            )
            self.login_btn.pack_forget()
            self.logout_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
            self.connection_status.configure(
                text="● Connected",
                text_color=UI_CONFIG['success_color']
            )
            self.fab.place(relx=0.95, rely=0.85, anchor="center")
        else:
            self.account_label.configure(
                text="Not authenticated",
                text_color="gray"
            )
            self.logout_btn.pack_forget()
            self.login_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.connection_status.configure(
                text="● Disconnected",
                text_color=UI_CONFIG['error_color']
            )
            self.fab.place_forget()
    
    def show_frame(self, frame_class, *args, **kwargs):
        """Show a specific frame with beautiful animation"""
        # Store frame history
        if self.current_frame:
            self.frame_history.append(self.current_frame)
            if len(self.frame_history) > 10:  # Keep only last 10 frames
                self.frame_history.pop(0)
        
        # Hide current frame with fade out
        if self.current_frame:
            self.animate_frame_transition(self.current_frame, "out")
        
        # Create and show new frame
        self.current_frame = frame_class(self.main_frame, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)
        
        # Animate frame entrance
        self.animate_frame_transition(self.current_frame, "in")
        
        # Update navigation
        self.update_navigation()
        
        # Update status
        self.update_status(f"Showing {frame_class.__name__}")
    
    def animate_frame_transition(self, frame, direction):
        """Animate frame transition"""
        if direction == "out":
            # Fade out animation
            def fade_out(alpha=1.0):
                if alpha > 0.0:
                    alpha -= 0.1
                    frame.configure(fg_color=("gray95", "gray10"))
                    self.root.after(20, lambda: fade_out(alpha))
                else:
                    frame.pack_forget()
            fade_out()
        else:
            # Fade in animation
            frame.configure(fg_color=("gray95", "gray10"))
    
    def update_navigation(self):
        """Update navigation button states"""
        current_frame_name = self.current_frame.__class__.__name__.lower().replace('frame', '')
        
        for key, btn in self.nav_buttons.items():
            if key == current_frame_name:
                btn.configure(fg_color=UI_CONFIG['accent_color'])
            else:
                btn.configure(fg_color="transparent")
    
    def show_login(self):
        """Show login frame"""
        self.show_frame(LoginFrame, self.on_login_success)
    
    def show_dashboard(self):
        """Show dashboard frame"""
        self.show_frame(DashboardFrame)
    
    def show_sheets(self):
        """Show Google Sheets frame"""
        if not auth_manager.get_current_account():
            messagebox.showwarning("Authentication Required", "Please login first")
            return
        self.show_frame(SheetsFrame, self.sheets_handler)
    
    def show_email(self):
        """Show email campaigns frame"""
        if not auth_manager.get_current_account():
            messagebox.showwarning("Authentication Required", "Please login first")
            return
        self.show_frame(EmailFrame, self.sheets_handler)
    
    def show_batch(self):
        """Show batch management frame"""
        if not auth_manager.get_current_account():
            messagebox.showwarning("Authentication Required", "Please login first")
            return
        self.show_frame(BatchFrame, self.sheets_handler)
    
    def show_analytics(self):
        """Show analytics frame"""
        if not auth_manager.get_current_account():
            messagebox.showwarning("Authentication Required", "Please login first")
            return
        self.show_frame(AnalyticsFrame, self.sheets_handler)
    
    def show_settings(self):
        """Show settings frame"""
        self.show_frame(SettingsFrame)
    
    def on_login_success(self):
        """Handle successful login"""
        self.update_account_display()
        self.show_dashboard()
        self.update_status("Login successful")
        
        # Show welcome message
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message after login"""
        welcome_window = ctk.CTkToplevel(self.root)
        welcome_window.title("Welcome to RTX Innovations!")
        welcome_window.geometry("500x300")
        welcome_window.transient(self.root)
        welcome_window.grab_set()
        
        # Center the window
        welcome_window.update_idletasks()
        x = (welcome_window.winfo_screenwidth() // 2) - (welcome_window.winfo_width() // 2)
        y = (welcome_window.winfo_screenheight() // 2) - (welcome_window.winfo_height() // 2)
        welcome_window.geometry(f"+{x}+{y}")
        
        # Welcome content
        welcome_label = ctk.CTkLabel(
            welcome_window,
            text="🎉 Welcome to RTX Innovations!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=UI_CONFIG['accent_color']
        )
        welcome_label.pack(pady=(30, 20))
        
        message_label = ctk.CTkLabel(
            welcome_window,
            text="You're now ready to create amazing email campaigns!\n\nStart by connecting your Google Sheets or creating a new campaign.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        message_label.pack(pady=(0, 30))
        
        # Quick start buttons
        btn_frame = ctk.CTkFrame(welcome_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)
        
        sheets_btn = ctk.CTkButton(
            btn_frame,
            text="📊 Connect Sheets",
            command=lambda: [welcome_window.destroy(), self.show_sheets()],
            height=35
        )
        sheets_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        campaign_btn = ctk.CTkButton(
            btn_frame,
            text="✉️ New Campaign",
            command=lambda: [welcome_window.destroy(), self.show_email()],
            height=35
        )
        campaign_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))
    
    def logout(self):
        """Logout current user"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            auth_manager.logout_account()
            self.update_account_display()
            self.show_login()
            self.update_status("Logged out")
            
            # Clear frame history
            self.frame_history.clear()
    
    def show_quick_actions(self):
        """Show quick actions menu"""
        # Create quick actions popup
        actions_window = ctk.CTkToplevel(self.root)
        actions_window.title("Quick Actions")
        actions_window.geometry("300x400")
        actions_window.transient(self.root)
        actions_window.grab_set()
        
        # Center the window
        actions_window.update_idletasks()
        x = (actions_window.winfo_screenwidth() // 2) - (actions_window.winfo_width() // 2)
        y = (actions_window.winfo_screenheight() // 2) - (actions_window.winfo_height() // 2)
        actions_window.geometry(f"+{x}+{y}")
        
        # Quick actions
        actions = [
            ("📊 Load Sheets", self.show_sheets),
            ("✉️ New Campaign", self.show_email),
            ("📦 Manage Batches", self.show_batch),
            ("📈 View Analytics", self.show_analytics),
            ("⚙️ Settings", self.show_settings),
            ("💾 Save Campaign", self.save_campaign),
            ("📤 Export Data", self.export_data),
        ]
        
        for text, command in actions:
            btn = ctk.CTkButton(
                actions_window,
                text=text,
                command=lambda cmd=command: [actions_window.destroy(), cmd()],
                height=40,
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
    
    def show_progress(self, show: bool = True):
        """Show/hide progress bar"""
        if show:
            self.progress_bar.grid()
        else:
            self.progress_bar.grid_remove()
    
    def update_progress(self, value: float):
        """Update progress bar value"""
        self.progress_bar.set(value)
    
    # Menu command implementations
    def new_campaign(self):
        """Create new campaign"""
        self.show_email()
    
    def open_campaign(self):
        """Open existing campaign"""
        # TODO: Implement campaign loading
        messagebox.showinfo("Open Campaign", "Campaign loading coming soon!")
    
    def save_campaign(self):
        """Save current campaign"""
        if self.current_frame and hasattr(self.current_frame, 'save_campaign'):
            self.current_frame.save_campaign()
        else:
            messagebox.showinfo("Save Campaign", "No campaign to save")
    
    def export_data(self):
        """Export data functionality"""
        if self.current_frame and hasattr(self.current_frame, 'export_data'):
            self.current_frame.export_data()
        else:
            messagebox.showinfo("Export", "Export functionality available in data views")
    
    def import_data(self):
        """Import data functionality"""
        # TODO: Implement import functionality
        messagebox.showinfo("Import", "Import functionality coming soon!")
    
    def show_account_settings(self):
        """Show account settings"""
        # TODO: Implement account settings
        messagebox.showinfo("Account Settings", "Account settings coming soon!")
    
    def show_logs(self):
        """Show logs dialog"""
        # TODO: Implement logs dialog
        messagebox.showinfo("Logs", "Logs viewer coming soon!")
    
    def show_templates(self):
        """Show template manager"""
        # TODO: Implement template manager
        messagebox.showinfo("Templates", "Template manager coming soon!")
    
    def show_tutorials(self):
        """Show video tutorials"""
        # TODO: Implement tutorial viewer
        messagebox.showinfo("Tutorials", "Video tutorials coming soon!")
    
    def show_support(self):
        """Show support information"""
        support_text = f"""
{APP_NAME} Support

📧 Email: support@rtxinnovations.com
🌐 Website: {UI_CONFIG.get('website', 'https://rtxinnovations.com')}
📱 Phone: +1 (555) 123-4567

Hours: Monday - Friday, 9 AM - 6 PM EST
        """
        messagebox.showinfo("Support", support_text.strip())
    
    def show_docs(self):
        """Show documentation"""
        # TODO: Implement documentation viewer
        messagebox.showinfo("Documentation", "Documentation viewer coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{APP_NAME} v{APP_VERSION}

{APP_DESCRIPTION}

Features:
• Multi-account Google authentication
• Full Google Sheets integration with editing
• Advanced email campaigns with templates
• Batch management and tracking
• Real-time analytics and reporting
• Status tracking and updates
• Professional macOS-inspired UI/UX
• Beautiful animations and transitions

© 2024 RTX Innovations
All rights reserved.
        """
        messagebox.showinfo("About", about_text.strip())
    
    def refresh_current_view(self):
        """Refresh current view"""
        if self.current_frame and hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh()
            self.update_status("View refreshed")
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🛑 Application interrupted by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
            messagebox.showerror("Error", f"Application error: {e}")

if __name__ == "__main__":
    app = RTXInnovationsApp()
    app.run() 