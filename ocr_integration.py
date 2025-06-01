import pytesseract
from PIL import Image
import io
import fitz # PyMuPDF
# import pikepdf # Not directly used in this simplified OCR module

class OCRIntegration:
    def __init__(self, tesseract_cmd_path=None):
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path

    def perform_ocr_on_image(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
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
        try:
            # This function is intended for creating searchable PDFs.
            # It's a more complex feature that requires careful handling of PDF structure
            # and text embedding. For now, this function will be a placeholder.
            # The actual implementation would involve using PyMuPDF to create a new PDF
            # and embed the OCR'd text as an invisible layer.
            
            # Example (conceptual) of how it might work with PyMuPDF:
            # doc_in = fitz.open(input_pdf_path)
            # doc_out = fitz.open() # New PDF
            # for page_num in range(len(doc_in)):
            #     page_in = doc_in.load_page(page_num)
            #     pix = page_in.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
            #     img_bytes = pix.tobytes("png")
            #     text = pytesseract.image_to_string(Image.open(io.BytesIO(img_bytes)), lang=tesseract_lang)
            #
            #     page_out = doc_out.new_page(width=page_in.rect.width, height=page_in.rect.height)
            #     # Insert original page content (e.g., as an image)
            #     # Then insert text with render_mode=3 (invisible)
            #     # page_out.insert_text((x, y), text, render_mode=3)
            # doc_out.save(output_pdf_path)
            # doc_in.close()
            # doc_out.close()
            
            print("Searchable PDF creation is not yet implemented.")
            return False
        except Exception as e:
            print(f"Error creating searchable PDF: {e}")
            return False