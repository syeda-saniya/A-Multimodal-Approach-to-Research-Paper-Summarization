import fitz  # PyMuPDF
import io
from PIL import Image

class PDFImageExtractor:
    def __init__(self):
        self.extracted_images = []  # List to store paths of extracted images

    def extract_images(self, pdf_file_path):
        """
        Opens the PDF file and extracts images from each page, saving them with figure numbering.
        
        Args:
            pdf_file_path (str): The file path of the PDF to process.
        
        Returns:
            list: A list of file paths of the saved images.
        """
        doc = fitz.open(pdf_file_path)
        figure_counter = 1  # Counter for figure numbering

        # Iterate through each page in the document
        for page_number in range(len(doc)):
            page = doc[page_number]
            image_list = page.get_images(full=True)
            print(f"[+] Found {len(image_list)} images on page {page_number + 1}")

            # Process each image in the page
            for image_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image = Image.open(io.BytesIO(image_bytes))
                
                # Save image locally with an incremented figure number
                image_save_path = f"Fig_{figure_counter}.{image_ext}"
                with open(image_save_path, "wb") as image_file:
                    image.save(image_file)
                print(f"Saved image as {image_save_path}")

                # Add the saved image path to the list of extracted images
                self.extracted_images.append(image_save_path)
                figure_counter += 1  # Increment figure counter for unique naming

        return self.extracted_images

# Example usage:
# extractor = PDFImageExtractor()
# images = extractor.extract_images("path/to/your/pdf_file.pdf")
# print("Extracted images:", images)
