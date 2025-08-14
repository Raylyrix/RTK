import re
from googleapiclient.discovery import build
from google_auth import GoogleAuthenticator

class SheetsHandler:
    def __init__(self):
        self.auth = GoogleAuthenticator()
        self.service = None
    
    def connect(self):
        """Connect to Google Sheets API"""
        try:
            self.auth.authenticate()
            self.service = self.auth.get_sheets_service()
            return True
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False
    
    def extract_sheet_id(self, url):
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
    
    def get_sheet_data(self, spreadsheet_url, sheet_name=None, range_name=None):
        """Get data from Google Sheets"""
        try:
            if not self.service:
                if not self.connect():
                    return None
            
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            if not sheet_id:
                raise ValueError("Invalid Google Sheets URL")
            
            # Get sheet metadata to find sheet names
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', '')
            
            if not sheet_name:
                # Use first sheet if no name specified
                sheet_name = sheets[0]['properties']['title']
            
            # Construct range
            if range_name:
                range_query = f"{sheet_name}!{range_name}"
            else:
                range_query = sheet_name
            
            # Get values
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_query
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return None
            
            # Convert to list of dictionaries (like DataFrame records)
            headers = values[0]  # First row as headers
            data = []
            for row in values[1:]:
                # Pad row with empty strings if it's shorter than headers
                while len(row) < len(headers):
                    row.append('')
                
                row_dict = {}
                for i, header in enumerate(headers):
                    # Clean header names and store both original and cleaned versions
                    clean_header = str(header).strip()
                    value = str(row[i]).strip() if i < len(row) and row[i] else ''
                    row_dict[clean_header] = value
                data.append(row_dict)
            
            return {
                'headers': headers,
                'data': data
            }
            
        except Exception as e:
            print(f"Error reading sheet data: {e}")
            return None
    
    def get_available_sheets(self, spreadsheet_url):
        """Get list of available sheets in spreadsheet"""
        try:
            if not self.service:
                if not self.connect():
                    return []
            
            sheet_id = self.extract_sheet_id(spreadsheet_url)
            if not sheet_id:
                return []
            
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            return [sheet['properties']['title'] for sheet in sheets]
            
        except Exception as e:
            print(f"Error getting sheet names: {e}")
            return []
    
    def find_placeholders(self, text):
        """Find placeholders in text format ((placeholder))"""
        try:
            if not text or not isinstance(text, str):
                return []
            
            # More robust regex to handle spaces and special characters
            pattern = r'\(\(([^)]+)\)\)'
            placeholders = re.findall(pattern, text)
            # Clean up placeholder names (strip spaces)
            cleaned_placeholders = [p.strip() for p in placeholders]
            return list(set(cleaned_placeholders))  # Remove duplicates
        except Exception as e:
            print(f"Error finding placeholders: {e}")
            return []
    
    def replace_placeholders(self, template, row_data):
        """Replace placeholders with actual data from row"""
        try:
            if not template or not isinstance(template, str):
                return template or ""
            
            if not row_data or not isinstance(row_data, dict):
                return template
            
            result = template
            
            # Find all placeholders
            placeholders = self.find_placeholders(template)
            
            for placeholder in placeholders:
                replacement_value = ""
                placeholder_found = False
                
                # Try exact match first
                if placeholder in row_data:
                    replacement_value = str(row_data[placeholder]) if row_data[placeholder] else ""
                    placeholder_found = True
                else:
                    # Try case-insensitive match
                    placeholder_lower = placeholder.lower().strip()
                    for col in row_data.keys():
                        col_lower = col.lower().strip()
                        if col_lower == placeholder_lower:
                            replacement_value = str(row_data[col]) if row_data[col] else ""
                            placeholder_found = True
                            break
                    
                    # Try partial match (for cases like "company name" matching "Company")
                    if not placeholder_found:
                        for col in row_data.keys():
                            col_lower = col.lower().strip()
                            if placeholder_lower in col_lower or col_lower in placeholder_lower:
                                replacement_value = str(row_data[col]) if row_data[col] else ""
                                placeholder_found = True
                                break
                
                if not placeholder_found:
                    replacement_value = f"[{placeholder}]"  # Show missing placeholder
                
                # Replace placeholder with value
                result = result.replace(f"(({placeholder}))", replacement_value)
            
            return result
            
        except Exception as e:
            print(f"Error replacing placeholders: {e}")
            return template or ""
    
    def validate_placeholders(self, template, sheet_data):
        """Validate that all placeholders exist in the sheet headers"""
        try:
            if not sheet_data or 'headers' not in sheet_data:
                return []
            
            placeholders = self.find_placeholders(template)
            headers = [str(h).strip() for h in sheet_data['headers']]
            headers_lower = [h.lower() for h in headers]
            
            missing_placeholders = []
            for placeholder in placeholders:
                placeholder_lower = placeholder.lower().strip()
                found = False
                
                # Check exact match
                if placeholder in headers:
                    found = True
                # Check case-insensitive match
                elif placeholder_lower in headers_lower:
                    found = True
                # Check partial match
                else:
                    for header_lower in headers_lower:
                        if placeholder_lower in header_lower or header_lower in placeholder_lower:
                            found = True
                            break
                
                if not found:
                    missing_placeholders.append(placeholder)
            
            return missing_placeholders
            
        except Exception as e:
            print(f"Error validating placeholders: {e}")
            return []
    
    def get_column_suggestions(self, placeholder, sheet_data):
        """Get column suggestions for a placeholder"""
        try:
            if not sheet_data or 'headers' not in sheet_data:
                return []
            
            headers = [str(h).strip() for h in sheet_data['headers']]
            placeholder_lower = placeholder.lower().strip()
            suggestions = []
            
            for header in headers:
                header_lower = header.lower().strip()
                # Check if placeholder words are in header or vice versa
                placeholder_words = placeholder_lower.split()
                header_words = header_lower.split()
                
                for p_word in placeholder_words:
                    for h_word in header_words:
                        if p_word in h_word or h_word in p_word:
                            if header not in suggestions:
                                suggestions.append(header)
            
            return suggestions[:5]  # Return top 5 suggestions
        except Exception as e:
            print(f"Error getting column suggestions: {e}")
            return [] 