import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .utils.figures_context import extract_paragraphs_with_figures_from_sections
from .utils.pdf_process import PDFProcessor
from .utils.image_extraction import PDFImageExtractor
import shutil
from pathlib import Path
import asyncio
import shutil
import asyncio
import httpx
from typing import Dict

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="PDF Extractor API",
    description="API for extracting and processing text from PDF files",
    version="1.0.0"
)

NGROK_URL = "https://ae99-35-201-134-19.ngrok-free.app/summarize"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_summaries(sections: Dict[str, str]) -> Dict[str, str]:
    """
    Get summaries for sections from ngrok service
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                NGROK_URL,
                json={"sections": sections},
                timeout=300  # 5 minutes timeout for long texts
            )
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'success':
                return result['summaries']
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error from summarization service: {result.get('error', 'Unknown error')}"
                )
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Summarization service timeout"
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with summarization service: {str(e)}"
            )


async def remove_file(file_path: Path, max_attempts: int = 5, delay: float = 0.5):
    """Attempt to remove a file multiple times with delay between attempts."""
    for attempt in range(max_attempts):
        try:
            if file_path.exists():
                file_path.unlink()
            break
        except PermissionError:
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
            else:
                print(f"Warning: Could not remove temporary file {file_path}")

@app.post("/upload", )
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    Returns extracted sections including Abstract and main content sections.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        pdf_processor = PDFProcessor()
        extractor = PDFImageExtractor()
        images = extractor.extract_images(str(file_path))
        print("Extracted images:", images)
        extracted_text = pdf_processor.process_pdf(str(file_path))
        figures_context = extract_paragraphs_with_figures_from_sections(extracted_text)
        summaries = await get_summaries(extracted_text)
        asyncio.create_task(remove_file(file_path))
        
        return dict(
            message="File successfully processed",
            sections=extracted_text,
            figures_context=figures_context,
            images=images,
            summaries=summaries
        )
    
    except Exception as e:
        asyncio.create_task(remove_file(file_path))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)