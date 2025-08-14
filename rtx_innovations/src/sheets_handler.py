"""
RTX Innovations - Enhanced Google Sheets Handler
Full data editing, status tracking, and batch management
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import STATUS_COLUMNS, DATA_CONFIG, SHEETS_CONFIG
from google_auth import auth_manager

class SheetsHandler:
    """Enhanced Google Sheets handler with full CRUD operations"""
    
    def __init__(self):
        self.service = None
        self.current_spreadsheet_id = None
        self.current_sheet_name = None
        self.sheet_data = None
        self.status_columns_added = False
        self.batch_labels = {}
        self.edit_history = []
        
    def connect(self) -> bool:
        """Connect to Google Sheets API"""
        try:
            if not auth_manager.get_current_account():
                print("❌ No authenticated account")
                return False
            
            self.service = auth_manager.get_service('sheets')
            return True if self.service else False
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {e}")
            return False
    
    def extract_sheet_id(self, url: str) -> Optional[str]:
        """Extract sheet ID from Google Sheets URL"""
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'key=([a-zA-Z0-9-_]+)',
            r'^([a-zA-Z0-9-_]+)$'  # Direct ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_available_sheets(self, spreadsheet_url: str) -> List[str]:
        """Get list of available sheets in spreadsheet"""
        try:
            if not self.connect():
                return []
            
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            if not sheet_id:
                print("❌ Invalid Google Sheets URL")
                return []
            
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            
            print(f"✅ Found {len(sheet_names)} sheets")
            return sheet_names
            
        except Exception as e:
            print(f"❌ Error getting sheet names: {e}")
            return []
    
    def load_sheet_data(self, spreadsheet_url: str, sheet_name: str = None) -> bool:
        """Load complete sheet data with status columns"""
        try:
            if not self.connect():
                return False
            
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            if not sheet_id:
                print("❌ Invalid Google Sheets URL")
                return False
            
            # Store current spreadsheet info
            self.current_spreadsheet_id = sheet_id
            self.current_sheet_name = sheet_name
            
            # Get sheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            
            if not sheet_name:
                # Use first sheet if no name specified
                sheet_name = sheets[0]['properties']['title']
                self.current_sheet_name = sheet_name
            
            # Get all data from the sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print("❌ No data found in sheet")
                return False
            
            # Convert to DataFrame for easier manipulation
            headers = values[0]
            data_rows = values[1:]
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Add status columns if they don't exist
            df = self.add_status_columns(df)
            
            # Store data
            self.sheet_data = {
                'headers': headers,
                'data': df.to_dict('records'),
                'dataframe': df,
                'total_rows': len(df),
                'last_loaded': datetime.now()
            }
            
            print(f"✅ Loaded {len(df)} rows from sheet '{sheet_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error loading sheet data: {e}")
            return False
    
    def add_status_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add status tracking columns to the DataFrame"""
        for col_name, display_name in STATUS_COLUMNS.items():
            if display_name not in df.columns:
                df[display_name] = ''
        
        # Add batch label column if enabled
        if SHEETS_CONFIG['enable_batch_labels']:
            if 'Batch Label' not in df.columns:
                df['Batch Label'] = ''
        
        return df
    
    def get_sheet_data(self, spreadsheet_url: str, sheet_name: str = None) -> Optional[Dict[str, Any]]:
        """Get sheet data (backward compatibility)"""
        if self.load_sheet_data(spreadsheet_url, sheet_name):
            return self.sheet_data
        return None
    
    def get_data_preview(self, max_rows: int = None) -> Optional[Dict[str, Any]]:
        """Get data preview with all columns and rows"""
        if not self.sheet_data:
            return None
        
        max_rows = max_rows or DATA_CONFIG['max_preview_rows']
        df = self.sheet_data['dataframe']
        
        # Get preview data
        preview_df = df.head(max_rows)
        
        return {
            'headers': list(preview_df.columns),
            'data': preview_df.values.tolist(),
            'total_rows': len(df),
            'preview_rows': len(preview_df),
            'columns_count': len(df.columns)
        }
    
    def edit_cell_value(self, row_index: int, column_name: str, new_value: str) -> bool:
        """Edit a single cell value"""
        try:
            if not self.service or not self.current_spreadsheet_id:
                print("❌ Not connected to Google Sheets")
                return False
            
            if not self.sheet_data:
                print("❌ No sheet data loaded")
                return False
            
            # Find the column index
            headers = self.sheet_data['headers']
            if column_name not in headers:
                print(f"❌ Column '{column_name}' not found")
                return False
            
            col_index = headers.index(column_name)
            
            # Update local data
            if 0 <= row_index < len(self.sheet_data['data']):
                self.sheet_data['data'][row_index][column_name] = new_value
                self.sheet_data['dataframe'].iloc[row_index, col_index] = new_value
            
            # Update Google Sheets
            range_name = f"{self.current_sheet_name}!{chr(65 + col_index)}{row_index + 2}"
            
            body = {
                'values': [[new_value]]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.current_spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Record edit history
            self.record_edit(row_index, column_name, new_value)
            
            print(f"✅ Updated cell ({row_index}, {column_name}) = {new_value}")
            return True
            
        except Exception as e:
            print(f"❌ Error editing cell: {e}")
            return False
    
    def edit_multiple_cells(self, edits: List[Tuple[int, str, str]]) -> bool:
        """Edit multiple cells in batch"""
        try:
            if not self.service or not self.current_spreadsheet_id:
                print("❌ Not connected to Google Sheets")
                return False
            
            if not edits:
                return True
            
            # Prepare batch update
            batch_body = {
                'valueInputOption': 'RAW',
                'data': []
            }
            
            for row_index, column_name, new_value in edits:
                if column_name in self.sheet_data['headers']:
                    col_index = self.sheet_data['headers'].index(column_name)
                    range_name = f"{self.current_sheet_name}!{chr(65 + col_index)}{row_index + 2}"
                    
                    batch_body['data'].append({
                        'range': range_name,
                        'values': [[new_value]]
                    })
                    
                    # Update local data
                    if 0 <= row_index < len(self.sheet_data['data']):
                        self.sheet_data['data'][row_index][column_name] = new_value
                        self.sheet_data['dataframe'].iloc[row_index, col_index] = new_value
            
            # Execute batch update
            if batch_body['data']:
                self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.current_spreadsheet_id,
                    body=batch_body
                ).execute()
                
                # Record edit history
                for row_index, column_name, new_value in edits:
                    self.record_edit(row_index, column_name, new_value)
                
                print(f"✅ Updated {len(edits)} cells in batch")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error in batch edit: {e}")
            return False
    
    def add_status_column(self, column_name: str, default_value: str = '') -> bool:
        """Add a new status column to the sheet"""
        try:
            if not self.service or not self.current_spreadsheet_id:
                print("❌ Not connected to Google Sheets")
                return False
            
            # Add column to local data
            if column_name not in self.sheet_data['headers']:
                self.sheet_data['headers'].append(column_name)
                
                # Add column to DataFrame
                self.sheet_data['dataframe'][column_name] = default_value
                
                # Add column to all data rows
                for row in self.sheet_data['data']:
                    row[column_name] = default_value
            
            # Add column to Google Sheets
            requests = [{
                'insertDimension': {
                    'range': {
                        'sheetId': self.get_sheet_id_by_name(self.current_sheet_name),
                        'dimension': 'COLUMNS',
                        'startIndex': len(self.sheet_data['headers']) - 1,
                        'endIndex': len(self.sheet_data['headers'])
                    }
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.current_spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            # Update header row
            header_range = f"{self.current_sheet_name}!A1:{chr(65 + len(self.sheet_data['headers']) - 1)}1"
            header_body = {
                'values': [self.sheet_data['headers']]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.current_spreadsheet_id,
                range=header_range,
                valueInputOption='RAW',
                body=header_body
            ).execute()
            
            print(f"✅ Added status column: {column_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding status column: {e}")
            return False
    
    def get_sheet_id_by_name(self, sheet_name: str) -> Optional[int]:
        """Get sheet ID by name"""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.current_spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return None
        except Exception:
            return None
    
    def update_email_status(self, row_index: int, status: str, additional_info: Dict[str, Any] = None) -> bool:
        """Update email status for a specific row"""
        try:
            if not self.sheet_data:
                print("❌ No sheet data loaded")
                return False
            
            updates = []
            
            # Update email status
            if 'Email Status' in self.sheet_data['headers']:
                updates.append((row_index, 'Email Status', status))
            
            # Update sent date and time
            if status in ['Sent', 'Delivered']:
                now = datetime.now()
                if 'Sent Date' in self.sheet_data['headers']:
                    updates.append((row_index, 'Sent Date', now.strftime('%Y-%m-%d')))
                if 'Sent Time' in self.sheet_data['headers']:
                    updates.append((row_index, 'Sent Time', now.strftime('%H:%M:%S')))
            
            # Update additional info
            if additional_info:
                for key, value in additional_info.items():
                    if key in self.sheet_data['headers']:
                        updates.append((row_index, key, str(value)))
            
            # Execute updates
            if updates:
                return self.edit_multiple_cells(updates)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating email status: {e}")
            return False
    
    def create_batch_label(self, batch_name: str, row_indices: List[int]) -> bool:
        """Create a batch label for specific rows"""
        try:
            if not SHEETS_CONFIG['enable_batch_labels']:
                print("❌ Batch labels are disabled")
                return False
            
            # Add batch label column if it doesn't exist
            if 'Batch Label' not in self.sheet_data['headers']:
                self.add_status_column('Batch Label')
            
            # Update batch labels
            updates = []
            for row_index in row_indices:
                updates.append((row_index, 'Batch Label', batch_name))
            
            # Store batch info
            self.batch_labels[batch_name] = {
                'row_indices': row_indices,
                'created_at': datetime.now(),
                'status': 'Active'
            }
            
            return self.edit_multiple_cells(updates)
            
        except Exception as e:
            print(f"❌ Error creating batch label: {e}")
            return False
    
    def get_batch_data(self, batch_name: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific batch"""
        if batch_name not in self.batch_labels:
            return None
        
        batch_info = self.batch_labels[batch_name]
        row_indices = batch_info['row_indices']
        
        batch_data = []
        for row_index in row_indices:
            if 0 <= row_index < len(self.sheet_data['data']):
                batch_data.append(self.sheet_data['data'][row_index])
        
        return {
            'batch_name': batch_name,
            'row_count': len(batch_data),
            'data': batch_data,
            'created_at': batch_info['created_at'],
            'status': batch_info['status']
        }
    
    def get_all_batches(self) -> Dict[str, Dict[str, Any]]:
        """Get all batch information"""
        return self.batch_labels
    
    def delete_batch(self, batch_name: str) -> bool:
        """Delete a batch label"""
        try:
            if batch_name not in self.batch_labels:
                print(f"❌ Batch '{batch_name}' not found")
                return False
            
            # Remove batch labels from rows
            row_indices = self.batch_labels[batch_name]['row_indices']
            updates = []
            for row_index in row_indices:
                updates.append((row_index, 'Batch Label', ''))
            
            # Execute updates
            if updates:
                self.edit_multiple_cells(updates)
            
            # Remove batch info
            del self.batch_labels[batch_name]
            
            print(f"✅ Deleted batch: {batch_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting batch: {e}")
            return False
    
    def record_edit(self, row_index: int, column_name: str, new_value: str):
        """Record edit history"""
        edit_record = {
            'timestamp': datetime.now(),
            'row_index': row_index,
            'column_name': column_name,
            'new_value': new_value,
            'user': auth_manager.get_current_account().email if auth_manager.get_current_account() else 'Unknown'
        }
        
        self.edit_history.append(edit_record)
        
        # Keep only last 1000 edits
        if len(self.edit_history) > 1000:
            self.edit_history = self.edit_history[-1000:]
    
    def get_edit_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get edit history"""
        return self.edit_history[-limit:] if self.edit_history else []
    
    def export_data(self, format: str = 'xlsx', file_path: str = None) -> bool:
        """Export sheet data to file"""
        try:
            if not self.sheet_data:
                print("❌ No sheet data to export")
                return False
            
            df = self.sheet_data['dataframe']
            
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = f"sheet_data_{timestamp}.{format}"
            
            if format.lower() == 'xlsx':
                df.to_excel(file_path, index=False)
            elif format.lower() == 'csv':
                df.to_csv(file_path, index=False)
            elif format.lower() == 'json':
                df.to_json(file_path, orient='records', indent=2)
            else:
                print(f"❌ Unsupported format: {format}")
                return False
            
            print(f"✅ Exported data to: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate sheet data"""
        if not self.sheet_data:
            return {'valid': False, 'errors': ['No data loaded']}
        
        df = self.sheet_data['dataframe']
        errors = []
        warnings = []
        
        # Check for required columns
        required_columns = ['Email', 'email', 'mail']
        email_column = None
        for col in required_columns:
            if col in df.columns:
                email_column = col
                break
        
        if not email_column:
            errors.append("No email column found")
        else:
            # Validate email format
            invalid_emails = []
            for idx, email in enumerate(df[email_column]):
                if email and '@' not in str(email):
                    invalid_emails.append(f"Row {idx + 2}: {email}")
            
            if invalid_emails:
                warnings.append(f"Found {len(invalid_emails)} invalid emails")
        
        # Check for empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            warnings.append(f"Found {empty_rows} empty rows")
        
        # Check data types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed data types
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if 0 < numeric_count < len(df):
                    warnings.append(f"Column '{col}' has mixed data types")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }
    
    def refresh_data(self) -> bool:
        """Refresh sheet data from Google Sheets"""
        if self.current_spreadsheet_id and self.current_sheet_name:
            return self.load_sheet_data(
                f"https://docs.google.com/spreadsheets/d/{self.current_spreadsheet_id}",
                self.current_sheet_name
            )
        return False
    
    def get_sheet_summary(self) -> Dict[str, Any]:
        """Get comprehensive sheet summary"""
        if not self.sheet_data:
            return {}
        
        df = self.sheet_data['dataframe']
        
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'last_loaded': self.sheet_data.get('last_loaded'),
            'spreadsheet_id': self.current_spreadsheet_id,
            'sheet_name': self.current_sheet_name,
            'column_info': {},
            'batch_info': {
                'total_batches': len(self.batch_labels),
                'batch_names': list(self.batch_labels.keys())
            },
            'edit_info': {
                'total_edits': len(self.edit_history),
                'last_edit': self.edit_history[-1] if self.edit_history else None
            }
        }
        
        # Column information
        for col in df.columns:
            summary['column_info'][col] = {
                'data_type': str(df[col].dtype),
                'non_null_count': df[col].notna().sum(),
                'unique_values': df[col].nunique(),
                'sample_values': df[col].dropna().head(3).tolist()
            }
        
        return summary 