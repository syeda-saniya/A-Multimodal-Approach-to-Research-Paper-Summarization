import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .utils.pdf_process import PDFProcessor
import shutil
from pathlib import Path

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="PDF Extractor API",
    description="API for extracting and processing text from PDF files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/", )
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    Returns extracted sections including Abstract and main content sections.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        pdf_processor = PDFProcessor()
        extracted_text = pdf_processor.process_pdf(str(file_path))
        
        # Clean up
        os.remove(file_path)
        
        return {
            "message": "File successfully processed",
            "sections": extracted_text
        }
    
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)