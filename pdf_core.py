import pikepdf
import fitz  # PyMuPDF
import io

class PDFCore:
    def __init__(self):
        self.pdf_document = None
        self.file_path = None

    def open_pdf(self, file_path, password=None):
        try:
            self.pdf_document = pikepdf.open(file_path, password=password)
            self.file_path = file_path
            return True
        except pikepdf.PasswordError:
            print("Incorrect password.")
            return False
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False

    def save_pdf(self, output_path=None):
        if not self.pdf_document:
            print("No PDF document open to save.")
            return False
        try:
            if output_path:
                self.pdf_document.save(output_path)
            else:
                self.pdf_document.save(self.file_path)
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False

    def close_pdf(self):
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
            self.file_path = None

    def extract_pages(self, page_numbers, output_path):
        if not self.pdf_document:
            print("No PDF document open.")
            return False
        try:
            new_pdf = pikepdf.new()
            for page_num in page_numbers:
                if 1 <= page_num <= len(self.pdf_document.pages):
                    new_pdf.pages.append(self.pdf_document.pages[page_num - 1])
                else:
                    print(f"Warning: Page {page_num} is out of bounds.")
            new_pdf.save(output_path)
            return True
        except Exception as e:
            print(f"Error extracting pages: {e}")
            return False

    def delete_pages(self, page_numbers):
        if not self.pdf_document:
            print("No PDF document open.")
            return False
        try:
            # Sort in descending order to avoid index issues after deletion
            sorted_page_numbers = sorted([p - 1 for p in page_numbers if 1 <= p <= len(self.pdf_document.pages)], reverse=True)
            for index in sorted_page_numbers:
                del self.pdf_document.pages[index]
            return True
        except Exception as e:
            print(f"Error deleting pages: {e}")
            return False

    def render_page_to_image(self, page_number, dpi=200):
        if not self.pdf_document:
            print("No PDF document open.")
            return None
        try:
            # PyMuPDF works with file paths or bytes, so we need to save to a buffer first
            # or open directly if self.file_path is available.
            # For simplicity, let's assume we can open with fitz directly from file_path
            if not self.file_path:
                print("Cannot render page: PDF not opened from a file path.")
                return None
            
            doc = fitz.open(self.file_path)
            if not (1 <= page_number <= len(doc)):
                print(f"Page {page_number} is out of bounds.")
                doc.close()
                return None
            
            page = doc.load_page(page_number - 1)  # PyMuPDF is 0-indexed
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            
            img_bytes = pix.tobytes("png")
            doc.close()
            return img_bytes
        except Exception as e:
            print(f"Error rendering page to image: {e}")
            return None

    def get_num_pages(self):
        if self.pdf_document:
            return len(self.pdf_document.pages)
        return 0

    def is_pdf_open(self):
        return self.pdf_document is not None