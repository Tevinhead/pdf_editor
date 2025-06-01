import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox, QHBoxLayout, QScrollArea
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from pdf_core import PDFCore
from ocr_integration import OCRIntegration

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.pdf_core = PDFCore()
        self.ocr_integration = OCRIntegration() # You might pass tesseract_cmd_path here

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Left Panel: Controls
        self.control_panel = QVBoxLayout()
        self.main_layout.addLayout(self.control_panel, 1) # 1/3 width

        self.open_button = QPushButton("Open PDF")
        self.open_button.clicked.connect(self.open_pdf_dialog)
        self.control_panel.addWidget(self.open_button)

        self.save_button = QPushButton("Save PDF")
        self.save_button.clicked.connect(self.save_pdf_dialog)
        self.control_panel.addWidget(self.save_button)

        self.save_as_button = QPushButton("Save PDF As...")
        self.save_as_button.clicked.connect(self.save_pdf_as_dialog)
        self.control_panel.addWidget(self.save_as_button)

        self.page_label = QLabel("Page: 0/0")
        self.control_panel.addWidget(self.page_label)

        self.prev_page_button = QPushButton("Previous Page")
        self.prev_page_button.clicked.connect(self.show_prev_page)
        self.control_panel.addWidget(self.prev_page_button)

        self.next_page_button = QPushButton("Next Page")
        self.next_page_button.clicked.connect(self.show_next_page)
        self.control_panel.addWidget(self.next_page_button)

        self.go_to_page_input = QLineEdit()
        self.go_to_page_input.setPlaceholderText("Go to page...")
        self.control_panel.addWidget(self.go_to_page_input)
        self.go_to_page_button = QPushButton("Go")
        self.go_to_page_button.clicked.connect(self.go_to_page)
        self.control_panel.addWidget(self.go_to_page_button)

        self.ocr_button = QPushButton("Perform OCR on Current Page")
        self.ocr_button.clicked.connect(self.perform_ocr_on_current_page)
        self.control_panel.addWidget(self.ocr_button)

        self.extract_pages_button = QPushButton("Extract Pages")
        self.extract_pages_button.clicked.connect(self.extract_pages_dialog)
        self.control_panel.addWidget(self.extract_pages_button)

        self.delete_pages_button = QPushButton("Delete Pages")
        self.delete_pages_button.clicked.connect(self.delete_pages_dialog)
        self.control_panel.addWidget(self.delete_pages_button)

        self.control_panel.addStretch() # Pushes everything to the top

        # Middle Panel: PDF Viewer
        self.pdf_viewer_layout = QVBoxLayout()
        self.main_layout.addLayout(self.pdf_viewer_layout, 3) # 2/3 width

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.pdf_image_label = QLabel("Open a PDF to view it here.")
        self.pdf_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.pdf_image_label)
        self.pdf_viewer_layout.addWidget(self.scroll_area)

        # Right Panel: OCR Output
        self.ocr_output_layout = QVBoxLayout()
        self.main_layout.addLayout(self.ocr_output_layout, 1) # 1/3 width

        self.ocr_output_label_title = QLabel("OCR Output:")
        self.ocr_output_layout.addWidget(self.ocr_output_label_title)
        self.ocr_output_text = QLabel("No OCR performed yet.")
        self.ocr_output_text.setWordWrap(True)
        self.ocr_output_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.ocr_output_scroll_area = QScrollArea()
        self.ocr_output_scroll_area.setWidgetResizable(True)
        self.ocr_output_scroll_area.setWidget(self.ocr_output_text)
        self.ocr_output_layout.addWidget(self.ocr_output_scroll_area)

        self.current_page_num = 0
        self.total_pages = 0

        self.update_ui_state()

    def update_ui_state(self):
        is_pdf_open = self.pdf_core.is_pdf_open()
        self.save_button.setEnabled(is_pdf_open)
        self.save_as_button.setEnabled(is_pdf_open)
        self.prev_page_button.setEnabled(is_pdf_open and self.current_page_num > 1)
        self.next_page_button.setEnabled(is_pdf_open and self.current_page_num < self.total_pages)
        self.go_to_page_input.setEnabled(is_pdf_open)
        self.go_to_page_button.setEnabled(is_pdf_open)
        self.ocr_button.setEnabled(is_pdf_open)
        self.extract_pages_button.setEnabled(is_pdf_open)
        self.delete_pages_button.setEnabled(is_pdf_open)

        if is_pdf_open:
            self.page_label.setText(f"Page: {self.current_page_num}/{self.total_pages}")
        else:
            self.page_label.setText("Page: 0/0")
            self.pdf_image_label.setText("Open a PDF to view it here.")
            self.ocr_output_text.setText("No OCR performed yet.")

    def open_pdf_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.open_pdf_with_password_prompt(file_path)

    def open_pdf_with_password_prompt(self, file_path):
        if self.pdf_core.open_pdf(file_path):
            self.total_pages = self.pdf_core.get_num_pages()
            self.current_page_num = 1 if self.total_pages > 0 else 0
            self.display_page(self.current_page_num)
            QMessageBox.information(self, "PDF Opened", "PDF opened successfully.")
        else:
            # If opening failed, it might be due to password. Prompt for password.
            password, ok = QLineEdit.getText(self, "Password Required", "Enter password for PDF:", QLineEdit.EchoMode.Password)
            if ok and password:
                if self.pdf_core.open_pdf(file_path, password=password):
                    self.total_pages = self.pdf_core.get_num_pages()
                    self.current_page_num = 1 if self.total_pages > 0 else 0
                    self.display_page(self.current_page_num)
                    QMessageBox.information(self, "PDF Opened", "PDF opened successfully with password.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to open PDF. Incorrect password or corrupted file.")
            else:
                QMessageBox.warning(self, "Error", "Failed to open PDF. Password not provided or cancelled.")
        self.update_ui_state()

    def display_page(self, page_num):
        if self.pdf_core.is_pdf_open() and page_num > 0 and page_num <= self.total_pages:
            img_bytes = self.pdf_core.render_page_to_image(page_num)
            if img_bytes:
                qimage = QImage.fromData(img_bytes)
                pixmap = QPixmap.fromImage(qimage)
                self.pdf_image_label.setPixmap(pixmap.scaledToWidth(self.scroll_area.width() - 20, Qt.TransformationMode.SmoothTransformation))
                self.current_page_num = page_num
            else:
                self.pdf_image_label.setText("Could not render page.")
        else:
            self.pdf_image_label.setText("No PDF page to display.")
        self.update_ui_state()

    def show_prev_page(self):
        if self.current_page_num > 1:
            self.display_page(self.current_page_num - 1)

    def show_next_page(self):
        if self.current_page_num < self.total_pages:
            self.display_page(self.current_page_num + 1)

    def go_to_page(self):
        try:
            page_num = int(self.go_to_page_input.text())
            if 1 <= page_num <= self.total_pages:
                self.display_page(page_num)
            else:
                QMessageBox.warning(self, "Invalid Page", f"Please enter a page number between 1 and {self.total_pages}.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the page.")
        self.go_to_page_input.clear()

    def save_pdf_dialog(self):
        if self.pdf_core.save_pdf():
            QMessageBox.information(self, "Save PDF", "PDF saved successfully.")
        else:
            QMessageBox.warning(self, "Save PDF", "Failed to save PDF.")

    def save_pdf_as_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if file_path:
            if self.pdf_core.save_pdf(file_path):
                QMessageBox.information(self, "Save PDF As", "PDF saved successfully to new file.")
            else:
                QMessageBox.warning(self, "Save PDF As", "Failed to save PDF to new file.")

    def perform_ocr_on_current_page(self):
        if self.pdf_core.is_pdf_open() and self.current_page_num > 0:
            pdf_path = self.pdf_core.file_path # OCRIntegration needs the file path
            if pdf_path:
                ocr_text = self.ocr_integration.perform_ocr_on_pdf_page(pdf_path, self.current_page_num)
                if ocr_text:
                    self.ocr_output_text.setText(ocr_text)
                    QMessageBox.information(self, "OCR Complete", "OCR performed successfully.")
                else:
                    self.ocr_output_text.setText("OCR failed or no text found.")
                    QMessageBox.warning(self, "OCR Failed", "Failed to perform OCR on the current page.")
            else:
                QMessageBox.warning(self, "OCR Error", "PDF file path not available for OCR.")
        else:
            QMessageBox.warning(self, "OCR Error", "No PDF open or no page selected for OCR.")

    def extract_pages_dialog(self):
        if not self.pdf_core.is_pdf_open():
            QMessageBox.warning(self, "Extract Pages", "No PDF document open.")
            return

        page_range_text, ok = QLineEdit.getText(self, "Extract Pages", "Enter page numbers or range (e.g., 1,3,5-7):")
        if ok and page_range_text:
            try:
                page_numbers = self.parse_page_range(page_range_text, self.total_pages)
                if not page_numbers:
                    QMessageBox.warning(self, "Invalid Input", "No valid page numbers found or out of bounds.")
                    return

                output_path, _ = QFileDialog.getSaveFileName(self, "Save Extracted Pages As", "", "PDF Files (*.pdf)")
                if output_path:
                    if self.pdf_core.extract_pages(page_numbers, output_path):
                        QMessageBox.information(self, "Extract Pages", "Pages extracted successfully.")
                    else:
                        QMessageBox.warning(self, "Extract Pages", "Failed to extract pages.")
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))
        
    def delete_pages_dialog(self):
        if not self.pdf_core.is_pdf_open():
            QMessageBox.warning(self, "Delete Pages", "No PDF document open.")
            return

        page_range_text, ok = QLineEdit.getText(self, "Delete Pages", "Enter page numbers or range to delete (e.g., 1,3,5-7):")
        if ok and page_range_text:
            try:
                page_numbers = self.parse_page_range(page_range_text, self.total_pages)
                if not page_numbers:
                    QMessageBox.warning(self, "Invalid Input", "No valid page numbers found or out of bounds.")
                    return

                reply = QMessageBox.question(self, "Confirm Deletion", 
                                             f"Are you sure you want to delete pages {page_range_text}?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if self.pdf_core.delete_pages(page_numbers):
                        QMessageBox.information(self, "Delete Pages", "Pages deleted successfully. Please save the PDF to apply changes.")
                        # After deletion, the current page might be invalid or total pages changed
                        self.total_pages = self.pdf_core.get_num_pages()
                        if self.current_page_num > self.total_pages:
                            self.current_page_num = self.total_pages if self.total_pages > 0 else 0
                        self.display_page(self.current_page_num)
                    else:
                        QMessageBox.warning(self, "Delete Pages", "Failed to delete pages.")
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))

    def parse_page_range(self, range_str, max_pages):
        pages = set()
        parts = range_str.replace(" ", "").split(',')
        for part in parts:
            if '-' in part:
                start_str, end_str = part.split('-')
                start = int(start_str)
                end = int(end_str)
                if not (1 <= start <= end <= max_pages):
                    raise ValueError(f"Range {part} is out of bounds (1-{max_pages}).")
                pages.update(range(start, end + 1))
            else:
                page_num = int(part)
                if not (1 <= page_num <= max_pages):
                    raise ValueError(f"Page {page_num} is out of bounds (1-{max_pages}).")
                pages.add(page_num)
        return sorted(list(pages))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())