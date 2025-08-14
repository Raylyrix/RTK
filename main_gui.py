import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter.messagebox import askyesno, showinfo, showerror
import threading
import datetime
from ttkthemes import ThemedTk
import os
import webbrowser

# Import our modules
from google_auth import GoogleAuthenticator
from sheets_handler import SheetsHandler
from email_sender import EmailSender
from scheduler import EmailScheduler
import config

class AutoMailerGUI:
    def __init__(self):
        # Initialize main window with modern theme
        self.root = ThemedTk(theme="equilux")  # Modern dark theme
        self.root.title(f"🚀 {config.APP_NAME} v{config.APP_VERSION}")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(900, 700)
        
        # Configure style
        self.setup_styles()
        
        # Initialize components
        self.auth = GoogleAuthenticator()
        self.sheets_handler = SheetsHandler()
        self.email_sender = EmailSender()
        self.scheduler = EmailScheduler()
        
        # Variables
        self.authenticated = False
        self.current_sheet_data = None
        self.sending_in_progress = False
        self.attachment_files = []  # List to store attachment file paths
        
        # Create GUI
        self.create_widgets()
        self.center_window()
        
        # Start scheduler
        self.scheduler.start_scheduler()
    
    def setup_styles(self):
        """Setup custom styles for better appearance"""
        style = ttk.Style()
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        style.configure('Success.TLabel', foreground='#00ff00')
        style.configure('Error.TLabel', foreground='#ff4444')
        style.configure('Warning.TLabel', foreground='#ffaa00')
        style.configure('Info.TLabel', foreground='#4488ff')
        
        # Button styles
        style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Success.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Danger.TButton', font=('Segoe UI', 9, 'bold'))
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create header
        self.create_header(main_container)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True, pady=(15, 0))
        
        # Create tabs
        self.create_main_tab()
        self.create_templates_tab()
        self.create_scheduler_tab()
        self.create_settings_tab()
        self.create_logs_tab()
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 10))
        
        # App title and version
        title_label = ttk.Label(header_frame, text="AutoMailer Pro", style='Title.TLabel')
        title_label.pack(side='left')
        
        version_label = ttk.Label(header_frame, text=f"v{config.APP_VERSION}", style='Subtitle.TLabel')
        version_label.pack(side='left', padx=(10, 0))
        
        # Status indicators
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side='right')
        
        self.connection_status = ttk.Label(status_frame, text="● Disconnected", style='Error.TLabel')
        self.connection_status.pack(side='right', padx=(10, 0))
    
    def create_main_tab(self):
        """Create main tab with enhanced design"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="📧 Main")
        
        # Create scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Authentication Section
        auth_frame = ttk.LabelFrame(scrollable_frame, text="🔐 Google Authentication", padding=15)
        auth_frame.pack(fill='x', padx=10, pady=8)
        
        self.auth_status_label = ttk.Label(auth_frame, text="Status: Not authenticated", style='Error.TLabel')
        self.auth_status_label.pack(anchor='w')
        
        auth_btn_frame = ttk.Frame(auth_frame)
        auth_btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(auth_btn_frame, text="🔑 Authenticate with Google", 
                  command=self.authenticate_google, style='Action.TButton').pack(side='left')
        
        self.signature_info_label = ttk.Label(auth_btn_frame, text="", style='Info.TLabel')
        self.signature_info_label.pack(side='right')
        
        # Google Sheets Section
        sheets_frame = ttk.LabelFrame(scrollable_frame, text="📊 Google Sheets Integration", padding=15)
        sheets_frame.pack(fill='x', padx=10, pady=8)
        
        ttk.Label(sheets_frame, text="Google Sheets URL:", style='Subtitle.TLabel').pack(anchor='w')
        self.sheets_url_var = tk.StringVar()
        url_frame = ttk.Frame(sheets_frame)
        url_frame.pack(fill='x', pady=(5, 10))
        
        ttk.Entry(url_frame, textvariable=self.sheets_url_var, font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True)
        ttk.Button(url_frame, text="📋 Paste", command=self.paste_url).pack(side='right', padx=(5, 0))
        
        sheets_controls = ttk.Frame(sheets_frame)
        sheets_controls.pack(fill='x')
        
        ttk.Button(sheets_controls, text="🔄 Load Sheets", command=self.load_sheets).pack(side='left', padx=(0,10))
        
        ttk.Label(sheets_controls, text="Sheet:", style='Subtitle.TLabel').pack(side='left', padx=(0,5))
        self.sheet_name_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheets_controls, textvariable=self.sheet_name_var, width=25, font=('Segoe UI', 9))
        self.sheet_combo.pack(side='left', padx=(0,10))
        
        ttk.Button(sheets_controls, text="👁️ Preview Data", command=self.preview_data).pack(side='left')
        
        # Data Preview with enhanced styling
        preview_frame = ttk.LabelFrame(scrollable_frame, text="📋 Data Preview", padding=15)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=8)
        
        # Treeview for data preview with custom styling
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.pack(fill='both', expand=True)
        
        self.data_tree = ttk.Treeview(tree_frame, height=8)
        data_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.data_tree.yview)
        data_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.data_tree.xview)
        
        self.data_tree.configure(yscrollcommand=data_scrollbar_y.set, xscrollcommand=data_scrollbar_x.set)
        
        self.data_tree.pack(side='left', fill='both', expand=True)
        data_scrollbar_y.pack(side='right', fill='y')
        data_scrollbar_x.pack(side='bottom', fill='x')
        
        # Email Template Section with enhanced design
        template_frame = ttk.LabelFrame(scrollable_frame, text="✉️ Email Template", padding=15)
        template_frame.pack(fill='x', padx=10, pady=8)
        
        # From Email Section with alias dropdown
        from_frame = ttk.Frame(template_frame)
        from_frame.pack(fill='x', pady=(0,10))
        
        ttk.Label(from_frame, text="From Email:", style='Subtitle.TLabel').pack(side='left')
        self.from_email_var = tk.StringVar()
        self.from_email_combo = ttk.Combobox(from_frame, textvariable=self.from_email_var, width=35, font=('Segoe UI', 9))
        self.from_email_combo.pack(side='left', padx=(5,15))
        
        ttk.Label(from_frame, text="Display Name:", style='Subtitle.TLabel').pack(side='left')
        self.from_name_var = tk.StringVar()
        ttk.Entry(from_frame, textvariable=self.from_name_var, width=25, font=('Segoe UI', 9)).pack(side='left', padx=(5,15))
        
        ttk.Button(from_frame, text="🔄 Refresh Aliases", command=self.refresh_aliases).pack(side='right')
        
        # Signature options
        signature_frame = ttk.Frame(template_frame)
        signature_frame.pack(fill='x', pady=(0,10))
        
        self.include_signature_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(signature_frame, text="📝 Include Gmail Signature", 
                       variable=self.include_signature_var).pack(side='left')
        
        self.signature_preview_btn = ttk.Button(signature_frame, text="👁️ Preview Signature", 
                                              command=self.preview_signature)
        self.signature_preview_btn.pack(side='right')
        
        # Subject and body
        ttk.Label(template_frame, text="Subject:", style='Subtitle.TLabel').pack(anchor='w')
        self.subject_var = tk.StringVar()
        ttk.Entry(template_frame, textvariable=self.subject_var, font=('Segoe UI', 10)).pack(fill='x', pady=(5,10))
        
        ttk.Label(template_frame, text="Body (Use ((column name)) for placeholders):", style='Subtitle.TLabel').pack(anchor='w')
        self.body_text = scrolledtext.ScrolledText(template_frame, height=10, wrap=tk.WORD, font=('Segoe UI', 9))
        self.body_text.pack(fill='x', pady=(5,10))
        
        template_controls = ttk.Frame(template_frame)
        template_controls.pack(fill='x')
        
        ttk.Button(template_controls, text="💾 Save Template", command=self.save_template).pack(side='left', padx=(0,5))
        ttk.Button(template_controls, text="📂 Load Template", command=self.load_template).pack(side='left', padx=(0,5))
        ttk.Button(template_controls, text="✅ Validate Placeholders", command=self.validate_placeholders).pack(side='left', padx=(0,5))
        ttk.Button(template_controls, text="🎯 Insert Placeholder", command=self.insert_placeholder).pack(side='left')
        
        # Attachments Section with drag-drop visual
        attachments_frame = ttk.LabelFrame(scrollable_frame, text="📎 Attachments", padding=15)
        attachments_frame.pack(fill='x', padx=10, pady=8)
        
        # Attachment controls
        attach_controls = ttk.Frame(attachments_frame)
        attach_controls.pack(fill='x', pady=(0,10))
        
        ttk.Button(attach_controls, text="📁 Add Files", command=self.add_attachments).pack(side='left', padx=(0,5))
        ttk.Button(attach_controls, text="🗑️ Remove Selected", command=self.remove_attachment).pack(side='left', padx=(0,5))
        ttk.Button(attach_controls, text="🧹 Clear All", command=self.clear_attachments).pack(side='left')
        
        # Attachment list with enhanced styling
        attach_list_frame = ttk.Frame(attachments_frame)
        attach_list_frame.pack(fill='x', pady=(0,10))
        
        self.attachments_listbox = tk.Listbox(attach_list_frame, height=4, font=('Segoe UI', 9))
        attach_scroll = ttk.Scrollbar(attach_list_frame, orient="vertical", command=self.attachments_listbox.yview)
        self.attachments_listbox.configure(yscrollcommand=attach_scroll.set)
        
        self.attachments_listbox.pack(side='left', fill='x', expand=True)
        attach_scroll.pack(side='right', fill='y')
        
        # Attachment info label
        self.attachment_info_label = ttk.Label(attachments_frame, text="No attachments", style='Subtitle.TLabel')
        self.attachment_info_label.pack(anchor='w')
        
        # Sending Options with better layout
        options_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Sending Options", padding=15)
        options_frame.pack(fill='x', padx=10, pady=8)
        
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(fill='x')
        
        # Batch size
        batch_frame = ttk.Frame(options_grid)
        batch_frame.pack(side='left', padx=(0,30))
        ttk.Label(batch_frame, text="Batch Size:", style='Subtitle.TLabel').pack()
        self.batch_size_var = tk.IntVar(value=config.DEFAULT_BATCH_SIZE)
        batch_spin = ttk.Spinbox(batch_frame, from_=1, to=100, textvariable=self.batch_size_var, width=10)
        batch_spin.pack()
        
        # Time gap
        gap_frame = ttk.Frame(options_grid)
        gap_frame.pack(side='left', padx=(0,30))
        ttk.Label(gap_frame, text="Time Gap (sec):", style='Subtitle.TLabel').pack()
        self.time_gap_var = tk.IntVar(value=config.DEFAULT_TIME_GAP)
        gap_spin = ttk.Spinbox(gap_frame, from_=1, to=60, textvariable=self.time_gap_var, width=10)
        gap_spin.pack()
        
        # Schedule Section with modern design
        schedule_frame = ttk.LabelFrame(scrollable_frame, text="⏰ Schedule Send (Optional)", padding=15)
        schedule_frame.pack(fill='x', padx=10, pady=8)
        
        schedule_controls = ttk.Frame(schedule_frame)
        schedule_controls.pack(fill='x')
        
        self.schedule_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(schedule_controls, text="📅 Schedule for later", 
                       variable=self.schedule_enabled_var, 
                       command=self.toggle_schedule).pack(side='left')
        
        # Date and time controls
        datetime_frame = ttk.Frame(schedule_controls)
        datetime_frame.pack(side='right')
        
        ttk.Label(datetime_frame, text="Date:", style='Subtitle.TLabel').pack(side='left', padx=(0,5))
        self.schedule_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.schedule_date_entry = ttk.Entry(datetime_frame, textvariable=self.schedule_date_var, width=12)
        self.schedule_date_entry.pack(side='left', padx=(0,15))
        self.schedule_date_entry.config(state='disabled')
        
        ttk.Label(datetime_frame, text="Time:", style='Subtitle.TLabel').pack(side='left', padx=(0,5))
        self.schedule_time_var = tk.StringVar(value="09:00")
        self.schedule_time_entry = ttk.Entry(datetime_frame, textvariable=self.schedule_time_var, width=8)
        self.schedule_time_entry.pack(side='left')
        self.schedule_time_entry.config(state='disabled')
        
        # Progress and Controls with enhanced styling
        controls_frame = ttk.LabelFrame(scrollable_frame, text="🚀 Send Controls", padding=15)
        controls_frame.pack(fill='x', padx=10, pady=8)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(fill='x', pady=(0,10))
        
        self.status_label = ttk.Label(controls_frame, text="Ready to send emails", style='Info.TLabel')
        self.status_label.pack(anchor='w', pady=(0,10))
        
        # Control buttons
        controls_buttons = ttk.Frame(controls_frame)
        controls_buttons.pack(fill='x')
        
        self.send_button = ttk.Button(controls_buttons, text="🚀 Send Emails", 
                                     command=self.send_emails, style='Success.TButton')
        self.send_button.pack(side='left', padx=(0,10))
        
        ttk.Button(controls_buttons, text="🧪 Send Test Email", command=self.send_test_email).pack(side='left', padx=(0,10))
        ttk.Button(controls_buttons, text="⏹️ Stop Sending", command=self.stop_sending, style='Danger.TButton').pack(side='left')
        
        # Email count display
        self.email_count_label = ttk.Label(controls_buttons, text="", style='Info.TLabel')
        self.email_count_label.pack(side='right')
        
        # Pack scrollable components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if 'docs.google.com/spreadsheets' in clipboard_content:
                self.sheets_url_var.set(clipboard_content)
                showinfo("Success", "URL pasted from clipboard!")
            else:
                showerror("Error", "Clipboard doesn't contain a valid Google Sheets URL")
        except:
            showerror("Error", "Could not access clipboard")
    
    def refresh_aliases(self):
        """Refresh Gmail aliases dropdown"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        try:
            # Force refresh aliases
            self.email_sender.get_gmail_aliases()
            aliases = self.email_sender.gmail_aliases
            
            alias_emails = [alias['email'] for alias in aliases]
            self.from_email_combo['values'] = alias_emails
            
            if aliases:
                # Set primary email as default
                for alias in aliases:
                    if alias.get('is_primary'):
                        self.from_email_var.set(alias['email'])
                        self.from_name_var.set(alias['name'])
                        break
                
                showinfo("Success", f"✅ Found {len(aliases)} verified send-as addresses")
            else:
                showinfo("Info", "No additional send-as addresses found. Using primary email.")
                
        except Exception as e:
            showerror("Error", f"Failed to refresh aliases: {str(e)}")
    
    def preview_signature(self):
        """Preview Gmail signature"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        signature = self.email_sender.gmail_signature
        if signature:
            # Create popup window for signature preview
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Gmail Signature Preview")
            preview_window.geometry("500x300")
            preview_window.transient(self.root)
            preview_window.grab_set()
            
            ttk.Label(preview_window, text="Your Gmail Signature:", style='Title.TLabel').pack(pady=10)
            
            signature_text = scrolledtext.ScrolledText(preview_window, height=12, wrap=tk.WORD, font=('Segoe UI', 9))
            signature_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            signature_text.insert(1.0, signature)
            signature_text.config(state='disabled')
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=(0,15))
        else:
            showinfo("Info", "No Gmail signature found for your account.")
    
    def insert_placeholder(self):
        """Insert placeholder helper"""
        if not self.current_sheet_data:
            showerror("Error", "Please load sheet data first to see available columns")
            return
        
        # Create popup for placeholder selection
        placeholder_window = tk.Toplevel(self.root)
        placeholder_window.title("Insert Placeholder")
        placeholder_window.geometry("400x300")
        placeholder_window.transient(self.root)
        placeholder_window.grab_set()
        
        ttk.Label(placeholder_window, text="Select a column to insert:", style='Title.TLabel').pack(pady=10)
        
        # List of available columns
        columns_listbox = tk.Listbox(placeholder_window, font=('Segoe UI', 10))
        columns_listbox.pack(fill='both', expand=True, padx=15, pady=(0,15))
        
        for header in self.current_sheet_data['headers']:
            columns_listbox.insert(tk.END, header)
        
        def insert_selected():
            selection = columns_listbox.curselection()
            if selection:
                column_name = columns_listbox.get(selection[0])
                placeholder = f"(({column_name}))"
                
                # Insert at cursor position in body text
                cursor_pos = self.body_text.index(tk.INSERT)
                self.body_text.insert(cursor_pos, placeholder)
                
                placeholder_window.destroy()
                showinfo("Success", f"✅ Inserted placeholder: {placeholder}")
        
        button_frame = ttk.Frame(placeholder_window)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Insert", command=insert_selected).pack(side='left', padx=(0,10))
        ttk.Button(button_frame, text="Cancel", command=placeholder_window.destroy).pack(side='left')
    
    def use_auth_email(self):
        """Use the authenticated email as from email"""
        if self.authenticated and self.auth.get_user_email():
            self.from_email_var.set(self.auth.get_user_email())
            if not self.from_name_var.get():
                # Extract name from email (before @)
                email = self.auth.get_user_email()
                name = email.split('@')[0].replace('.', ' ').title()
                self.from_name_var.set(name)
        else:
            showerror("Error", "Please authenticate with Google first")
    
    def toggle_schedule(self):
        """Toggle schedule controls based on checkbox"""
        if self.schedule_enabled_var.get():
            self.schedule_date_entry.config(state='normal')
            self.schedule_time_entry.config(state='normal')
            self.send_button.config(text="📅 Schedule Send")
        else:
            self.schedule_date_entry.config(state='disabled')
            self.schedule_time_entry.config(state='disabled')
            self.send_button.config(text="🚀 Send Emails")
    
    def add_attachments(self):
        """Add attachment files"""
        file_paths = filedialog.askopenfilenames(
            title="Select Files to Attach",
            filetypes=[
                ("All files", "*.*"),
                ("Documents", "*.pdf *.doc *.docx *.txt *.rtf"),
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("Spreadsheets", "*.xlsx *.xls *.csv"),
                ("Presentations", "*.ppt *.pptx"),
                ("Archives", "*.zip *.rar *.7z")
            ]
        )
        
        if file_paths:
            total_size = sum(os.path.getsize(f) for f in self.attachment_files if os.path.exists(f))
            max_size = 25 * 1024 * 1024  # 25MB
            
            added_count = 0
            for file_path in file_paths:
                if file_path not in self.attachment_files:
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        if total_size + file_size > max_size:
                            showerror("File Too Large", 
                                    f"Adding this file would exceed the 25MB attachment limit.\n"
                                    f"File: {os.path.basename(file_path)} ({file_size/(1024*1024):.1f}MB)")
                            continue
                        
                        self.attachment_files.append(file_path)
                        total_size += file_size
                        self.attachments_listbox.insert(tk.END, f"📎 {os.path.basename(file_path)}")
                        added_count += 1
            
            self.update_attachment_info()
            if added_count > 0:
                showinfo("Success", f"✅ Added {added_count} attachment(s)")
    
    def remove_attachment(self):
        """Remove selected attachment"""
        selection = self.attachments_listbox.curselection()
        if selection:
            index = selection[0]
            self.attachments_listbox.delete(index)
            if 0 <= index < len(self.attachment_files):
                removed_file = self.attachment_files.pop(index)
                showinfo("Success", f"✅ Removed {os.path.basename(removed_file)}")
            self.update_attachment_info()
        else:
            showerror("Error", "Please select an attachment to remove")
    
    def clear_attachments(self):
        """Clear all attachments"""
        if self.attachment_files:
            if askyesno("Confirm", "⚠️ Are you sure you want to remove all attachments?\n\n"
                                   "This action cannot be undone."):
                self.attachment_files.clear()
                self.attachments_listbox.delete(0, tk.END)
                self.update_attachment_info()
                showinfo("Success", "✅ All attachments removed")
    
    def update_attachment_info(self):
        """Update attachment information label"""
        if not self.attachment_files:
            self.attachment_info_label.config(text="📎 No attachments")
        else:
            total_size = sum(os.path.getsize(f) for f in self.attachment_files if os.path.exists(f))
            size_mb = total_size / (1024 * 1024)
            count = len(self.attachment_files)
            
            if size_mb < 1:
                size_str = f"{total_size/1024:.1f} KB"
            else:
                size_str = f"{size_mb:.1f} MB"
            
            if size_mb > 20:
                self.attachment_info_label.config(text=f"⚠️ {count} file(s), {size_str} total (Near limit!)", style='Warning.TLabel')
            else:
                self.attachment_info_label.config(text=f"📎 {count} file(s), {size_str} total", style='Info.TLabel')
    
    def create_templates_tab(self):
        """Create templates management tab"""
        templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(templates_frame, text="📝 Templates")
        
        # Header
        header_frame = ttk.Frame(templates_frame)
        header_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(header_frame, text="Email Templates", style='Title.TLabel').pack(side='left')
        
        # Templates list with enhanced styling
        list_frame = ttk.LabelFrame(templates_frame, text="💾 Saved Templates", padding=15)
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0,15))
        
        # Template listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill='both', expand=True, pady=(0,15))
        
        self.templates_listbox = tk.Listbox(list_container, height=12, font=('Segoe UI', 10))
        template_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.templates_listbox.yview)
        self.templates_listbox.configure(yscrollcommand=template_scrollbar.set)
        
        self.templates_listbox.pack(side='left', fill='both', expand=True)
        template_scrollbar.pack(side='right', fill='y')
        
        # Template controls
        templates_controls = ttk.Frame(list_frame)
        templates_controls.pack(fill='x')
        
        ttk.Button(templates_controls, text="📂 Load Selected", command=self.load_selected_template).pack(side='left', padx=(0,10))
        ttk.Button(templates_controls, text="🗑️ Delete Selected", command=self.delete_template).pack(side='left', padx=(0,10))
        ttk.Button(templates_controls, text="🔄 Refresh List", command=self.refresh_templates).pack(side='left')
        
        self.refresh_templates()
    
    def create_scheduler_tab(self):
        """Create scheduler tab"""
        scheduler_frame = ttk.Frame(self.notebook)
        self.notebook.add(scheduler_frame, text="⏰ Scheduler")
        
        # Header
        header_frame = ttk.Frame(scheduler_frame)
        header_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(header_frame, text="Email Scheduler", style='Title.TLabel').pack(side='left')
        
        # New job section
        new_job_frame = ttk.LabelFrame(scheduler_frame, text="➕ Create Scheduled Job", padding=15)
        new_job_frame.pack(fill='x', padx=15, pady=(0,15))
        
        # Job name
        ttk.Label(new_job_frame, text="Job Name:", style='Subtitle.TLabel').pack(anchor='w')
        self.job_name_var = tk.StringVar()
        ttk.Entry(new_job_frame, textvariable=self.job_name_var, font=('Segoe UI', 10)).pack(fill='x', pady=(5,15))
        
        # Schedule type
        schedule_frame = ttk.Frame(new_job_frame)
        schedule_frame.pack(fill='x', pady=(0,15))
        
        ttk.Label(schedule_frame, text="Schedule Type:", style='Subtitle.TLabel').pack(side='left')
        self.schedule_type_var = tk.StringVar(value="once")
        schedule_combo = ttk.Combobox(schedule_frame, textvariable=self.schedule_type_var, 
                                    values=["once", "daily", "weekly", "monthly"], width=15)
        schedule_combo.pack(side='left', padx=(10,0))
        
        # Schedule time
        ttk.Label(schedule_frame, text="Time:", style='Subtitle.TLabel').pack(side='left', padx=(30,5))
        self.schedule_time_var = tk.StringVar(value="09:00")
        ttk.Entry(schedule_frame, textvariable=self.schedule_time_var, width=10).pack(side='left')
        
        # Schedule date (for 'once' type)
        ttk.Label(schedule_frame, text="Date (YYYY-MM-DD):", style='Subtitle.TLabel').pack(side='left', padx=(30,5))
        self.schedule_date_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        ttk.Entry(schedule_frame, textvariable=self.schedule_date_var, width=12).pack(side='left')
        
        ttk.Button(new_job_frame, text="➕ Create Job", command=self.create_scheduled_job, style='Action.TButton').pack(anchor='w')
        
        # Scheduled jobs list
        jobs_frame = ttk.LabelFrame(scheduler_frame, text="📋 Scheduled Jobs", padding=15)
        jobs_frame.pack(fill='both', expand=True, padx=15, pady=(0,15))
        
        # Jobs treeview with enhanced styling
        jobs_container = ttk.Frame(jobs_frame)
        jobs_container.pack(fill='both', expand=True, pady=(0,15))
        
        columns = ("Name", "Type", "Time", "Status", "Next Run")
        self.jobs_tree = ttk.Treeview(jobs_container, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.jobs_tree.heading(col, text=col)
            self.jobs_tree.column(col, width=150)
        
        jobs_scrollbar = ttk.Scrollbar(jobs_container, orient="vertical", command=self.jobs_tree.yview)
        self.jobs_tree.configure(yscrollcommand=jobs_scrollbar.set)
        
        self.jobs_tree.pack(side='left', fill='both', expand=True)
        jobs_scrollbar.pack(side='right', fill='y')
        
        # Job controls
        jobs_controls = ttk.Frame(jobs_frame)
        jobs_controls.pack(fill='x')
        
        ttk.Button(jobs_controls, text="❌ Cancel Selected", command=self.cancel_selected_job).pack(side='left', padx=(0,10))
        ttk.Button(jobs_controls, text="🔄 Refresh Jobs", command=self.refresh_scheduled_jobs).pack(side='left')
        
        self.refresh_scheduled_jobs()
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Header
        header_frame = ttk.Frame(settings_frame)
        header_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(header_frame, text="Settings", style='Title.TLabel').pack(side='left')
        
        # API Settings
        api_frame = ttk.LabelFrame(settings_frame, text="🔑 API Configuration", padding=15)
        api_frame.pack(fill='x', padx=15, pady=(0,15))
        
        ttk.Label(api_frame, text="Google API Credentials:", style='Subtitle.TLabel').pack(anchor='w')
        creds_frame = ttk.Frame(api_frame)
        creds_frame.pack(fill='x', pady=(5,15))
        
        self.creds_path_var = tk.StringVar(value=str(config.CREDENTIALS_FILE))
        ttk.Entry(creds_frame, textvariable=self.creds_path_var, font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True)
        ttk.Button(creds_frame, text="📁 Browse", command=self.browse_credentials).pack(side='right', padx=(10,0))
        
        ttk.Button(api_frame, text="📖 Setup Instructions", command=self.open_setup_guide).pack(anchor='w')
        
        # Default Settings
        defaults_frame = ttk.LabelFrame(settings_frame, text="🎛️ Default Settings", padding=15)
        defaults_frame.pack(fill='x', padx=15, pady=(0,15))
        
        settings_grid = ttk.Frame(defaults_frame)
        settings_grid.pack(fill='x')
        
        # Left column
        left_col = ttk.Frame(settings_grid)
        left_col.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_col, text=f"📦 Default Batch Size: {config.DEFAULT_BATCH_SIZE}", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        ttk.Label(left_col, text=f"⏱️ Default Time Gap: {config.DEFAULT_TIME_GAP} seconds", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        ttk.Label(left_col, text="📎 Max Attachment Size: 25MB per email", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        
        # Right column
        right_col = ttk.Frame(settings_grid)
        right_col.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_col, text="🎨 Theme: Modern Dark", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        ttk.Label(right_col, text="🔒 Secure OAuth Authentication", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        ttk.Label(right_col, text="📧 Gmail API Integration", style='Subtitle.TLabel').pack(anchor='w', pady=2)
        
        # About
        about_frame = ttk.LabelFrame(settings_frame, text="ℹ️ About", padding=15)
        about_frame.pack(fill='x', padx=15, pady=(0,15))
        
        about_info = ttk.Frame(about_frame)
        about_info.pack(fill='x')
        
        # Left side - app info
        app_info = ttk.Frame(about_info)
        app_info.pack(side='left', fill='x', expand=True)
        
        ttk.Label(app_info, text=f"🚀 {config.APP_NAME} v{config.APP_VERSION}", style='Title.TLabel').pack(anchor='w')
        ttk.Label(app_info, text="Professional email marketing automation", style='Subtitle.TLabel').pack(anchor='w', pady=(5,15))
        
        features_text = """✅ Smart placeholder extraction with fuzzy matching
