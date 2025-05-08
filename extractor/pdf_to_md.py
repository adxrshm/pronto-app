import os
import pymupdf4llm
import fitz # PyMuPDF
from pathlib import Path
from typing import List, Optional, Dict, Union

class PDFToMarkdownConverter:
    """A class to handle batch conversion of PDF files to Markdown format with page exclusions."""
    
    def __init__(self, pdf_folder: str = "pdf", output_folder: str = "output_md", page_exclusions: Dict[str, Dict[str, str]] = None):
        """
        Initialize the converter with input and output folder paths.
        
        Args:
            pdf_folder (str): Path to folder containing PDF files
            output_folder (str): Path to folder where Markdown files will be saved
            page_exclusions (Dict[str, Dict[str, str]]): Dictionary containing file names and their pages to ignore
                                                        Format: {"filename": {"pages_to_ignore": "0-10"}}
        """
        self.pdf_folder = Path(pdf_folder)
        self.output_folder = Path(output_folder)
        self.page_exclusions = page_exclusions or {}
        self.conversion_stats = {
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def parse_page_range(self, range_str: str) -> List[int]:
        """
        Parse a page range string into a list of page numbers to ignore.
        
        Args:
            range_str (str): String representing page ranges (e.g., "0-10,15,20-25")
            
        Returns:
            List[int]: List of page numbers to ignore
        """
        pages_to_ignore = set()
        for part in range_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages_to_ignore.update(range(start, end + 1))
            else:
                pages_to_ignore.add(int(part))
        return sorted(list(pages_to_ignore))
    
    def get_pages_to_include(self, pdf_path: Path, pages_to_ignore: List[int]) -> List[int]:
        """
        Get list of pages to include based on total pages and ignore list.
        
        Args:
            pdf_path (Path): Path to the PDF file
            pages_to_ignore (List[int]): List of pages to ignore
            
        Returns:
            List[int]: List of pages to include
        """
        try:
            # Get total number of pages
            doc = fitz.open(str(pdf_path))
            total_pages = doc.page_count
            doc.close()
            
            # Create list of all pages except those in ignore list
            return [i for i in range(total_pages) if i not in pages_to_ignore]
        except Exception as e:
            print(f"Error getting page count for {pdf_path.name}: {str(e)}")
            return []
    
    def setup_folders(self) -> None:
        """Create output folder if it doesn't exist and verify input folder."""
        if not self.pdf_folder.exists():
            raise FileNotFoundError(f"PDF folder not found: {self.pdf_folder}")
        
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def get_pdf_files(self) -> List[Path]:
        """
        Get list of all PDF files in the input folder.
        
        Returns:
            List[Path]: List of paths to PDF files
        """
        return list(self.pdf_folder.glob('*.pdf'))
    
    def convert_single_pdf(self, pdf_path: Path) -> Optional[str]:
        """
        Convert a single PDF file to Markdown, excluding specified pages.
        
        Args:
            pdf_path (Path): Path to the PDF file
        
        Returns:
            Optional[str]: Markdown text if successful, None if failed
        """
        try:
            # Get pages to ignore and convert to pages to include
            pages_to_ignore = []
            file_config = self.page_exclusions.get(pdf_path.stem)
            if file_config and 'pages_to_ignore' in file_config:
                pages_to_ignore = self.parse_page_range(file_config['pages_to_ignore'])
                print(f"Excluding pages {pages_to_ignore} from {pdf_path.name}")
            
            # Get list of pages to include
            pages_to_include = self.get_pages_to_include(pdf_path, pages_to_ignore)
            
            if not pages_to_include:
                raise ValueError("No pages to convert after applying exclusions")
            
            # Convert to markdown with page selection
            return pymupdf4llm.to_markdown(
                str(pdf_path),
                pages=pages_to_include
            )
        except Exception as e:
            print(f"Error converting {pdf_path.name}: {str(e)}")
            return None
    
    def save_markdown(self, md_text: str, output_path: Path) -> bool:
        """
        Save Markdown text to file.
        
        Args:
            md_text (str): Markdown content to save
            output_path (Path): Path where to save the file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            output_path.write_bytes(md_text.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error saving {output_path.name}: {str(e)}")
            return False
    
    def convert_all_pdfs(self, skip_existing: bool = True) -> dict:
        """
        Convert all PDFs in the input folder to Markdown.
        
        Args:
            skip_existing (bool): Skip files that already exist in output folder
        
        Returns:
            dict: Statistics about the conversion process
        """
        self.setup_folders()
        pdf_files = self.get_pdf_files()
        
        for pdf_path in pdf_files:
            md_filename = pdf_path.stem + '.md'
            output_path = self.output_folder / md_filename
            
            if skip_existing and output_path.exists():
                print(f"Skipping existing file: {md_filename}")
                self.conversion_stats['skipped'] += 1
                continue
            
            print(f"Converting {pdf_path.name} to Markdown...")
            md_text = self.convert_single_pdf(pdf_path)
            
            if md_text is not None:
                if self.save_markdown(md_text, output_path):
                    print(f"Successfully converted {pdf_path.name} to {md_filename}")
                    self.conversion_stats['successful'] += 1
                else:
                    self.conversion_stats['failed'] += 1
            else:
                self.conversion_stats['failed'] += 1
        
        return self.conversion_stats

    def get_conversion_summary(self) -> str:
        """
        Get a summary of the conversion process.
        
        Returns:
            str: Summary of conversion statistics
        """
        return (f"Conversion Summary:\n"
                f"  Successful: {self.conversion_stats['successful']}\n"
                f"  Failed: {self.conversion_stats['failed']}\n"
                f"  Skipped: {self.conversion_stats['skipped']}")


if __name__ == "__main__":
    # Example page exclusions configuration
    page_exclusions = {
        "JAPANESE CANDLESTICK CHARTING TECHNIQUES": {
            "pages_to_ignore": "0-13"
        },
        "The Definitive Guide to Point and Figures": {
            "pages_to_ignore": "0-22"
        },
         "The New Trading for a Living": {
            "pages_to_ignore": "0-15"
        },
         "Encyclopedia Of Chart Patterns": {
            "pages_to_ignore": "0-22"
        },
    }
    
    # Create converter instance with page exclusions
    converter = PDFToMarkdownConverter(
        pdf_folder="pdf",
        output_folder="output_pdf",
        page_exclusions=page_exclusions
    )
    
    # Convert all PDFs and get statistics
    stats = converter.convert_all_pdfs(skip_existing=True)
    
    # Print summary
    print("\n" + converter.get_conversion_summary())