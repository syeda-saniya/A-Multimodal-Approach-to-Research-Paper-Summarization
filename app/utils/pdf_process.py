import os
import re
import pdfplumber
import PyPDF2
from typing import Dict, List, Tuple
from contextlib import contextmanager

class PDFProcessor:
    @contextmanager
    def open_pdf(self, pdf_path):
        """Context manager to ensure PDF files are properly closed."""
        pdf = pdfplumber.open(pdf_path)
        try:
            yield pdf
        finally:
            pdf.close()

    def extract_text_from_columns(self, page) -> List[str]:
        """Extract text from columns in a page."""
        column_texts = []
        width = page.width
        height = page.height
        column_boundaries = [
            (0, 0, width / 2, height),
            (width / 2, 0, width, height)
        ]

        for boundary in column_boundaries:
            cropped_page = page.within_bbox(boundary)
            text = cropped_page.extract_text(layout=True)
            column_texts.append(text)

        return column_texts

    def extract_table(self, page) -> List[str]:
        """Extract tables from a page."""
        tables = page.extract_tables()
        table_strings = []
        for table in tables:
            table_string = ''
            for row in table:
                cleaned_row = [
                    item.replace('\n', ' ') if item is not None and '\n' in item 
                    else 'None' if item is None else item 
                    for item in row
                ]
                table_string += ('|' + '|'.join(cleaned_row) + '|' + '\n')
            table_strings.append(table_string.strip())
        return table_strings

    def extract_content_from_pdf(self, pdf_path: str) -> Dict[str, Dict]:
        """Extract text and tables from PDF file."""
        text_per_page = {}

        with self.open_pdf(pdf_path) as pdf:
            for pagenum, page in enumerate(pdf.pages):
                column_texts = self.extract_text_from_columns(page)
                tables = self.extract_table(page)
                page_text = "\n".join(column_texts)

                page_content = {
                    'text': page_text,
                    'tables': tables
                }
                text_per_page[f'Page_{pagenum}'] = page_content

        return text_per_page

    def delete_text_after_word(self, text: str, word: str) -> str:
        """Delete all text after a specific word."""
        index = text.find(word)
        if index != -1:
            text = text[:index]
        return text

    def delete_text_before_word(self, text: str, word: str) -> str:
        """Delete all text before a specific word."""
        index = text.find(word)
        if index != -1:
            text = text[index:]
        return text

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from text using Roman numeral headers."""
        heading_pattern = re.compile(r'\b([IVX]+)\.\s*([A-Za-z\s]+)\n')
        headings = list(heading_pattern.finditer(text))
        sections = {}

        for i in range(len(headings)):
            section_title = headings[i].group(2).strip()
            start_pos = headings[i].end()

            if i + 1 < len(headings):
                end_pos = headings[i + 1].start()
            else:
                end_pos = len(text)

            section_text = text[start_pos:end_pos].strip()
            sections[section_title] = section_text

        return sections

    def clean_section_titles(self, sections):
        cleaned_sections = {}
        for title, content in sections.items():
            # If any content accidentally attaches to the title, we clean it
            cleaned_title = title.split("\n")[0].strip()  # Keep only the first line of the title
            cleaned_sections[cleaned_title] = content

        return cleaned_sections

    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Process PDF file and extract structured content."""
        text_per_page = self.extract_content_from_pdf(pdf_path)
        
        pdf_text = ""
        for page_key in sorted(text_per_page.keys()):
            pdf_text += text_per_page[page_key]['text'] + "\n"

        modified_pdf_text = pdf_text
        for word in ["REFERENCES", "References"]:
            modified_pdf_text = self.delete_text_after_word(modified_pdf_text, word)
        
        modified_pdf_text = self.delete_text_before_word(modified_pdf_text, "Abstract")
        
        extracted_text_before_intro = modified_pdf_text.split("INTRODUCTION")[0].strip()
        
        complete_extracted_text = {"Abstract": extracted_text_before_intro}
        sections = self.extract_sections(modified_pdf_text)
        complete_extracted_text.update(sections)
        cleaned_sections = self.clean_section_titles(complete_extracted_text)
        
        
        return cleaned_sections