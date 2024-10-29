# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from transformers import T5ForConditionalGeneration, T5Tokenizer
# from PIL import Image
# import torch
# import pytesseract
# import fitz  # PyMuPDF
# from typing import Dict
# import io

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize T5 model and tokenizer
# t5_model = T5ForConditionalGeneration.from_pretrained('t5-base')
# t5_tokenizer = T5Tokenizer.from_pretrained('t5-base')

# def extract_text_from_pdf(pdf_file: bytes) -> tuple[str, list]:
#     """Extract text and images from PDF file."""
#     doc = fitz.open(stream=pdf_file, filetype="pdf")
#     text = ""
#     images = []
    
#     for page in doc:
#         text += page.get_text()
#         # Extract images
#         img_list = page.get_images()
#         for img_index, img in enumerate(img_list):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             # Convert to PIL Image
#             image = Image.open(io.BytesIO(image_bytes))
#             images.append(image)
    
#     return text, images

# def get_llava_analysis(image: Image) -> str:
#     """Get image analysis from LLaVA (dummy implementation)."""
#     # In a real implementation, you would call the LLaVA API
#     return "This image shows a scientific diagram with experimental results."

# def generate_summary_with_t5(text: str) -> str:
#     """Generate summary using T5 model."""
#     inputs = t5_tokenizer.encode("summarize: " + text[:4096], 
#                                return_tensors="pt", 
#                                max_length=4096, 
#                                truncation=True)
    
#     summary_ids = t5_model.generate(inputs,
#                                   max_length=150,
#                                   min_length=40,
#                                   length_penalty=2.0,
#                                   num_beams=4)
    
#     summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
#     return summary

# @app.post("/analyze")
# async def analyze_file(file: UploadFile = File(...)) -> Dict:
#     try:
#         # Read file content
#         content = await file.read()
        
#         # Extract text and images from PDF
#         text, images = extract_text_from_pdf(content)
        
#         # Get image analysis from LLaVA
#         image_analyses = []
#         for image in images:
#             analysis = get_llava_analysis(image)
#             image_analyses.append(analysis)
        
#         # Combine text and image analyses
#         combined_text = text + " " + " ".join(image_analyses)
        
#         # Generate initial summary
#         initial_summary = generate_summary_with_t5(combined_text)
        
#         # Generate final refined summary
#         final_summary = generate_summary_with_t5(initial_summary)
        
#         return {
#             "summary": final_summary
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0000", port=8000)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Tuple

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_file: bytes) -> Tuple[str, List]:
    """Extract text and images from PDF file."""
    return ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", 
            [])

def get_llava_analysis(image) -> str:
    """Get image analysis from LLaVA (dummy implementation)."""
    return "This is a placeholder image analysis. The image appears to contain important scientific data."

def generate_summary_with_t5(text: str) -> str:
    """Generate summary using T5 model."""
    return "This is a placeholder T5 summary. The document discusses various scientific concepts and experimental results.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.", 

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)) -> Dict:
    try:
        content = await file.read()
        
        # Extract text and images from PDF
        text, images = extract_text_from_pdf(content)
        
        # Get image analysis
        image_analyses = []
        for _ in images:
            analysis = get_llava_analysis(None)
            image_analyses.append(analysis)
            
        # Generate summaries
        initial_summary = generate_summary_with_t5(text)
        final_summary = generate_summary_with_t5(initial_summary)
        
        return {
            "summary": final_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)