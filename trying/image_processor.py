import os
import fitz
import io
from PIL import Image
from typing import Dict, List
from contextlib import contextmanager
from base_processor import BaseProcessor

class PDFImageProcessor(BaseProcessor):
    """Handles extraction and organization of images from PDFs."""
    
    def _setup_directories(self):
        """Create directory structure for image processing."""
        self.image_base_dir = os.path.join(self.output_base_dir, "images")
        self._create_directory(self.image_base_dir)
    
    def _create_pdf_specific_dirs(self, pdf_name: str) -> str:
        """Create directories for a specific PDF's images."""
        timestamp = self._get_timestamp()
        pdf_dir = os.path.join(self.image_base_dir, f"{pdf_name}_{timestamp}")
        self._create_directory(pdf_dir)
        return pdf_dir
    
    @contextmanager
    def _open_pdf(self, pdf_path: str):
        """Context manager for PyMuPDF operations."""
        doc = fitz.open(pdf_path)
        try:
            yield doc
        finally:
            doc.close()
    
    def extract_images(self, pdf_path: str) -> Dict[str, List[str]]:
        """Extract and save images from PDF."""
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = self._create_pdf_specific_dirs(pdf_name)
        image_info = {"pdf_name": pdf_name, "images": []}
        
        with self._open_pdf(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        image_filename = f"page_{page_num}_fig_{img_idx+1}.{image_ext}"
                        image_path = os.path.join(output_dir, image_filename)
                        
                        image = Image.open(io.BytesIO(image_bytes))
                        image.save(image_path)
                        
                        image_info["images"].append({
                            "filename": image_filename,
                            "path": image_path,
                            "page": page_num,
                            "figure_number": img_idx + 1
                        })
                        
                        self.logger.info(f"Saved image: {image_filename}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing image on page {page_num}: {str(e)}")
        
        metadata_path = os.path.join(output_dir, "image_metadata.json")
        self._save_json(image_info, metadata_path)
        
        return image_info