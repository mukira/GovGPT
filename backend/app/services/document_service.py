"""
Document Processing Service
Extracts text from PDF, Word, Excel, and CSV documents
"""
import fitz  # PyMuPDF
from docx import Document
import pandas as pd
from typing import List, Dict
import re


class DocumentProcessor:
    """Process different document types and extract text"""
    
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def process_pdf(self, file_bytes: bytes, filename: str) -> Dict:
        """Extract text from PDF"""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            doc.close()
            
            return {
                'filename': filename,
                'type': 'pdf',
                'text': full_text,
                'page_count': len(text_parts),
                'char_count': len(full_text)
            }
        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise
    
    def process_docx(self, file_bytes: bytes, filename: str) -> Dict:
        """Extract text from Word document"""
        try:
            import io
            doc = Document(io.BytesIO(file_bytes))
            
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            full_text = "\n\n".join(text_parts)
            
            return {
                'filename': filename,
                'type': 'docx',
                'text': full_text,
                'paragraph_count': len(text_parts),
                'char_count': len(full_text)
            }
        except Exception as e:
            print(f"Error processing DOCX: {e}")
            raise
    
    def process_excel(self, file_bytes: bytes, filename: str) -> Dict:
        """Extract text from Excel file"""
        try:
            import io
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
            
            text_parts = []
            for sheet_name, sheet_df in df.items():
                text_parts.append(f"## {sheet_name}\n")
                text_parts.append(sheet_df.to_string())
            
            full_text = "\n\n".join(text_parts)
            
            return {
                'filename': filename,
                'type': 'xlsx',
                'text': full_text,
                'sheet_count': len(df),
                'char_count': len(full_text)
            }
        except Exception as e:
            print(f"Error processing Excel: {e}")
            raise
    
    def process_csv(self, file_bytes: bytes, filename: str) -> Dict:
        """Extract text from CSV file"""
        try:
            import io
            df = pd.read_csv(io.BytesIO(file_bytes))
            full_text = df.to_string()
            
            return {
                'filename': filename,
                'type': 'csv',
                'text': full_text,
                'row_count': len(df),
                'char_count': len(full_text)
            }
        except Exception as e:
            print(f"Error processing CSV: {e}")
            raise
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full document text
            metadata: Document metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to end at sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                boundary = max(last_period, last_newline)
                
                if boundary > self.chunk_size // 2:
                    chunk_text = chunk_text[:boundary + 1]
                    end = start + boundary + 1
            
            chunk = {
                'chunk_id': chunk_id,
                'text': chunk_text.strip(),
                'start': start,
                'end': end,
                'char_count': len(chunk_text)
            }
            
            if metadata:
                chunk.update(metadata)
            
            chunks.append(chunk)
            chunk_id += 1
            
            # Move start with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_document(self, file_bytes: bytes, filename: str, mime_type: str) -> Dict:
        """
        Process document based on type
        
        Args:
            file_bytes: Document content as bytes
            filename: Original filename
            mime_type: Document MIME type
            
        Returns:
            Processed document with text and chunks
        """
        # Map MIME types to processors
        processors = {
            'application/pdf': self.process_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self.process_docx,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': self.process_excel,
            'text/csv': self.process_csv,
        }
        
        processor = processors.get(mime_type)
        if not processor:
            raise ValueError(f"Unsupported document type: {mime_type}")
        
        # Extract text
        doc_info = processor(file_bytes, filename)
        
        # Create chunks
        chunks = self.chunk_text(
            doc_info['text'],
            metadata={
                'filename': filename,
                'type': doc_info['type']
            }
        )
        
        doc_info['chunks'] = chunks
        doc_info['chunk_count'] = len(chunks)
        
        return doc_info


# Singleton instance
document_processor = DocumentProcessor()
