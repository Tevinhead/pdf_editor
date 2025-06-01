import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF
import os
import platform

class OCRIntegration:
    def __init__(self, tesseract_cmd_path=None):
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
        else:
            # Try to find tesseract automatically
            self._auto_configure_tesseract()

    def _auto_configure_tesseract(self):
        """Try to automatically find Tesseract installation"""
        if platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.environ.get('USERNAME', ''))
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def perform_ocr_on_image(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error performing OCR on image: {e}")
            return None

    def perform_ocr_on_pdf_page(self, pdf_path, page_number, dpi=300):
        try:
            doc = fitz.open(pdf_path)
            if not (1 <= page_number <= len(doc)):
                print(f"Page {page_number} is out of bounds.")
                doc.close()
                return None
            
            page = doc.load_page(page_number - 1)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            img_bytes = pix.tobytes("png")
            doc.close()
            
            return self.perform_ocr_on_image(img_bytes)
        except Exception as e:
            print(f"Error performing OCR on PDF page: {e}")
            return None

    def create_searchable_pdf(self, input_pdf_path, output_pdf_path, tesseract_lang='eng'):
        """Create a searchable PDF with OCR text layer"""
        try:
            import ocrmypdf
            
            # Use ocrmypdf if available
            ocrmypdf.ocr(
                input_pdf_path,
                output_pdf_path,
                language=tesseract_lang,
                deskew=True,
                remove_background=True
            )
            return True
        except ImportError:
            print("ocrmypdf not installed. Install with: pip install ocrmypdf")
            return False
        except Exception as e:
            print(f"Error creating searchable PDF: {e}")
            return False