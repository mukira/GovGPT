"""
Google Drive Service
Syncs documents from a specified Google Drive folder
"""
from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import List, Dict, Optional
import io


class GoogleDriveService:
    """Service for syncing documents from Google Drive folder"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Supported document types
    SUPPORTED_MIMETYPES = {
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'text/csv': '.csv',
        'application/vnd.google-apps.document': '.gdoc',  # Google Docs
        'application/vnd.google-apps.spreadsheet': '.gsheet',  # Google Sheets
    }
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize Google Drive service
        
        Args:
            credentials_path: Path to service account JSON file
        """
        self.credentials_path = credentials_path
        self.service = None
        
        if credentials_path:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive using service account"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive authenticated")
        except Exception as e:
            print(f"❌ Failed to authenticate with Google Drive: {e}")
            raise
    
    def list_folder_files(self, folder_id: str) -> List[Dict]:
        """
        List all supported documents in a Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            raise Exception("Google Drive service not authenticated")
        
        try:
            # Build query for supported file types
            mime_query = " or ".join([
                f"mimeType='{mime}'" 
                for mime in self.SUPPORTED_MIMETYPES.keys()
            ])
            
            query = f"'{folder_id}' in parents and ({mime_query}) and trashed=false"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            # Normalize file info
            normalized = []
            for file in files:
                normalized.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mime_type': file['mimeType'],
                    'extension': self.SUPPORTED_MIMETYPES.get(file['mimeType'], ''),
                    'modified': file.get('modifiedTime'),
                    'size': int(file.get('size', 0)) if file.get('size') else 0
                })
            
            print(f"✅ Found {len(normalized)} documents in folder")
            return normalized
            
        except Exception as e:
            print(f"❌ Error listing folder files: {e}")
            return []
    
    def download_file(self, file_id: str, mime_type: str) -> bytes:
        """
        Download file content from Google Drive
        
        Args:
            file_id: Google Drive file ID
            mime_type: File MIME type
            
        Returns:
            File content as bytes
        """
        if not self.service:
            raise Exception("Google Drive service not authenticated")
        
        try:
            # Handle Google Workspace files (export to standard formats)
            if mime_type == 'application/vnd.google-apps.document':
                # Export Google Doc as DOCX
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                # Export Google Sheet as XLSX
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                # Regular file download
                request = self.service.files().get_media(fileId=file_id)
            
            # Download to memory
            file_buffer = io.BytesIO()
            from googleapiclient.http import MediaIoBaseDownload
            
            downloader = MediaIoBaseDownload(file_buffer, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return file_buffer.getvalue()
            
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            raise
    
    def get_folder_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract folder ID from Google Drive URL
        
        Args:
            url: Google Drive folder URL
            
        Returns:
            Folder ID or None
        """
        # URL format: https://drive.google.com/drive/folders/FOLDER_ID
        if '/folders/' in url:
            return url.split('/folders/')[-1].split('?')[0]
        
        # Already just the ID
        if len(url) == 33 and '/' not in url:
            return url
        
        return None


# Singleton instance (will be initialized with credentials from env)
drive_service = GoogleDriveService()
