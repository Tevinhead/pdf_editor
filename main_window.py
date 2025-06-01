import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QFileDialog, QLabel, QLineEdit, 
                            QMessageBox, QHBoxLayout, QScrollArea, QTextEdit,
                            QSplitter, QMenu, QMenuBar, QStatusBar, QToolBar,
                            QSpinBox, QComboBox, QGroupBox)
from PyQt6.QtGui import QPixmap, QImage, QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
from pdf_core import PDFCore
from ocr_integration import OCRIntegration

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor Pro")
        self.setGeometry(100, 100, 1400, 900)

        self.pdf_core = PDFCore()
        self.ocr_integration = OCRIntegration()

        self.current_page_num = 0
        self.total_pages = 0
        self.zoom_level = 1.0

        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left Panel: Controls
        control_widget = QWidget()
        self.control_panel = QVBoxLayout(control_widget)
        self.splitter.addWidget(control_widget)

        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        self.open_button = QPushButton("Open PDF")
        self.open_button.clicked.connect(self.open_pdf_dialog)
        file_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Save PDF")
        self.save_button.clicked.connect(self.save_pdf_dialog)
        file_layout.addWidget(self.save_button)

        self.save_as_button = QPushButton("Save PDF As...")
        self.save_as_button.clicked.connect(self.save_pdf_as_dialog)
        file_layout.addWidget(self.save_as_button)

        file_group.setLayout(file_layout)
        self.control_panel.addWidget(file_group)

        # Navigation group
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout()

        self.page_label = QLabel("Page: 0/0")
        nav_layout.addWidget(self.page_label)

        nav_buttons = QHBoxLayout()
        self.prev_page_button = QPushButton("◀")
        self.prev_page_button.clicked.connect(self.show_prev_page)
        nav_buttons.addWidget(self.prev_page_button)

        self.page_spinner = QSpinBox()
        self.page_spinner.setMinimum(0)
        self.page_spinner.valueChanged.connect(self.go_to_page_spinner)
        nav_buttons.addWidget(self.page_spinner)

        self.next_page_button = QPushButton("▶")
        self.next_page_button.clicked.connect(self.show_next_page)
        nav_buttons.addWidget(self.next_page_button)

        nav_layout.addLayout(nav_buttons)

        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.zoom_changed)
        zoom_layout.addWidget(self.zoom_combo)

        nav_layout.addLayout(zoom_layout)
        nav_group.setLayout(nav_layout)
        self.control_panel.addWidget(nav_group)

        # Page operations group
        page_ops_group = QGroupBox("Page Operations")
        page_ops_layout = QVBoxLayout()

        self.extract_pages_button = QPushButton("Extract Pages")
        self.extract_pages_button.clicked.connect(self.extract_pages_dialog)
        page_ops_layout.addWidget(self.extract_pages_button)

        self.delete_pages_button = QPushButton("Delete Pages")
        self.delete_pages_button.clicked.connect(self.delete_pages_dialog)
        page_ops_layout.addWidget(self.delete_pages_button)

        page_ops_group.setLayout(page_ops_layout)
        self.control_panel.addWidget(page_ops_group)

        # OCR group
        ocr_group = QGroupBox("OCR Operations")
        ocr_layout = QVBoxLayout()

        self.ocr_button = QPushButton("Perform OCR on Current Page")
        self.ocr_button.clicked.connect(self.perform_ocr_on_current_page)
        ocr_layout.addWidget(self.ocr_button)

        self.ocr_all_button = QPushButton("Create Searchable PDF")
        self.ocr_all_button.clicked.connect(self.create_searchable_pdf)
        ocr_layout.addWidget(self.ocr_all_button)

        ocr_group.setLayout(ocr_layout)
        self.control_panel.addWidget(ocr_group)

        self.control_panel.addStretch()

        # Middle Panel: PDF Viewer
        viewer_widget = QWidget()
        self.pdf_viewer_layout = QVBoxLayout(viewer_widget)
        self.splitter.addWidget(viewer_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.pdf_image_label = QLabel("Open a PDF to view it here.")
        self.pdf_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_image_label.setStyleSheet("QLabel { background-color: #f0f0f0; }")
        self.scroll_area.setWidget(self.pdf_image_label)
        self.pdf_viewer_layout.addWidget(self.scroll_area)

        # Right Panel: OCR Output
        ocr_widget = QWidget()
        self.ocr_output_layout = QVBoxLayout(ocr_widget)
        self.splitter.addWidget(ocr_widget)

        self.ocr_output_label_title = QLabel("OCR Output:")
        self.ocr_output_layout.addWidget(self.ocr_output_label_title)

        self.ocr_output_text = QTextEdit()
        self.ocr_output_text.setReadOnly(True)
        self.ocr_output_text.setPlaceholderText("No OCR performed yet.")
        self.ocr_output_layout.addWidget(self.ocr_output_text)

        # Set initial splitter sizes
        self.splitter.setSizes([300, 700, 400])

        self.update_ui_state()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open PDF", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_pdf_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_pdf_dialog)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_pdf_as_dialog)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("Reset Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        toolbar.addAction("Open", self.open_pdf_dialog)
        toolbar.addAction("Save", self.save_pdf_dialog)
        toolbar.addSeparator()
        toolbar.addAction("Previous", self.show_prev_page)
        toolbar.addAction("Next", self.show_next_page)
        toolbar.addSeparator()
        toolbar.addAction("OCR", self.perform_ocr_on_current_page)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def update_ui_state(self):
        is_pdf_open = self.pdf_core.is_pdf_open()
        self.save_button.setEnabled(is_pdf_open)
        self.save_as_button.setEnabled(is_pdf_open)
        self.prev_page_button.setEnabled(is_pdf_open and self.current_page_num > 1)
        self.next_page_button.setEnabled(is_pdf_open and self.current_page_num < self.total_pages)
        self.page_spinner.setEnabled(is_pdf_open)
        self.ocr_button.setEnabled(is_pdf_open)
        self.ocr_all_button.setEnabled(is_pdf_open)
        self.extract_pages_button.setEnabled(is_pdf_open)
        self.delete_pages_button.setEnabled(is_pdf_open)
        self.zoom_combo.setEnabled(is_pdf_open)

        if is_pdf_open:
            self.page_label.setText(f"Page: {self.current_page_num}/{self.total_pages}")
            self.page_spinner.setMaximum(self.total_pages)
            self.page_spinner.setValue(self.current_page_num)
            self.status_bar.showMessage(f"PDF loaded: {self.total_pages} pages")
        else:
            self.page_label.setText("Page: 0/0")
            self.pdf_image_label.setText("Open a PDF to view it here.")
            self.ocr_output_text.clear()
            self.page_spinner.setMaximum(0)
            self.status_bar.showMessage("Ready")

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
            password, ok = self.get_password_dialog()
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

    def get_password_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        password, ok = QInputDialog.getText(self, "Password Required", 
                                          "Enter password for PDF:", 
                                          QLineEdit.EchoMode.Password)
        return password, ok

    def display_page(self, page_num):
        if self.pdf_core.is_pdf_open() and page_num > 0 and page_num <= self.total_pages:
            # Calculate DPI based on zoom level
            dpi = int(200 * self.zoom_level)
            img_bytes = self.pdf_core.render_page_to_image(page_num, dpi=dpi)
            if img_bytes:
                qimage = QImage.fromData(img_bytes)
                pixmap = QPixmap.fromImage(qimage)
                self.pdf_image_label.setPixmap(pixmap)
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

    def go_to_page_spinner(self, value):
        if value > 0 and value <= self.total_pages:
            self.display_page(value)

    def zoom_changed(self, text):
        try:
            self.zoom_level = int(text.replace("%", "")) / 100.0
            self.display_page(self.current_page_num)
        except:
            pass

    def zoom_in(self):
        current_index = self.zoom_combo.currentIndex()
        if current_index < self.zoom_combo.count() - 1:
            self.zoom_combo.setCurrentIndex(current_index + 1)

    def zoom_out(self):
        current_index = self.zoom_combo.currentIndex()
        if current_index > 0:
            self.zoom_combo.setCurrentIndex(current_index - 1)

    def zoom_reset(self):
        self.zoom_combo.setCurrentText("100%")

    def save_pdf_dialog(self):
        if self.pdf_core.save_pdf():
            QMessageBox.information(self, "Save PDF", "PDF saved successfully.")
            self.status_bar.showMessage("PDF saved", 3000)
        else:
            QMessageBox.warning(self, "Save PDF", "Failed to save PDF.")

    def save_pdf_as_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if file_path:
            if self.pdf_core.save_pdf(file_path):
                QMessageBox.information(self, "Save PDF As", "PDF saved successfully to new file.")
                self.status_bar.showMessage(f"PDF saved as: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "Save PDF As", "Failed to save PDF to new file.")

    def perform_ocr_on_current_page(self):
        if self.pdf_core.is_pdf_open() and self.current_page_num > 0:
            self.status_bar.showMessage("Performing OCR...")
            QApplication.processEvents()  # Update UI
            
            pdf_path = self.pdf_core.file_path
            if pdf_path:
                ocr_text = self.ocr_integration.perform_ocr_on_pdf_page(pdf_path, self.current_page_num)
                if ocr_text:
                    self.ocr_output_text.setPlainText(ocr_text)
                    QMessageBox.information(self, "OCR Complete", "OCR performed successfully.")
                    self.status_bar.showMessage("OCR completed", 3000)
                else:
                    self.ocr_output_text.setPlainText("OCR failed or no text found.")
                    QMessageBox.warning(self, "OCR Failed", "Failed to perform OCR on the current page.")
                    self.status_bar.showMessage("OCR failed", 3000)
            else:
                QMessageBox.warning(self, "OCR Error", "PDF file path not available for OCR.")
        else:
            QMessageBox.warning(self, "OCR Error", "No PDF open or no page selected for OCR.")

    def create_searchable_pdf(self):
        if not self.pdf_core.is_pdf_open():
            QMessageBox.warning(self, "Create Searchable PDF", "No PDF document open.")
            return

        output_path, _ = QFileDialog.getSaveFileName(self, "Save Searchable PDF As", "", "PDF Files (*.pdf)")
        if output_path:
            self.status_bar.showMessage("Creating searchable PDF...")
            QApplication.processEvents()
            
            if self.ocr_integration.create_searchable_pdf(self.pdf_core.file_path, output_path):
                QMessageBox.information(self, "Success", "Searchable PDF created successfully.")
                self.status_bar.showMessage("Searchable PDF created", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to create searchable PDF. Make sure ocrmypdf is installed.")
                self.status_bar.showMessage("Failed to create searchable PDF", 3000)

    def extract_pages_dialog(self):
        if not self.pdf_core.is_pdf_open():
            QMessageBox.warning(self, "Extract Pages", "No PDF document open.")
            return

        from PyQt6.QtWidgets import QInputDialog
        page_range_text, ok = QInputDialog.getText(self, "Extract Pages", 
                                                  "Enter page numbers or range (e.g., 1,3,5-7):")
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
                        self.status_bar.showMessage("Pages deleted - save to apply changes", 3000)
                        # After deletion, update the display
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

    def closeEvent(self, event):
        """Handle application close event"""
        if self.pdf_core.is_pdf_open():
            reply = QMessageBox.question(self, "Exit", 
                                       "Do you want to save changes before closing?",
                                       QMessageBox.StandardButton.Save | 
                                       QMessageBox.StandardButton.Discard | 
                                       QMessageBox.StandardButton.Cancel)
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_pdf_dialog()
                self.pdf_core.close_pdf()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                self.pdf_core.close_pdf()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()