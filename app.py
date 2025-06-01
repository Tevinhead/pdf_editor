import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()_bar.showMessage("Pages extracted", 3000)
                    else:
                        QMessageBox.warning(self, "Extract Pages", "Failed to extract pages.")
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))
        
    def delete_pages_dialog(self):
        if not self.pdf_core.is_pdf_open():
            QMessageBox.warning(self, "Delete Pages", "No PDF document open.")
            return

        from PyQt6.QtWidgets import QInputDialog
        page_range_text, ok = QInputDialog.getText(self, "Delete Pages", 
                                                  "Enter page numbers or range to delete (e.g., 1,3,5-7):")
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
                        self.status