import fitz
import io
import re
import os
from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import base64

@dataclass
class FigureData:
    """Data class to store figure information"""
    path: str
    base64_data: str
    context: List[str]

class ImageExtractor:
    def __init__(self, output_dir: str = "extracted_figures"):
        """
        Initialize the PDF processor with an output directory for images.
        
        Args:
            output_dir (str): Directory where extracted images will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.figure_pattern = re.compile(r'\bFig\.\s*\d+\b', re.IGNORECASE)
        
    def process_pdf(self, pdf_path: str, sections: Dict[str, str]) -> Dict[str, FigureData]:
        """
        Process a PDF file to extract images and their corresponding context.
        
        Args:
            pdf_path (str): Path to the PDF file
            sections (Dict[str, str]): Dictionary of section names and their content
            
        Returns:
            Dict[str, FigureData]: Dictionary mapping figure references to their data
        """
        # Extract images and their paths
        image_paths = self._extract_images(pdf_path)
        
        # Extract context for figures from sections
        figures_context = self._extract_figures_context(sections)
        
        # Combine image paths with their context
        return self._combine_figures_data(image_paths, figures_context)
    
    def _extract_images(self, pdf_path: str) -> List[Tuple[str, str]]:
        """
        Extract images from PDF and save them to the output directory.
        Also return the base64 encoded image data.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            List[Tuple[str, str]]: List of (image_path, base64_image_data) tuples
        """
        doc = fitz.open(pdf_path)
        saved_images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Create filename with page and image index for better tracking
                image_filename = f"Fig_{page_num + 1}_{img_idx + 1}.{image_ext}"
                image_path = self.output_dir / image_filename
                
                # Save image using PIL
                image = Image.open(io.BytesIO(image_bytes))
                image.save(image_path)
                
                # Encode the image data to base64
                base64_image_data = base64.b64encode(image_bytes).decode('utf-8')
                
                saved_images.append((str(image_path), base64_image_data))
                print(f"Saved image as {image_path}")
        
        return saved_images
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    def _extract_figures_context(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Extract paragraphs containing figure references from sections.
        
        Args:
            sections (Dict[str, str]): Dictionary of section names and their content
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping figure references to their context
        """
        figures_dict = {}
        
        for section_name, content in sections.items():
            paragraphs = self._split_into_paragraphs(content)
            
            for para in paragraphs:
                matches = self.figure_pattern.findall(para)
                
                for fig in matches:
                    if fig not in figures_dict:
                        figures_dict[fig] = []
                    figures_dict[fig].extend([
                        f"Section: {section_name}",
                        para.strip(),
                        "-" * 50
                    ])
        
        return figures_dict
    
    def _combine_figures_data(
        self,
        image_data: List[Tuple[str, str]],
        figures_context: Dict[str, List[str]]
    ) -> Dict[str, FigureData]:
        """
        Combine image paths and base64 data with their corresponding context.
        
        Args:
            image_data (List[Tuple[str, str]]): List of (image_path, base64_image_data) tuples
            figures_context (Dict[str, List[str]]): Dictionary of figure contexts
            
        Returns:
            Dict[str, FigureData]: Combined figure data
        """
        combined_data = {}
        
        for idx, (path, base64_data) in enumerate(image_data):
            figure_ref = f"Fig. {idx + 1}"
            context = figures_context.get(figure_ref, ["No context found."])
            combined_data[figure_ref] = FigureData(path=path, base64_data=base64_data, context=context)
        
        return combined_data
    
    def prepare_for_llava(self, figure_data: Dict[str, FigureData]) -> List[Tuple[str, str, str, List[str]]]:
        """
        Prepare the extracted data for use with LLaVA model.
        
        Args:
            figure_data (Dict[str, FigureData]): Combined figure data
            
        Returns:
            List[Tuple[str, str, str, List[str]]]: List of (figure_ref, image_path, base64_image_data, context) tuples
        """
        llava_data = []
        
        for figure_ref, data in figure_data.items():
            llava_data.append((
                figure_ref,
                data.path,
                data.base64_data,
                data.context
            ))
        
        return llava_data