✅ Gmail signature auto-detection and inclusion
✅ Verified send-as alias support  
✅ Large file attachments up to 25MB
✅ Integrated scheduling system
✅ Modern responsive GUI design
✅ Comprehensive error handling"""
        
        ttk.Label(app_info, text=features_text, style='Subtitle.TLabel').pack(anchor='w')
        
        # Right side - stats
        stats_info = ttk.Frame(about_info)
        stats_info.pack(side='right', padx=(30,0))
        
        ttk.Label(stats_info, text="📊 Statistics", style='Title.TLabel').pack(anchor='w')
        
        # We'll update these dynamically
        self.stats_label = ttk.Label(stats_info, text="", style='Subtitle.TLabel')
        self.stats_label.pack(anchor='w', pady=(5,0))
        
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        try:
            stats_text = f"📧 Session Emails Sent: {getattr(self.email_sender, 'sent_count', 0)}\n"
            stats_text += f"❌ Session Failures: {getattr(self.email_sender, 'failed_count', 0)}\n"
            stats_text += f"📎 Attachments: {len(self.attachment_files)}\n"
            stats_text += f"📝 Templates: {len(list(config.TEMPLATES_DIR.glob('*.json'))) if config.TEMPLATES_DIR.exists() else 0}"
            
            self.stats_label.config(text=stats_text)
        except Exception as e:
            pass
        
        # Schedule next update
        self.root.after(5000, self.update_stats)
    
    def create_logs_tab(self):
        """Create logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Header
        header_frame = ttk.Frame(logs_frame)
        header_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Label(header_frame, text="Application Logs", style='Title.TLabel').pack(side='left')
        
        # Logs display
        logs_display_frame = ttk.LabelFrame(logs_frame, text="📄 Log Viewer", padding=15)
        logs_display_frame.pack(fill='both', expand=True, padx=15, pady=(0,15))
        
        # Log text area
        logs_container = ttk.Frame(logs_display_frame)
        logs_container.pack(fill='both', expand=True, pady=(0,15))
        
        self.logs_text = scrolledtext.ScrolledText(logs_container, height=20, wrap=tk.WORD, font=('Consolas', 9))
        self.logs_text.pack(fill='both', expand=True)
        
        # Log controls
        logs_controls = ttk.Frame(logs_display_frame)
        logs_controls.pack(fill='x')
        
        ttk.Button(logs_controls, text="🔄 Refresh Logs", command=self.refresh_logs).pack(side='left', padx=(0,10))
        ttk.Button(logs_controls, text="🧹 Clear Logs", command=self.clear_logs).pack(side='left', padx=(0,10))
        ttk.Button(logs_controls, text="💾 Export Logs", command=self.export_logs).pack(side='left')
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(logs_controls, text="🔄 Auto-refresh", 
                       variable=self.auto_refresh_var).pack(side='right')
        
        # Load initial logs
        self.refresh_logs()
        self.auto_refresh_logs()
    
    def auto_refresh_logs(self):
        """Auto-refresh logs if enabled"""
        if self.auto_refresh_var.get():
            self.refresh_logs()
        
        # Schedule next refresh
        self.root.after(10000, self.auto_refresh_logs)  # Every 10 seconds
    
    # Event handlers and methods
    def authenticate_google(self):
        """Authenticate with Google APIs"""
        try:
            if self.auth.authenticate():
                self.authenticated = True
                user_email = self.auth.get_user_email()
                
                # Update UI
                self.auth_status_label.config(text=f"✅ Authenticated as {user_email}", style='Success.TLabel')
                self.connection_status.config(text="● Connected", style='Success.TLabel')
                
                # Connect email sender and get aliases
                self.email_sender.connect()
                
                # Update signature info
                if self.email_sender.gmail_signature:
                    self.signature_info_label.config(text="📝 Signature detected", style='Success.TLabel')
                else:
                    self.signature_info_label.config(text="📝 No signature found", style='Warning.TLabel')
                
                # Refresh aliases
                self.refresh_aliases()
                
                showinfo("Success", f"✅ Successfully authenticated with Google!\n\n"
                                  f"📧 Email: {user_email}\n"
                                  f"📝 Signature: {'Found' if self.email_sender.gmail_signature else 'None'}\n"
                                  f"🔗 Aliases: {len(self.email_sender.gmail_aliases)} verified")
            else:
                showerror("Error", "Failed to authenticate with Google")
        except Exception as e:
            showerror("Error", f"Authentication failed: {str(e)}")
    
    def load_sheets(self):
        """Load Google Sheets data"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        url = self.sheets_url_var.get().strip()
        if not url:
            showerror("Error", "Please enter a Google Sheets URL")
            return
        
        try:
            # Get available sheets
            sheet_names = self.sheets_handler.get_available_sheets(url)
            if sheet_names:
                self.sheet_combo['values'] = sheet_names
                self.sheet_combo.set(sheet_names[0])
                showinfo("Success", f"✅ Loaded {len(sheet_names)} sheets")
            else:
                showerror("Error", "No sheets found or unable to access the spreadsheet")
        except Exception as e:
            showerror("Error", f"Failed to load sheets: {str(e)}")
    
    def preview_data(self):
        """Preview data from selected sheet"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        url = self.sheets_url_var.get().strip()
        sheet_name = self.sheet_name_var.get()
        
        if not url or not sheet_name:
            showerror("Error", "Please select a sheet to preview")
            return
        
        try:
            self.current_sheet_data = self.sheets_handler.get_sheet_data(url, sheet_name)
            
            if self.current_sheet_data and 'data' in self.current_sheet_data and self.current_sheet_data['data']:
                # Clear existing data
                self.data_tree.delete(*self.data_tree.get_children())
                
                # Set up columns
                columns = self.current_sheet_data['headers']
                self.data_tree['columns'] = columns
                self.data_tree['show'] = 'headings'
                
                for col in columns:
                    self.data_tree.heading(col, text=col)
                    self.data_tree.column(col, width=120)
                
                # Add data (limit to first 100 rows for performance)
                for row in self.current_sheet_data['data'][:100]:
                    values = [str(row.get(col, '')) for col in columns]
                    self.data_tree.insert('', 'end', values=values)
                
                # Update status and email count
                row_count = len(self.current_sheet_data['data'])
                self.status_label.config(text=f"✅ Loaded {row_count} rows", style='Success.TLabel')
                self.email_count_label.config(text=f"📧 {row_count} emails ready")
                
                showinfo("Success", f"✅ Previewing {row_count} rows of data\n\n"
                                  f"📊 Columns: {', '.join(columns[:3])}{'...' if len(columns) > 3 else ''}")
            else:
                showerror("Error", "No data found in the selected sheet")
        except Exception as e:
            showerror("Error", f"Failed to preview data: {str(e)}")
    
    def validate_placeholders(self):
        """Validate placeholders in email template with suggestions"""
        if self.current_sheet_data is None:
            showerror("Error", "Please load sheet data first")
            return
        
        subject = self.subject_var.get()
        body = self.body_text.get(1.0, tk.END)
        
        missing_subject = self.sheets_handler.validate_placeholders(subject, self.current_sheet_data)
        missing_body = self.sheets_handler.validate_placeholders(body, self.current_sheet_data)
        
        all_missing = list(set(missing_subject + missing_body))
        
        if all_missing:
            # Create detailed validation window
            validation_window = tk.Toplevel(self.root)
            validation_window.title("Placeholder Validation")
            validation_window.geometry("600x400")
            validation_window.transient(self.root)
            validation_window.grab_set()
            
            ttk.Label(validation_window, text="⚠️ Placeholder Validation Issues", style='Title.TLabel').pack(pady=15)
            
            # Scrollable text for detailed feedback
            feedback_text = scrolledtext.ScrolledText(validation_window, height=15, wrap=tk.WORD, font=('Segoe UI', 9))
            feedback_text.pack(fill='both', expand=True, padx=15, pady=(0,15))
            
            feedback_content = "The following placeholders were not found in your data:\n\n"
            
            for placeholder in all_missing:
                suggestions = self.sheets_handler.get_column_suggestions(placeholder, self.current_sheet_data)
                feedback_content += f"❌ '(({placeholder}))'\n"
                if suggestions:
                    feedback_content += f"   💡 Did you mean: {', '.join(f'(({s}))' for s in suggestions)}\n"
                feedback_content += "\n"
            
            feedback_content += f"\n📋 Available columns:\n{', '.join(f'(({col}))' for col in self.current_sheet_data['headers'])}"
            
            feedback_text.insert(1.0, feedback_content)
            feedback_text.config(state='disabled')
            
            ttk.Button(validation_window, text="Close", command=validation_window.destroy).pack(pady=(0,15))
        else:
            showinfo("Validation Success", "✅ All placeholders are valid!\n\n"
                                         f"Found {len(self.sheets_handler.find_placeholders(subject + body))} placeholders")
    
    def send_emails(self):
        """Send bulk emails or schedule them"""
        if self.sending_in_progress:
            showerror("Error", "Email sending already in progress")
            return
        
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        if not self.current_sheet_data or not self.current_sheet_data.get('data'):
            showerror("Error", "Please load sheet data first")
            return
        
        subject = self.subject_var.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        
        if not subject or not body:
            showerror("Error", "Please enter both subject and body")
            return
        
        # Get From email settings
        from_email = self.from_email_var.get().strip() or None
        from_name = self.from_name_var.get().strip() or None
        
        # Check attachments
        attachments = self.attachment_files if self.attachment_files else None
        
        # Get signature setting
        include_signature = self.include_signature_var.get()
        
        # Check if scheduling is enabled
        if self.schedule_enabled_var.get():
            try:
                schedule_date = self.schedule_date_var.get()
                schedule_time = self.schedule_time_var.get()
                send_datetime = datetime.datetime.strptime(f"{schedule_date} {schedule_time}", "%Y-%m-%d %H:%M")
                
                if send_datetime <= datetime.datetime.now():
                    showerror("Error", "Scheduled time must be in the future")
                    return
                
                # Confirm schedule
                email_count = len(self.current_sheet_data['data'])
                attach_info = f" with {len(self.attachment_files)} attachment(s)" if attachments else ""
                from_info = f" from {from_name} <{from_email}>" if from_email else ""
                sig_info = " (with signature)" if include_signature else ""
                
                if not askyesno("Confirm Schedule", 
                               f"📅 Schedule {email_count} emails{attach_info}{from_info}{sig_info}\n\n"
                               f"⏰ Send time: {send_datetime}\n\n"
                               f"Continue?"):
                    return
                
                # Schedule the email
                if self.email_sender.send_scheduled_email(
                    self.current_sheet_data, subject, body, send_datetime,
                    None, self.batch_size_var.get(), self.time_gap_var.get(),
                    attachments, from_email, from_name, include_signature
                ):
                    showinfo("Scheduled", f"✅ Emails scheduled for {send_datetime}\n\n"
                                        f"📧 {email_count} emails will be sent automatically")
                    self.status_label.config(text=f"📅 Scheduled for {send_datetime}", style='Success.TLabel')
                else:
                    showerror("Error", "Failed to schedule emails")
                return
                
            except ValueError:
                showerror("Error", "Invalid date or time format")
                return
        
        # Regular send (not scheduled)
        email_count = len(self.current_sheet_data['data'])
        attach_info = f" with {len(self.attachment_files)} attachment(s)" if attachments else ""
        from_info = f" from {from_name} <{from_email}>" if from_email else ""
        sig_info = " (with signature)" if include_signature else ""
        
        if not askyesno("Confirm Send", 
                       f"🚀 Send {email_count} emails{attach_info}{from_info}{sig_info}?\n\n"
                       f"📦 Batch size: {self.batch_size_var.get()}\n"
                       f"⏱️ Time gap: {self.time_gap_var.get()} seconds\n\n"
                       f"This will start immediately. Continue?"):
            return
        
        # Start sending in background thread
        self.sending_in_progress = True
        self.send_button.config(state='disabled', text="⏳ Sending...")
        self.progress_var.set(0)
        
        def send_worker():
            try:
                sent, failed = self.email_sender.send_bulk_emails(
                    self.current_sheet_data,
                    subject,
                    body,
                    batch_size=self.batch_size_var.get(),
                    time_gap=self.time_gap_var.get(),
                    progress_callback=self.update_progress,
                    attachments=attachments,
                    from_email=from_email,
                    from_name=from_name,
                    include_signature=include_signature
                )
                
                # Update UI on completion
                self.root.after(0, lambda: self.on_send_complete(sent, failed))
                
            except Exception as e:
                self.root.after(0, lambda: self.on_send_error(str(e)))
        
        threading.Thread(target=send_worker, daemon=True).start()
    
    def update_progress(self, progress, sent, failed):
        """Update progress bar and status"""
        self.root.after(0, lambda: self._update_progress_ui(progress, sent, failed))
    
    def _update_progress_ui(self, progress, sent, failed):
        """Update progress UI elements"""
        self.progress_var.set(progress)
        self.status_label.config(text=f"🚀 Progress: {progress:.1f}% - Sent: {sent}, Failed: {failed}", style='Info.TLabel')
    
    def on_send_complete(self, sent, failed):
        """Handle send completion"""
        self.sending_in_progress = False
        self.send_button.config(state='normal', text="🚀 Send Emails")
        self.progress_var.set(100)
        self.status_label.config(text=f"✅ Completed - Sent: {sent}, Failed: {failed}", style='Success.TLabel')
        
        # Show detailed completion dialog
        total = sent + failed
        success_rate = (sent / total * 100) if total > 0 else 0
        
        showinfo("Send Complete", f"🎉 Email sending completed!\n\n"
                                f"✅ Successfully sent: {sent}\n"
                                f"❌ Failed: {failed}\n"
                                f"📊 Success rate: {success_rate:.1f}%\n\n"
                                f"Check the logs for detailed information.")
    
    def on_send_error(self, error_msg):
        """Handle send error"""
        self.sending_in_progress = False
        self.send_button.config(state='normal', text="🚀 Send Emails")
        self.status_label.config(text="❌ Error occurred during sending", style='Error.TLabel')
        showerror("Send Error", f"❌ Error during email sending:\n\n{error_msg}")
    
    def send_test_email(self):
        """Send a test email to yourself"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        subject = self.subject_var.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        
        if not subject or not body:
            showerror("Error", "Please enter both subject and body")
            return
        
        try:
            user_email = self.auth.get_user_email()
            attachments = self.attachment_files if self.attachment_files else None
            from_email = self.from_email_var.get().strip() or None
            from_name = self.from_name_var.get().strip() or None
            include_signature = self.include_signature_var.get()
            
            if self.email_sender.send_single_email(user_email, f"[TEST] {subject}", body, 
                                                  attachments=attachments, from_email=from_email, 
                                                  from_name=from_name, include_signature=include_signature):
                attach_info = f" with {len(self.attachment_files)} attachment(s)" if attachments else ""
                from_info = f" from {from_name} <{from_email}>" if from_email else ""
                sig_info = " (with signature)" if include_signature else ""
                
                showinfo("Test Success", f"✅ Test email sent to {user_email}\n\n"
                                       f"📧 Subject: [TEST] {subject}\n"
                                       f"📎 Attachments: {len(self.attachment_files) if attachments else 0}\n"
                                       f"📝 Signature: {'Included' if include_signature else 'Not included'}")
            else:
                showerror("Error", "Failed to send test email")
        except Exception as e:
            showerror("Error", f"Failed to send test email: {str(e)}")
    
    def stop_sending(self):
        """Stop email sending process"""
        if self.sending_in_progress:
            if askyesno("Confirm Stop", "⚠️ Are you sure you want to stop email sending?\n\n"
                                      "This will interrupt the current batch."):
                self.sending_in_progress = False
                self.status_label.config(text="⏹️ Stopping email send...", style='Warning.TLabel')
                self.send_button.config(text="⏹️ Stopping...")
    
    def save_template(self):
        """Save current template"""
        subject = self.subject_var.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        
        if not subject or not body:
            showerror("Error", "Please enter both subject and body")
            return
        
        # Simple template saving - you could expand this
        template_name = tk.simpledialog.askstring("Save Template", "Enter template name:")
        if template_name:
            try:
                template_data = {
                    'subject': subject,
                    'body': body,
                    'attachments': self.attachment_files.copy(),
                    'from_email': self.from_email_var.get(),
                    'from_name': self.from_name_var.get(),
                    'include_signature': self.include_signature_var.get(),
                    'created': datetime.datetime.now().isoformat()
                }
                
                # Save to templates directory
                template_file = config.TEMPLATES_DIR / f"{template_name}.json"
                with open(template_file, 'w') as f:
                    import json
                    json.dump(template_data, f, indent=2)
                
                showinfo("Success", f"✅ Template '{template_name}' saved\n\n"
                                  f"📎 Attachments: {len(self.attachment_files)}\n"
                                  f"📝 Signature: {'Included' if self.include_signature_var.get() else 'Not included'}")
                self.refresh_templates()
            except Exception as e:
                showerror("Error", f"Failed to save template: {str(e)}")
    
    def load_template(self):
        """Load a template file"""
        template_file = filedialog.askopenfilename(
            initialdir=config.TEMPLATES_DIR,
            title="Select Template File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if template_file:
            try:
                import json
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                
                self.subject_var.set(template_data.get('subject', ''))
                self.body_text.delete(1.0, tk.END)
                self.body_text.insert(1.0, template_data.get('body', ''))
                
                # Load From email settings
                self.from_email_var.set(template_data.get('from_email', ''))
                self.from_name_var.set(template_data.get('from_name', ''))
                
                # Load signature setting
                self.include_signature_var.set(template_data.get('include_signature', True))
                
                # Load attachments if they exist
                saved_attachments = template_data.get('attachments', [])
                self.clear_attachments()
                for attachment in saved_attachments:
                    if os.path.exists(attachment):
                        self.attachment_files.append(attachment)
                        self.attachments_listbox.insert(tk.END, f"📎 {os.path.basename(attachment)}")
                self.update_attachment_info()
                
                showinfo("Success", f"✅ Template loaded\n\n"
                                  f"📎 Attachments: {len(saved_attachments)}\n"
                                  f"📝 Signature: {'Included' if template_data.get('include_signature', True) else 'Not included'}")
            except Exception as e:
                showerror("Error", f"Failed to load template: {str(e)}")
    
    def refresh_templates(self):
        """Refresh templates list"""
        self.templates_listbox.delete(0, tk.END)
        
        try:
            if config.TEMPLATES_DIR.exists():
                templates = list(config.TEMPLATES_DIR.glob("*.json"))
                templates.sort(key=lambda x: x.stat().st_mtime, reverse=True)  # Sort by modification time
                
                for template_file in templates:
                    self.templates_listbox.insert(tk.END, f"📝 {template_file.stem}")
        except Exception as e:
            print(f"Error refreshing templates: {e}")
    
    def load_selected_template(self):
        """Load selected template from list"""
        selection = self.templates_listbox.curselection()
        if not selection:
            showerror("Error", "Please select a template to load")
            return
        
        template_name = self.templates_listbox.get(selection[0]).replace("📝 ", "")
        template_file = config.TEMPLATES_DIR / f"{template_name}.json"
        
        try:
            import json
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            self.subject_var.set(template_data.get('subject', ''))
            self.body_text.delete(1.0, tk.END)
            self.body_text.insert(1.0, template_data.get('body', ''))
            
            # Load From email settings
            self.from_email_var.set(template_data.get('from_email', ''))
            self.from_name_var.set(template_data.get('from_name', ''))
            
            # Load signature setting
            self.include_signature_var.set(template_data.get('include_signature', True))
            
            # Load attachments if they exist
            saved_attachments = template_data.get('attachments', [])
            self.clear_attachments()
            for attachment in saved_attachments:
                if os.path.exists(attachment):
                    self.attachment_files.append(attachment)
                    self.attachments_listbox.insert(tk.END, f"📎 {os.path.basename(attachment)}")
            self.update_attachment_info()
            
            # Switch to main tab
            self.notebook.select(0)
            showinfo("Success", f"✅ Template '{template_name}' loaded\n\n"
                              f"📎 Attachments: {len(saved_attachments)}\n"
                              f"📝 Signature: {'Included' if template_data.get('include_signature', True) else 'Not included'}")
        except Exception as e:
            showerror("Error", f"Failed to load template: {str(e)}")
    
    def delete_template(self):
        """Delete selected template"""
        selection = self.templates_listbox.curselection()
        if not selection:
            showerror("Error", "Please select a template to delete")
            return
        
        template_name = self.templates_listbox.get(selection[0]).replace("📝 ", "")
        
        if askyesno("Confirm Delete", f"⚠️ Are you sure you want to delete template '{template_name}'?\n\n"
                                    f"This action cannot be undone."):
            try:
                template_file = config.TEMPLATES_DIR / f"{template_name}.json"
                template_file.unlink()
                self.refresh_templates()
                showinfo("Success", f"✅ Template '{template_name}' deleted")
            except Exception as e:
                showerror("Error", f"Failed to delete template: {str(e)}")
    
    def create_scheduled_job(self):
        """Create a new scheduled job"""
        if not self.authenticated:
            showerror("Error", "Please authenticate with Google first")
            return
        
        # Get job details
        job_name = self.job_name_var.get().strip()
        if not job_name:
            showerror("Error", "Please enter a job name")
            return
        
        # Get template data
        subject = self.subject_var.get().strip()
        body = self.body_text.get(1.0, tk.END).strip()
        
        if not subject or not body:
            showerror("Error", "Please enter email subject and body in the main tab")
            return
        
        # Get sheet data
        sheet_url = self.sheets_url_var.get().strip()
        sheet_name = self.sheet_name_var.get().strip()
        
        if not sheet_url or not sheet_name:
            showerror("Error", "Please configure Google Sheets in the main tab")
            return
        
        # Prepare schedule time
        schedule_type = self.schedule_type_var.get()
        schedule_time = self.schedule_time_var.get()
        
        if schedule_type == "once":
            schedule_date = self.schedule_date_var.get()
            try:
                datetime.datetime.strptime(f"{schedule_date} {schedule_time}", "%Y-%m-%d %H:%M")
                schedule_time = f"{schedule_date} {schedule_time}"
            except ValueError:
                showerror("Error", "Invalid date or time format")
                return
        
        try:
            job_id = self.scheduler.create_scheduled_job(
                job_name, schedule_type, schedule_time,
                subject, body, None,  # No HTML template for now
                sheet_url, sheet_name,
                self.batch_size_var.get(), self.time_gap_var.get()
            )
            
            if job_id:
                showinfo("Success", f"✅ Scheduled job '{job_name}' created successfully\n\n"
                                  f"📅 Type: {schedule_type}\n"
                                  f"⏰ Time: {schedule_time}")
                self.refresh_scheduled_jobs()
            else:
                showerror("Error", "Failed to create scheduled job")
        except Exception as e:
            showerror("Error", f"Failed to create scheduled job: {str(e)}")
    
    def refresh_scheduled_jobs(self):
        """Refresh scheduled jobs list"""
        # Clear existing items
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        
        # Add current jobs
        try:
            jobs = self.scheduler.get_scheduled_jobs()
            for job in jobs:
                next_run = self.scheduler.get_next_run_time(job['id'])
                next_run_str = next_run.strftime("%Y-%m-%d %H:%M") if next_run else "N/A"
                
                # Add status emoji
                status_emoji = {
                    'active': '🟢',
                    'completed': '✅',
                    'cancelled': '❌',
                    'failed': '🔴'
                }.get(job['status'], '⚪')
                
                self.jobs_tree.insert('', 'end', values=(
                    job['name'], 
                    job['schedule_type'].title(), 
                    job['schedule_time'], 
                    f"{status_emoji} {job['status'].title()}", 
                    next_run_str
                ))
        except Exception as e:
            print(f"Error refreshing jobs: {e}")
    
    def cancel_selected_job(self):
        """Cancel selected scheduled job"""
        selection = self.jobs_tree.selection()
        if not selection:
            showerror("Error", "Please select a job to cancel")
            return
        
        item = self.jobs_tree.item(selection[0])
        job_name = item['values'][0]
        
        if askyesno("Confirm Cancel", f"⚠️ Are you sure you want to cancel job '{job_name}'?\n\n"
                                    f"This will stop all future executions."):
            try:
                # Find job by name and cancel it
                jobs = self.scheduler.get_scheduled_jobs()
                for job in jobs:
                    if job['name'] == job_name:
                        if self.scheduler.cancel_job(job['id']):
                            showinfo("Success", f"✅ Job '{job_name}' cancelled")
                            self.refresh_scheduled_jobs()
                        else:
                            showerror("Error", "Failed to cancel job")
                        break
            except Exception as e:
                showerror("Error", f"Failed to cancel job: {str(e)}")
    
    def browse_credentials(self):
        """Browse for credentials file"""
        file_path = filedialog.askopenfilename(
            title="Select Google API Credentials File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.creds_path_var.set(file_path)
            # Update config (this is simplified - you might want to save this to a config file)
            config.CREDENTIALS_FILE = file_path
            showinfo("Success", "✅ Credentials file path updated")
    
    def open_setup_guide(self):
        """Open Google API setup guide"""
        webbrowser.open("https://developers.google.com/gmail/api/quickstart/python")
    
    def refresh_logs(self):
        """Refresh logs display"""
        self.logs_text.delete(1.0, tk.END)
        
        try:
            log_file = config.LOGS_DIR / 'email_sender.log'
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = f.read()
                    if logs:
                        self.logs_text.insert(1.0, logs)
                    else:
                        self.logs_text.insert(1.0, "📄 No log entries yet.\n\nLogs will appear here when you send emails.")
            else:
                self.logs_text.insert(1.0, "📄 Log file not found.\n\nLogs will be created when you send your first email.")
        except Exception as e:
            self.logs_text.insert(1.0, f"❌ Error reading logs: {e}")
    
    def clear_logs(self):
        """Clear log files"""
        if askyesno("Confirm Clear", "⚠️ Are you sure you want to clear all logs?\n\n"
                                   "This action cannot be undone."):
            try:
                log_file = config.LOGS_DIR / 'email_sender.log'
                if log_file.exists():
                    log_file.unlink()
                self.logs_text.delete(1.0, tk.END)
                self.logs_text.insert(1.0, "📄 Logs cleared.\n\nNew logs will appear here when you send emails.")
                showinfo("Success", "✅ Logs cleared")
            except Exception as e:
                showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Logs"
            )
            
            if file_path:
                log_content = self.logs_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"AutoMailer Pro v{config.APP_VERSION} - Log Export\n")
                    f.write(f"Exported: {datetime.datetime.now().isoformat()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(log_content)
                showinfo("Success", f"✅ Logs exported to {file_path}")
        except Exception as e:
            showerror("Error", f"Failed to export logs: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.sending_in_progress:
            if not askyesno("Confirm Exit", "⚠️ Email sending is in progress. Exit anyway?\n\n"
                                         "This will interrupt the current batch."):
                return
        
        # Stop scheduler
        self.scheduler.stop_scheduler()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    import tkinter.simpledialog
    app = AutoMailerGUI()
    app.run() 