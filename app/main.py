import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.utils.pdf_process import PDFProcessor
from app.utils.image_extraction import ImageExtractor
import shutil
from pathlib import Path
import asyncio
import httpx
from typing import Dict

UPLOAD_DIR = Path("uploads")
FIGURE_DIR = Path("extracted_figures")  # Add directory for figures
UPLOAD_DIR.mkdir(exist_ok=True)
FIGURE_DIR.mkdir(exist_ok=True)  # Create figures directory

app = FastAPI(
    title="PDF Extractor API",
    description="API for extracting and processing text from PDF files",
    version="1.0.0"
)

NGROK_URL = "https://66cb-34-75-189-225.ngrok-free.app/summarize"

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
async def get_summaries(payload: Dict) -> Dict[str, str]:
    """Get summaries for sections and images from ngrok service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                NGROK_URL,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            result = response.json()
            
            if result['status'] == 'success':
                return result
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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    Returns extracted sections including Abstract and main content sections.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = UPLOAD_DIR / file.filename
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize processors
        pdf_processor = PDFProcessor()
        image_extractor = ImageExtractor(output_dir=str(FIGURE_DIR))
        
        # Extract text content
        extracted_text = pdf_processor.process_pdf(str(file_path))
        
        # Process images and get their context
        figure_data = image_extractor.process_pdf(str(file_path), extracted_text)
        # figures_context = image_extractor._extract_figures_context(extracted_text)
        llava_data = image_extractor.prepare_for_llava(figure_data)
        
        payload = {
            "sections": extracted_text,
            "image_data": llava_data
        }
        
        print(payload)
        
        # Send the combined payload to /summarize endpoint
        summaries = await get_summaries(payload)
        
        
        # Schedule file cleanup
        asyncio.create_task(remove_file(file_path))
        
        return {
            "message": "File successfully processed",
            "section_summaries": summaries.get("section_summaries", {}),
            "image_summaries": summaries.get("image_summaries", {}),
            "final_summary": summaries.get("final_summary", {})
        }
    
    except Exception as e:
        # Ensure cleanup on error
        asyncio.create_task(remove_file(file_path))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up any extracted images that are no longer needed
        for image_file in FIGURE_DIR.glob("*.{jpg,jpeg,png}"):
            asyncio.create_task(remove_file(image_file))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)