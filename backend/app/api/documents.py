"""
Documents API Endpoints
Manages Google Drive document syncing
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import hashlib

from app.services.google_drive_service import drive_service
from app.services.document_service import document_processor
from app.services.vector_service import vector_service

router = APIRouter()


class DriveFolderRequest(BaseModel):
    folder_url_or_id: str


class SyncResponse(BaseModel):
    synced_count: int
    processed_count: int
    failed_count: int
    documents: List[dict]


@router.post("/sync", response_model=SyncResponse)
async def sync_drive_folder(request: DriveFolderRequest):
    """
    Sync documents from Google Drive folder
    
    Request body:
    - folder_url_or_id: Google Drive folder URL or ID
    """
    try:
        # Extract folder ID
        folder_id = drive_service.get_folder_id_from_url(request.folder_url_or_id)
        if not folder_id:
            raise HTTPException(status_code=400, detail="Invalid folder URL or ID")
        
        # List files in folder
        files = drive_service.list_folder_files(folder_id)
        
        synced = []
        processed = 0
        failed = 0
        
        for file in files:
            try:
                # Download file
                file_bytes = drive_service.download_file(
                    file['id'],
                    file['mime_type']
                )
                
                # Process document
                doc_info = document_processor.process_document(
                    file_bytes,
                    file['name'],
                    file['mime_type']
                )
                
                # Store in vector database
                doc_id = hashlib.md5(file['id'].encode()).hexdigest()
                vector_service.store_chunks(doc_info['chunks'], doc_id)
                
                synced.append({
                    'id': doc_id,
                    'name': file['name'],
                    'type': doc_info['type'],
                    'chunks': doc_info['chunk_count'],
                    'size': file['size']
                })
                processed += 1
                
            except Exception as e:
                print(f"Failed to process {file['name']}: {e}")
                failed += 1
        
        return {
            'synced_count': len(files),
            'processed_count': processed,
            'failed_count': failed,
            'documents': synced
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_documents():
    """List all synced documents (from vector DB metadata)"""
    try:
        # TODO: Implement listing from Qdrant collection
        # For now, return placeholder
        return {
            "message": "Document listing not yet implemented",
            "documents": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Remove document from vector database"""
    try:
        vector_service.delete_document(doc_id)
        return {"message": f"Document {doc_id} deleted", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
