import base64
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os
import mimetypes
import re
from google_auth import GoogleAuthenticator
import config

# Setup logging
logging.basicConfig(
    filename=config.LOGS_DIR / 'email_sender.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EmailSender:
    def __init__(self):
        self.auth = GoogleAuthenticator()
        self.service = None
        self.sender_email = None
        self.sent_count = 0
        self.failed_count = 0
        self.max_attachment_size = 25 * 1024 * 1024  # 25MB Gmail limit
        self.gmail_aliases = []
        self.gmail_signature = ""
    
    def connect(self):
        """Connect to Gmail API"""
        try:
            self.auth.authenticate()
            self.service = self.auth.get_gmail_service()
            self.sender_email = self.auth.get_user_email()
            
            # Get Gmail aliases and signature
            self.get_gmail_aliases()
            self.get_gmail_signature()
            
            return True
        except Exception as e:
            logging.error(f"Error connecting to Gmail: {e}")
            return False
    
    def get_gmail_aliases(self):
        """Get available Gmail send-as aliases"""
        try:
            if not self.service:
                return []
            
            # Get send-as aliases (verified email addresses that can be used as 'from')
            result = self.service.users().settings().sendAs().list(userId='me').execute()
            aliases = result.get('sendAs', [])
            
            self.gmail_aliases = []
            for alias in aliases:
                if alias.get('verificationStatus') == 'accepted' or alias.get('isPrimary'):
                    self.gmail_aliases.append({
                        'email': alias.get('sendAsEmail'),
                        'name': alias.get('displayName', ''),
                        'signature': alias.get('signature', ''),
                        'is_primary': alias.get('isPrimary', False)
                    })
            
            logging.info(f"Found {len(self.gmail_aliases)} verified send-as addresses")
            return self.gmail_aliases
            
        except Exception as e:
            logging.error(f"Error getting Gmail aliases: {e}")
            return []
    
    def get_gmail_signature(self):
        """Extract Gmail signature from the primary account"""
        try:
            if not self.service:
                return ""
            
            # Get the primary send-as settings which includes signature
            result = self.service.users().settings().sendAs().list(userId='me').execute()
            send_as_list = result.get('sendAs', [])
            
            for send_as in send_as_list:
                if send_as.get('isPrimary'):
                    signature_html = send_as.get('signature', '')
                    if signature_html:
                        # Convert HTML signature to plain text
                        signature_text = self.html_to_text(signature_html)
                        self.gmail_signature = signature_text
                        logging.info("Gmail signature extracted successfully")
                        return signature_text
            
            # If no primary signature, try to get from Gmail settings
            try:
                settings = self.service.users().settings().get(userId='me').execute()
                if 'signature' in settings:
                    signature_html = settings['signature']
                    signature_text = self.html_to_text(signature_html)
                    self.gmail_signature = signature_text
                    return signature_text
            except:
                pass
            
            logging.info("No Gmail signature found")
            return ""
            
        except Exception as e:
            logging.error(f"Error getting Gmail signature: {e}")
            return ""
    
    def html_to_text(self, html):
        """Convert HTML to plain text"""
        if not html:
            return ""
        
        # Remove HTML tags
        text = re.sub('<.*?>', '', html)
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        # Clean up whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        return text
    
    def get_valid_from_email(self, requested_email, requested_name):
        """Get a valid from email that Gmail will accept"""
        if not requested_email:
            return self.sender_email, requested_name or ""
        
        # Check if requested email is in verified aliases
        for alias in self.gmail_aliases:
            if alias['email'].lower() == requested_email.lower():
                return requested_email, requested_name or alias['name']
        
        # If not found in aliases, use primary email but keep the requested name
        logging.warning(f"Email {requested_email} not in verified aliases. Using primary email: {self.sender_email}")
        return self.sender_email, requested_name or ""
    
    def validate_attachment(self, file_path):
        """Validate attachment file"""
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            file_size = os.path.getsize(file_path)
            if file_size > self.max_attachment_size:
                size_mb = file_size / (1024 * 1024)
                return False, f"File too large: {size_mb:.1f}MB (max 25MB)"
            
            if file_size == 0:
                return False, f"File is empty: {file_path}"
            
            return True, "Valid"
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def add_signature_to_body(self, body_text, include_signature=True):
        """Add Gmail signature to email body"""
        if not include_signature or not self.gmail_signature:
            return body_text
        
        # Add signature with proper spacing
        if body_text.strip():
            return f"{body_text}\n\n--\n{self.gmail_signature}"
        else:
            return f"{body_text}\n\n{self.gmail_signature}"
    
    def create_message(self, to_email, subject, body_text, body_html=None, attachments=None, 
                      from_email=None, from_name=None, include_signature=True):
        """Create email message with enhanced attachment support and proper from address handling"""
        try:
            # Get valid from email
            valid_from_email, valid_from_name = self.get_valid_from_email(from_email, from_name)
            
            # Add signature to body
            final_body_text = self.add_signature_to_body(body_text, include_signature)
            
            # Determine message type based on content
            if attachments or body_html:
                message = MIMEMultipart()
            else:
                message = MIMEText(final_body_text, 'plain', 'utf-8')
                message['to'] = to_email
                message['subject'] = subject
                
                # Set From header with validated email
                if valid_from_name:
                    message['from'] = f"{valid_from_name} <{valid_from_email}>"
                else:
                    message['from'] = valid_from_email
                
                return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            
            message['to'] = to_email
            message['subject'] = subject
            
            # Set From header for multipart messages
            if valid_from_name:
                message['from'] = f"{valid_from_name} <{valid_from_email}>"
            else:
                message['from'] = valid_from_email
            
            # Create multipart message for text/html content
            if body_html:
                msg_body = MIMEMultipart('alternative')
                
                # Add plain text part with signature
                part1 = MIMEText(final_body_text, 'plain', 'utf-8')
                msg_body.attach(part1)
                
                # Add HTML part with signature
                final_body_html = body_html
                if include_signature and self.gmail_signature:
                    # Convert signature to HTML for HTML emails
                    signature_html = self.gmail_signature.replace('\n', '<br>')
                    final_body_html = f"{body_html}<br><br>--<br>{signature_html}"
                
                part2 = MIMEText(final_body_html, 'html', 'utf-8')
                msg_body.attach(part2)
                
                message.attach(msg_body)
            else:
                # Add plain text only with signature
                text_part = MIMEText(final_body_text, 'plain', 'utf-8')
                message.attach(text_part)
            
            # Handle attachments
            if attachments:
                total_size = 0
                for file_path in attachments:
                    try:
                        # Validate attachment
                        is_valid, error_msg = self.validate_attachment(file_path)
                        if not is_valid:
                            logging.warning(f"Skipping invalid attachment: {error_msg}")
                            continue
                        
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # Check total attachment size
                        if total_size > self.max_attachment_size:
                            logging.warning(f"Total attachment size exceeds 25MB limit, skipping: {file_path}")
                            continue
                        
                        # Determine MIME type
                        mime_type, encoding = mimetypes.guess_type(file_path)
                        if mime_type is None:
                            mime_type = 'application/octet-stream'
                        
                        main_type, sub_type = mime_type.split('/', 1)
                        
                        # Read and attach file
                        with open(file_path, "rb") as attachment_file:
                            if main_type == 'application':
                                part = MIMEApplication(
                                    attachment_file.read(),
                                    _subtype=sub_type
                                )
                            else:
                                part = MIMEBase(main_type, sub_type)
                                part.set_payload(attachment_file.read())
                                encoders.encode_base64(part)
                        
                        # Add header with filename
                        filename = os.path.basename(file_path)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{filename}"'
                        )
                        
                        message.attach(part)
                        logging.info(f"Attached file: {filename} ({file_size} bytes)")
                        
                    except Exception as e:
                        logging.error(f"Error attaching file {file_path}: {e}")
                        continue
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return {'raw': raw_message}
            
        except Exception as e:
            logging.error(f"Error creating message: {e}")
            return None
    
    def send_message(self, message):
        """Send email message"""
        try:
            if not self.service:
                if not self.connect():
                    return False
            
            sent_message = self.service.users().messages().send(
                userId="me", body=message
            ).execute()
            
            logging.info(f"Message sent. ID: {sent_message['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            return False
    
    def send_bulk_emails(self, sheet_data, template_subject, template_body, 
                        template_html=None, batch_size=None, time_gap=None, 
                        progress_callback=None, attachments=None, from_email=None, 
                        from_name=None, include_signature=True):
        """Send bulk emails with batch processing and time gaps"""
        
        if not batch_size:
            batch_size = config.DEFAULT_BATCH_SIZE
        if not time_gap:
            time_gap = config.DEFAULT_TIME_GAP
        
        # Extract data from sheet_data structure
        if not sheet_data or 'data' not in sheet_data:
            logging.error("Invalid sheet data structure")
            return 0, 0
        
        email_data = sheet_data['data']
        total_emails = len(email_data)
        self.sent_count = 0
        self.failed_count = 0
        
        # Get valid from email
        valid_from_email, valid_from_name = self.get_valid_from_email(from_email, from_name)
        
        logging.info(f"Starting bulk email send: {total_emails} emails")
        logging.info(f"Using sender: {valid_from_name} <{valid_from_email}>" if valid_from_name else f"Using sender: {valid_from_email}")
        if attachments:
            logging.info(f"Attachments: {', '.join(attachments)}")
        if include_signature and self.gmail_signature:
            logging.info("Including Gmail signature")
        
        for i, row in enumerate(email_data):
            try:
                # Check if email column exists
                email_col = None
                for col in row.keys():
                    if 'email' in col.lower() or 'mail' in col.lower():
                        email_col = col
                        break
                
                if not email_col:
                    logging.error(f"No email column found in row {i}")
                    self.failed_count += 1
                    continue
                
                recipient_email = row[email_col]
                if not recipient_email or '@' not in str(recipient_email):
                    logging.error(f"Invalid email address: {recipient_email}")
                    self.failed_count += 1
                    continue
                
                # Replace placeholders in subject and body
                from sheets_handler import SheetsHandler
                sheets_handler = SheetsHandler()
                
                personalized_subject = sheets_handler.replace_placeholders(template_subject, row)
                personalized_body = sheets_handler.replace_placeholders(template_body, row)
                personalized_html = None
                
                if template_html:
                    personalized_html = sheets_handler.replace_placeholders(template_html, row)
                
                # Create and send message
                message = self.create_message(
                    recipient_email, 
                    personalized_subject, 
                    personalized_body,
                    personalized_html,
                    attachments,
                    valid_from_email,
                    valid_from_name,
                    include_signature
                )
                
                if message and self.send_message(message):
                    self.sent_count += 1
                    logging.info(f"Email sent to: {recipient_email}")
                else:
                    self.failed_count += 1
                    logging.error(f"Failed to send email to: {recipient_email}")
                
                # Update progress
                if progress_callback:
                    progress = ((self.sent_count + self.failed_count) / total_emails) * 100
                    progress_callback(progress, self.sent_count, self.failed_count)
                
                # Add time gap between emails (except for last email)
                if i < len(email_data) - 1:
                    time.sleep(time_gap)
                
                # Batch processing - longer pause after each batch
                if (self.sent_count + self.failed_count) % batch_size == 0:
                    logging.info(f"Completed batch. Pausing for 10 seconds...")
                    time.sleep(10)
                    
            except Exception as e:
                logging.error(f"Error processing row {i}: {e}")
                self.failed_count += 1
        
        logging.info(f"Bulk email send completed. Sent: {self.sent_count}, Failed: {self.failed_count}")
        return self.sent_count, self.failed_count
    
    def send_single_email(self, to_email, subject, body, html_body=None, attachments=None, 
                         from_email=None, from_name=None, include_signature=True):
        """Send a single email with attachments and proper from address"""
        try:
            message = self.create_message(to_email, subject, body, html_body, attachments, 
                                        from_email, from_name, include_signature)
            if message:
                return self.send_message(message)
            return False
        except Exception as e:
            logging.error(f"Error sending single email: {e}")
            return False
    
    def send_scheduled_email(self, sheet_data, template_subject, template_body, 
                           send_datetime, template_html=None, batch_size=None, time_gap=None, 
                           attachments=None, from_email=None, from_name=None, include_signature=True):
        """Schedule an email to be sent at a specific datetime"""
        try:
            import datetime
            import threading
            
            if isinstance(send_datetime, str):
                send_datetime = datetime.datetime.fromisoformat(send_datetime)
            
            current_time = datetime.datetime.now()
            if send_datetime <= current_time:
                # Send immediately if the time has passed
                return self.send_bulk_emails(
                    sheet_data, template_subject, template_body, 
                    template_html, batch_size, time_gap, 
                    None, attachments, from_email, from_name, include_signature
                )
            
            # Calculate delay
            delay = (send_datetime - current_time).total_seconds()
            
            def delayed_send():
                time.sleep(delay)
                self.send_bulk_emails(
                    sheet_data, template_subject, template_body, 
                    template_html, batch_size, time_gap, 
                    None, attachments, from_email, from_name, include_signature
                )
            
            # Start the delayed send in a background thread
            thread = threading.Thread(target=delayed_send, daemon=True)
            thread.start()
            
            logging.info(f"Email scheduled for {send_datetime}")
            return True
            
        except Exception as e:
            logging.error(f"Error scheduling email: {e}")
            return False
    
    def get_stats(self):
        """Get sending statistics"""
        return {
            'sent': self.sent_count,
            'failed': self.failed_count,
            'total': self.sent_count + self.failed_count
        } 